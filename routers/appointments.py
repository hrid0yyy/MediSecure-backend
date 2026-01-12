from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from config.database import get_db
from schemas.appointment import (
    AppointmentCreate, AppointmentUpdate, AppointmentCancel,
    AppointmentResponse, AppointmentListResponse
)
from services.appointment_service import AppointmentService
from utils.security import get_current_user
from models.user import User
from models.appointment import AppointmentStatus

router = APIRouter(prefix="/api/v1/appointments", tags=["Appointments"])


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new appointment"""
    appointment = AppointmentService.create_appointment(
        db=db,
        patient_id=current_user.id,
        appointment_data=appointment_data
    )
    return appointment


@router.get("/my-appointments", response_model=AppointmentListResponse)
def get_my_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[AppointmentStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's appointments"""
    appointments, total = AppointmentService.get_patient_appointments(
        db=db,
        patient_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    return AppointmentListResponse(
        appointments=appointments,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/doctor/{doctor_id}", response_model=AppointmentListResponse)
def get_doctor_appointments(
    doctor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get appointments for a specific doctor"""
    appointments, total = AppointmentService.get_doctor_appointments(
        db=db,
        doctor_id=doctor_id,
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to
    )
    return AppointmentListResponse(
        appointments=appointments,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific appointment"""
    appointment = AppointmentService.get_appointment_by_id(
        db=db,
        appointment_id=appointment_id,
        user_id=current_user.id
    )
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an appointment"""
    appointment = AppointmentService.update_appointment(
        db=db,
        appointment_id=appointment_id,
        user_id=current_user.id,
        update_data=update_data
    )
    return appointment


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    cancel_data: AppointmentCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an appointment"""
    appointment = AppointmentService.cancel_appointment(
        db=db,
        appointment_id=appointment_id,
        user_id=current_user.id,
        cancellation_reason=cancel_data.cancellation_reason
    )
    return appointment
