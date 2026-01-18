"""
Patients API Router
Routes: /api/patients/*

Full CRUD operations for patient management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

from config.database import get_db
from models import User, UserRole, Patient
from utils.security import get_current_user, get_current_staff_or_above

router = APIRouter(prefix="/api/patients", tags=["Patients"])


# ============ SCHEMAS ============

class PatientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None  # ISO date string
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[List[str]] = []


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[List[str]] = None


class PatientResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[List[str]] = []
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatientsListResponse(BaseModel):
    patients: List[PatientResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# ============ HELPER FUNCTIONS ============

def patient_to_response(patient: Patient) -> dict:
    """Convert Patient model to response format"""
    return {
        "id": patient.id,
        "user_id": patient.user_id,
        "name": patient.name,
        "email": patient.email,
        "phone": patient.phone,
        "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
        "gender": patient.gender,
        "blood_type": patient.blood_type,
        "address": patient.address,
        "emergency_contact": patient.emergency_contact_phone,
        "medical_history": patient.medical_history,
        "allergies": patient.allergies or [],
        "status": patient.status or "active",
        "created_at": patient.created_at.isoformat() if patient.created_at else None,
        "updated_at": patient.updated_at.isoformat() if patient.updated_at else None
    }


# ============ ENDPOINTS ============

@router.get("", response_model=PatientsListResponse)
@router.get("/", response_model=PatientsListResponse)
async def get_patients(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all patients (paginated).
    
    GET /api/patients?page=1&limit=10&search=john&status=active
    """
    # Check permissions - Admin, Staff, Doctor can view all patients
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.STAFF, UserRole.DOCTOR]:
        raise HTTPException(status_code=403, detail="Not authorized to view patients")
    
    query = db.query(Patient)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Patient.name.ilike(f"%{search}%"),
                Patient.email.ilike(f"%{search}%"),
                Patient.phone.ilike(f"%{search}%")
            )
        )
    
    if status:
        query = query.filter(Patient.status == status)
    else:
        query = query.filter(Patient.is_active == True)
    
    # Count total
    total = query.count()
    
    # Paginate
    skip = (page - 1) * limit
    patients = query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "patients": [patient_to_response(p) for p in patients],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/my-patients", response_model=PatientsListResponse)
async def get_my_patients(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get patients assigned to the current doctor.
    
    GET /api/patients/my-patients
    """
    from models import Doctor, Appointment
    
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
    
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        return {
            "patients": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "total_pages": 0
        }
    
    # Get unique patient IDs from appointments
    from sqlalchemy import distinct
    patient_ids_query = db.query(distinct(Appointment.patient_id)).filter(
        Appointment.doctor_id == doctor.id
    )
    patient_ids = [pid for (pid,) in patient_ids_query.all()]
    
    query = db.query(Patient).filter(Patient.id.in_(patient_ids))
    
    if search:
        query = query.filter(
            or_(
                Patient.name.ilike(f"%{search}%"),
                Patient.email.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    skip = (page - 1) * limit
    patients = query.offset(skip).limit(limit).all()
    
    return {
        "patients": [patient_to_response(p) for p in patients],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/{patient_id}")
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific patient by ID.
    
    GET /api/patients/{patient_id}
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Check permissions
    if current_user.role == UserRole.PATIENT:
        # Patients can only view their own record
        if patient.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this patient")
    
    return patient_to_response(patient)


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_above)
):
    """
    Create a new patient record.
    
    POST /api/patients
    """
    from datetime import date
    
    # Parse date if provided
    dob = None
    if patient_data.date_of_birth:
        try:
            dob = date.fromisoformat(patient_data.date_of_birth)
        except ValueError:
            pass
    
    new_patient = Patient(
        name=patient_data.name,
        email=patient_data.email,
        phone=patient_data.phone,
        date_of_birth=dob,
        gender=patient_data.gender,
        blood_type=patient_data.blood_type,
        address=patient_data.address,
        emergency_contact_name=patient_data.emergency_contact_name,
        emergency_contact_phone=patient_data.emergency_contact_phone,
        medical_history=patient_data.medical_history,
        allergies=patient_data.allergies or [],
        status="active",
        is_active=True
    )
    
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    return patient_to_response(new_patient)


@router.put("/{patient_id}")
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a patient record.
    
    PUT /api/patients/{patient_id}
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Check permissions
    if current_user.role == UserRole.PATIENT:
        if patient.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this patient")
        # Patients can only update limited fields
        allowed_fields = ["phone", "address", "emergency_contact_name", "emergency_contact_phone"]
        update_data = patient_data.model_dump(exclude_unset=True)
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    else:
        update_data = patient_data.model_dump(exclude_unset=True)
    
    # Handle date conversion
    if "date_of_birth" in update_data and update_data["date_of_birth"]:
        from datetime import date
        try:
            update_data["date_of_birth"] = date.fromisoformat(update_data["date_of_birth"])
        except ValueError:
            del update_data["date_of_birth"]
    
    for field, value in update_data.items():
        if hasattr(patient, field):
            setattr(patient, field, value)
    
    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)
    
    return patient_to_response(patient)


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a patient record.
    
    DELETE /api/patients/{patient_id}
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Only admins can delete patients")
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Soft delete
    patient.is_active = False
    patient.status = "inactive"
    patient.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Patient deleted successfully"}
