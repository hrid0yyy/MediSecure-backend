"""
Appointments API Router (v2)
Routes: /api/appointments/*

Full CRUD operations for appointments with role-based access.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from config.database import get_db
from models import User, UserRole, Appointment, AppointmentStatus, Patient, Doctor
from utils.security import get_current_user

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


# ============ SCHEMAS ============

class AppointmentCreate(BaseModel):
    patient_id: Optional[int] = None  # Optional if patient is creating for themselves
    doctor_id: int
    scheduled_time: str  # ISO datetime string
    type: str = "consultation"
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    scheduled_time: Optional[str] = None
    type: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: str  # scheduled, confirmed, completed, cancelled


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: Optional[str] = None
    doctor_id: int
    doctor_name: Optional[str] = None
    scheduled_time: str
    end_time: Optional[str] = None
    type: str
    status: str
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class AppointmentsListResponse(BaseModel):
    appointments: List[AppointmentResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# ============ HELPER FUNCTIONS ============

def appointment_to_response(apt: Appointment, db: Session) -> dict:
    """Convert Appointment model to response format"""
    patient = db.query(Patient).filter(Patient.id == apt.patient_id).first() if apt.patient_id else None
    doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first() if apt.doctor_id else None
    
    return {
        "id": apt.id,
        "patient_id": apt.patient_id,
        "patient_name": patient.name if patient else None,
        "doctor_id": apt.doctor_id,
        "doctor_name": doctor.name if doctor else None,
        "scheduled_time": apt.scheduled_time.isoformat() if apt.scheduled_time else None,
        "end_time": apt.end_time.isoformat() if hasattr(apt, 'end_time') and apt.end_time else None,
        "type": apt.appointment_type if hasattr(apt, 'appointment_type') else "consultation",
        "status": apt.status.value if apt.status else "scheduled",
        "notes": apt.notes if hasattr(apt, 'notes') else None,
        "cancellation_reason": apt.cancellation_reason if hasattr(apt, 'cancellation_reason') else None,
        "created_at": apt.created_at.isoformat() if apt.created_at else None,
        "updated_at": apt.updated_at.isoformat() if hasattr(apt, 'updated_at') and apt.updated_at else None
    }


# ============ ENDPOINTS ============

@router.get("", response_model=AppointmentsListResponse)
@router.get("/", response_model=AppointmentsListResponse)
async def get_appointments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    date: Optional[str] = None,
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get appointments with filters (role-based).
    
    GET /api/appointments?page=1&limit=10&status=scheduled
    """
    query = db.query(Appointment)
    
    # Role-based filtering
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(Appointment.patient_id == patient.id)
        else:
            return {"appointments": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}
    
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor:
            query = query.filter(Appointment.doctor_id == doctor.id)
        else:
            return {"appointments": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}
    
    # Apply filters
    if status:
        try:
            status_enum = AppointmentStatus(status)
            query = query.filter(Appointment.status == status_enum)
        except ValueError:
            pass
    
    if date:
        from sqlalchemy import func
        try:
            filter_date = datetime.fromisoformat(date).date()
            query = query.filter(func.date(Appointment.scheduled_time) == filter_date)
        except ValueError:
            pass
    
    if doctor_id and current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.STAFF]:
        query = query.filter(Appointment.doctor_id == doctor_id)
    
    if patient_id and current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.STAFF, UserRole.DOCTOR]:
        query = query.filter(Appointment.patient_id == patient_id)
    
    total = query.count()
    skip = (page - 1) * limit
    appointments = query.order_by(Appointment.scheduled_time.desc()).offset(skip).limit(limit).all()
    
    return {
        "appointments": [appointment_to_response(a, db) for a in appointments],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/my-appointments", response_model=AppointmentsListResponse)
async def get_my_appointments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get appointments for current user (patient or doctor).
    
    GET /api/appointments/my-appointments
    """
    query = db.query(Appointment)
    
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient:
            return {"appointments": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}
        query = query.filter(Appointment.patient_id == patient.id)
    
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor:
            return {"appointments": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}
        query = query.filter(Appointment.doctor_id == doctor.id)
    
    if status:
        try:
            status_enum = AppointmentStatus(status)
            query = query.filter(Appointment.status == status_enum)
        except ValueError:
            pass
    
    total = query.count()
    skip = (page - 1) * limit
    appointments = query.order_by(Appointment.scheduled_time.desc()).offset(skip).limit(limit).all()
    
    return {
        "appointments": [appointment_to_response(a, db) for a in appointments],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/{appointment_id}")
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific appointment.
    
    GET /api/appointments/{appointment_id}
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check access permissions
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or appointment.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    return appointment_to_response(appointment, db)


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new appointment.
    
    POST /api/appointments
    """
    # Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    if not doctor.is_available:
        raise HTTPException(status_code=400, detail="Doctor is not available")
    
    # Determine patient_id
    patient_id = data.patient_id
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient:
            raise HTTPException(status_code=400, detail="Patient profile not found")
        patient_id = patient.id
    elif not patient_id:
        raise HTTPException(status_code=400, detail="patient_id is required")
    
    # Parse scheduled time
    try:
        scheduled_time = datetime.fromisoformat(data.scheduled_time.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scheduled_time format")
    
    new_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=data.doctor_id,
        scheduled_time=scheduled_time,
        status=AppointmentStatus.SCHEDULED,
        created_at=datetime.utcnow()
    )
    
    if hasattr(new_appointment, 'appointment_type'):
        new_appointment.appointment_type = data.type
    if hasattr(new_appointment, 'notes'):
        new_appointment.notes = data.notes
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    return appointment_to_response(new_appointment, db)


@router.put("/{appointment_id}")
async def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an appointment.
    
    PUT /api/appointments/{appointment_id}
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check permissions
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        # Patients can only update limited fields
        if data.status:
            raise HTTPException(status_code=403, detail="Patients cannot change status directly")
    
    update_data = data.model_dump(exclude_unset=True)
    
    if "scheduled_time" in update_data and update_data["scheduled_time"]:
        try:
            update_data["scheduled_time"] = datetime.fromisoformat(
                update_data["scheduled_time"].replace('Z', '+00:00')
            )
        except ValueError:
            del update_data["scheduled_time"]
    
    if "status" in update_data:
        try:
            update_data["status"] = AppointmentStatus(update_data["status"])
        except ValueError:
            del update_data["status"]
    
    for field, value in update_data.items():
        if field == "type" and hasattr(appointment, 'appointment_type'):
            appointment.appointment_type = value
        elif hasattr(appointment, field):
            setattr(appointment, field, value)
    
    if hasattr(appointment, 'updated_at'):
        appointment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(appointment)
    
    return appointment_to_response(appointment, db)


@router.patch("/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update appointment status.
    
    PATCH /api/appointments/{appointment_id}/status
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.STAFF, UserRole.DOCTOR]:
        raise HTTPException(status_code=403, detail="Not authorized to change status")
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    try:
        new_status = AppointmentStatus(data.status)
        appointment.status = new_status
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    if hasattr(appointment, 'updated_at'):
        appointment.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "id": appointment.id,
        "status": appointment.status.value,
        "message": f"Appointment {data.status} successfully"
    }


@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an appointment.
    
    DELETE /api/appointments/{appointment_id}
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check permissions
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    appointment.status = AppointmentStatus.CANCELLED
    if hasattr(appointment, 'updated_at'):
        appointment.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}
