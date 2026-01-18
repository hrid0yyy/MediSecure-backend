"""
Doctors API Router
Routes: /api/doctors/*

Full CRUD operations for doctor management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

from config.database import get_db
from models import User, UserRole, Doctor, SPECIALIZATIONS
from utils.security import get_current_user, get_current_admin

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])


# ============ SCHEMAS ============

class AvailableHours(BaseModel):
    start: str = "09:00"
    end: str = "17:00"


class DoctorBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialization: str
    license_number: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    consultation_fee: Optional[float] = 0.0
    available_days: Optional[List[str]] = []
    available_hours: Optional[AvailableHours] = None


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    consultation_fee: Optional[float] = None
    available_days: Optional[List[str]] = None
    available_hours: Optional[AvailableHours] = None
    is_available: Optional[bool] = None


class DoctorResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    specialization: str
    license_number: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    consultation_fee: float = 0.0
    available_days: List[str] = []
    available_hours: Optional[dict] = None
    is_available: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DoctorsListResponse(BaseModel):
    doctors: List[DoctorResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# ============ HELPER FUNCTIONS ============

def doctor_to_response(doctor: Doctor) -> dict:
    """Convert Doctor model to response format"""
    return {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "name": doctor.name,
        "email": doctor.email,
        "phone": doctor.phone,
        "specialization": doctor.specialization,
        "license_number": doctor.license_number,
        "department": doctor.department,
        "bio": doctor.bio,
        "avatar_url": doctor.avatar_url,
        "consultation_fee": doctor.consultation_fee or 0.0,
        "available_days": doctor.available_days or [],
        "available_hours": doctor.available_hours or {"start": "09:00", "end": "17:00"},
        "is_available": doctor.is_available,
        "created_at": doctor.created_at.isoformat() if doctor.created_at else None
    }


# ============ ENDPOINTS ============

@router.get("", response_model=DoctorsListResponse)
@router.get("/", response_model=DoctorsListResponse)
async def get_doctors(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    specialization: Optional[str] = None,
    available: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all doctors (paginated).
    
    GET /api/doctors?page=1&limit=10&specialization=Cardiology&available=true
    """
    query = db.query(Doctor).filter(Doctor.is_active == True)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Doctor.name.ilike(f"%{search}%"),
                Doctor.specialization.ilike(f"%{search}%"),
                Doctor.department.ilike(f"%{search}%")
            )
        )
    
    if specialization:
        query = query.filter(Doctor.specialization == specialization)
    
    if available is not None:
        query = query.filter(Doctor.is_available == available)
    
    # Count total
    total = query.count()
    
    # Paginate
    skip = (page - 1) * limit
    doctors = query.order_by(Doctor.name).offset(skip).limit(limit).all()
    
    return {
        "doctors": [doctor_to_response(d) for d in doctors],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/available", response_model=DoctorsListResponse)
async def get_available_doctors(
    date: Optional[str] = None,
    time: Optional[str] = None,
    specialization: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get only available doctors.
    
    GET /api/doctors/available?date=2025-01-20&time=10:00&specialization=Cardiology
    """
    query = db.query(Doctor).filter(
        Doctor.is_active == True,
        Doctor.is_available == True
    )
    
    if specialization:
        query = query.filter(Doctor.specialization == specialization)
    
    # TODO: Add date/time availability checking based on available_days and available_hours
    
    total = query.count()
    skip = (page - 1) * limit
    doctors = query.order_by(Doctor.name).offset(skip).limit(limit).all()
    
    return {
        "doctors": [doctor_to_response(d) for d in doctors],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/specializations")
async def get_specializations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all specializations.
    
    GET /api/doctors/specializations
    """
    # Get active specializations from database
    active_specs = db.query(Doctor.specialization).filter(
        Doctor.is_active == True,
        Doctor.specialization.isnot(None)
    ).distinct().all()
    
    active_list = [spec for (spec,) in active_specs if spec]
    
    # Combine with predefined list
    all_specs = list(set(active_list + SPECIALIZATIONS))
    all_specs.sort()
    
    return {"specializations": all_specs}


@router.get("/{doctor_id}")
async def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific doctor by ID.
    
    GET /api/doctors/{doctor_id}
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return doctor_to_response(doctor)


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Create a new doctor record.
    
    POST /api/doctors
    """
    # Check if license number already exists
    if doctor_data.license_number:
        existing = db.query(Doctor).filter(
            Doctor.license_number == doctor_data.license_number
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="License number already registered")
    
    new_doctor = Doctor(
        name=doctor_data.name,
        email=doctor_data.email,
        phone=doctor_data.phone,
        specialization=doctor_data.specialization,
        license_number=doctor_data.license_number,
        department=doctor_data.department or doctor_data.specialization,
        bio=doctor_data.bio,
        consultation_fee=doctor_data.consultation_fee or 0.0,
        available_days=doctor_data.available_days or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        available_hours=doctor_data.available_hours.model_dump() if doctor_data.available_hours else {"start": "09:00", "end": "17:00"},
        is_available=True,
        is_active=True
    )
    
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    
    return doctor_to_response(new_doctor)


@router.put("/{doctor_id}")
async def update_doctor(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a doctor record.
    
    PUT /api/doctors/{doctor_id}
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check permissions - only admin or the doctor themselves can update
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        if doctor.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this doctor")
    
    update_data = doctor_data.model_dump(exclude_unset=True)
    
    # Handle available_hours conversion
    if "available_hours" in update_data and update_data["available_hours"]:
        if hasattr(update_data["available_hours"], "model_dump"):
            update_data["available_hours"] = update_data["available_hours"].model_dump()
    
    for field, value in update_data.items():
        if hasattr(doctor, field):
            setattr(doctor, field, value)
    
    doctor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(doctor)
    
    return doctor_to_response(doctor)


@router.delete("/{doctor_id}")
async def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Soft delete a doctor record.
    
    DELETE /api/doctors/{doctor_id}
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Soft delete
    doctor.is_active = False
    doctor.is_available = False
    doctor.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Doctor deleted successfully"}


@router.patch("/{doctor_id}/availability")
async def update_availability(
    doctor_id: int,
    is_available: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle doctor availability.
    
    PATCH /api/doctors/{doctor_id}/availability
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        if doctor.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    doctor.is_available = is_available
    doctor.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "id": doctor.id,
        "is_available": doctor.is_available,
        "message": f"Availability updated to {'available' if is_available else 'unavailable'}"
    }
