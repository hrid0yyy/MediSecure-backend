from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from models.appointment import Appointment, AppointmentStatus
from schemas.appointment import AppointmentCreate, AppointmentUpdate
from models.user import User, UserRole


class AppointmentService:
    """Business logic for appointment management"""

    @staticmethod
    def create_appointment(
        db: Session,
        patient_id: int,
        appointment_data: AppointmentCreate
    ) -> Appointment:
        """Create a new appointment with conflict checking"""
        
        # Verify doctor exists and has doctor role
        doctor = db.query(User).filter(User.id == appointment_data.doctor_id).first()
        if not doctor or doctor.role != UserRole.DOCTOR:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid doctor ID"
            )
        
        # Check for scheduling conflicts
        end_time = appointment_data.appointment_date + timedelta(minutes=appointment_data.duration_minutes)
        conflicts = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == appointment_data.doctor_id,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
                or_(
                    and_(
                        Appointment.appointment_date <= appointment_data.appointment_date,
                        Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) > appointment_data.appointment_date
                    ),
                    and_(
                        Appointment.appointment_date < end_time,
                        Appointment.appointment_date >= appointment_data.appointment_date
                    )
                )
            )
        ).first()
        
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Doctor is not available at this time"
            )
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            **appointment_data.model_dump()
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        return appointment

    @staticmethod
    def get_patient_appointments(
        db: Session,
        patient_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[AppointmentStatus] = None
    ) -> tuple[List[Appointment], int]:
        """Get all appointments for a patient"""
        query = db.query(Appointment).filter(Appointment.patient_id == patient_id)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        total = query.count()
        appointments = query.order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit).all()
        
        return appointments, total

    @staticmethod
    def get_doctor_appointments(
        db: Session,
        doctor_id: int,
        skip: int = 0,
        limit: int = 20,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> tuple[List[Appointment], int]:
        """Get all appointments for a doctor"""
        query = db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
        
        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)
        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)
        
        total = query.count()
        appointments = query.order_by(Appointment.appointment_date).offset(skip).limit(limit).all()
        
        return appointments, total

    @staticmethod
    def update_appointment(
        db: Session,
        appointment_id: int,
        user_id: int,
        update_data: AppointmentUpdate
    ) -> Appointment:
        """Update an appointment"""
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Verify user has permission to update
        if appointment.patient_id != user_id and appointment.doctor_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this appointment"
            )
        
        # Update fields
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(appointment, field, value)
        
        appointment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(appointment)
        
        return appointment

    @staticmethod
    def cancel_appointment(
        db: Session,
        appointment_id: int,
        user_id: int,
        cancellation_reason: str
    ) -> Appointment:
        """Cancel an appointment"""
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Verify user has permission to cancel
        if appointment.patient_id != user_id and appointment.doctor_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this appointment"
            )
        
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = cancellation_reason
        appointment.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(appointment)
        
        return appointment

    @staticmethod
    def get_appointment_by_id(db: Session, appointment_id: int, user_id: int) -> Appointment:
        """Get a specific appointment"""
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Verify user has permission to view
        if appointment.patient_id != user_id and appointment.doctor_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this appointment"
            )
        
        return appointment
