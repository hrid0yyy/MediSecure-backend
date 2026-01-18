"""
Dashboard API Router
Routes: /api/dashboard/*

Provides role-based dashboard statistics and analytics.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional

from config.database import get_db
from models import User, UserRole, Patient, Doctor, Appointment, AppointmentStatus, Invoice, Prescription
from utils.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics based on user role.
    
    GET /api/dashboard/stats
    """
    today = datetime.utcnow().date()
    
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.STAFF]:
        # Admin/Staff dashboard
        total_patients = db.query(Patient).filter(Patient.is_active == True).count()
        total_doctors = db.query(Doctor).filter(Doctor.is_active == True).count()
        total_appointments = db.query(Appointment).count()
        pending_appointments = db.query(Appointment).filter(
            Appointment.status == AppointmentStatus.SCHEDULED
        ).count()
        todays_appointments = db.query(Appointment).filter(
            func.date(Appointment.appointment_date) == today
        ).count()
        completed_appointments = db.query(Appointment).filter(
            Appointment.status == AppointmentStatus.COMPLETED
        ).count()
        
        # Revenue calculation
        try:
            total_revenue = db.query(func.sum(Invoice.total_amount)).filter(
                Invoice.status == "paid"
            ).scalar() or 0.0
        except:
            total_revenue = 0.0
        
        # Recent patients
        recent_patients = db.query(Patient).order_by(
            Patient.created_at.desc()
        ).limit(5).all()
        
        return {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "total_appointments": total_appointments,
            "pending_appointments": pending_appointments,
            "todays_appointments": todays_appointments,
            "completed_appointments": completed_appointments,
            "total_revenue": float(total_revenue),
            "recent_patients": [
                {
                    "id": p.id,
                    "name": p.name,
                    "email": p.email,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in recent_patients
            ]
        }
    
    elif current_user.role == UserRole.DOCTOR:
        # Doctor dashboard - doctor_id in appointments references users table (user.id)
        # So we use current_user.id directly
        
        # Count unique patients from appointments
        my_patients = db.query(func.count(func.distinct(Appointment.patient_id))).filter(
            Appointment.doctor_id == current_user.id
        ).scalar() or 0
        
        todays_appointments = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == current_user.id,
                func.date(Appointment.appointment_date) == today
            )
        ).count()
        
        pending_appointments = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == current_user.id,
                Appointment.status == AppointmentStatus.SCHEDULED
            )
        ).count()
        
        completed_appointments = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == current_user.id,
                Appointment.status == AppointmentStatus.COMPLETED
            )
        ).count()
        
        # Upcoming appointments
        upcoming = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == current_user.id,
                Appointment.appointment_date >= datetime.utcnow(),
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
            )
        ).order_by(Appointment.appointment_date).limit(5).all()
        
        return {
            "my_patients": my_patients,
            "todays_appointments": todays_appointments,
            "pending_appointments": pending_appointments,
            "completed_appointments": completed_appointments,
            "upcoming_appointments": [
                {
                    "id": a.id,
                    "patient_name": a.patient.name if a.patient else "Unknown",
                    "scheduled_time": a.appointment_date.isoformat() if a.appointment_date else None,
                    "type": "consultation"
                }
                for a in upcoming
            ]
        }
    
    else:  # Patient
        # patient_id in appointments references users table (user.id)
        # So we use current_user.id directly
        
        upcoming_appointments = db.query(Appointment).filter(
            and_(
                Appointment.patient_id == current_user.id,
                Appointment.appointment_date >= datetime.utcnow(),
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
            )
        ).count()
        
        completed_appointments = db.query(Appointment).filter(
            and_(
                Appointment.patient_id == current_user.id,
                Appointment.status == AppointmentStatus.COMPLETED
            )
        ).count()
        
        # Count prescriptions for this user
        try:
            active_prescriptions = db.query(Prescription).filter(
                and_(
                    Prescription.patient_id == current_user.id,
                    Prescription.status == "ACTIVE"
                )
            ).count()
        except:
            active_prescriptions = 0
        
        # Count pending invoices
        try:
            pending_bills = db.query(Invoice).filter(
                and_(
                    Invoice.patient_id == current_user.id,
                    Invoice.status == "PENDING"
                )
            ).count()
        except:
            pending_bills = 0
        
        # Next appointment
        next_apt = db.query(Appointment).filter(
            and_(
                Appointment.patient_id == current_user.id,
                Appointment.appointment_date >= datetime.utcnow(),
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
            )
        ).order_by(Appointment.appointment_date).first()
        
        return {
            "upcoming_appointments": upcoming_appointments,
            "completed_appointments": completed_appointments,
            "active_prescriptions": active_prescriptions,
            "pending_bills": pending_bills,
            "next_appointment": {
                "id": next_apt.id,
                "doctor_name": next_apt.doctor.name if next_apt.doctor else "Unknown",
                "scheduled_time": next_apt.appointment_date.isoformat(),
                "type": "consultation"
            } if next_apt else None
        }


@router.get("/appointment-trends")
async def get_appointment_trends(
    period: str = Query("week", pattern="^(week|month|year)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get appointment trend data for charts.
    
    GET /api/dashboard/appointment-trends?period=week
    """
    today = datetime.utcnow().date()
    
    if period == "week":
        # Last 7 days
        labels = []
        completed = []
        scheduled = []
        cancelled = []
        
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime("%a"))
            
            day_completed = db.query(Appointment).filter(
                and_(
                    func.date(Appointment.appointment_date) == day,
                    Appointment.status == AppointmentStatus.COMPLETED
                )
            ).count()
            completed.append(day_completed)
            
            day_scheduled = db.query(Appointment).filter(
                and_(
                    func.date(Appointment.appointment_date) == day,
                    Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
                )
            ).count()
            scheduled.append(day_scheduled)
            
            day_cancelled = db.query(Appointment).filter(
                and_(
                    func.date(Appointment.appointment_date) == day,
                    Appointment.status == AppointmentStatus.CANCELLED
                )
            ).count()
            cancelled.append(day_cancelled)
        
        return {
            "labels": labels,
            "completed": completed,
            "scheduled": scheduled,
            "cancelled": cancelled
        }
    
    elif period == "month":
        # Last 4 weeks
        labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
        completed = []
        scheduled = []
        cancelled = []
        
        for i in range(4):
            week_start = today - timedelta(days=today.weekday() + (7 * (3 - i)))
            week_end = week_start + timedelta(days=6)
            
            week_completed = db.query(Appointment).filter(
                and_(
                    func.date(Appointment.appointment_date) >= week_start,
                    func.date(Appointment.appointment_date) <= week_end,
                    Appointment.status == AppointmentStatus.COMPLETED
                )
            ).count()
            completed.append(week_completed)
            
            week_scheduled = db.query(Appointment).filter(
                and_(
                    func.date(Appointment.appointment_date) >= week_start,
                    func.date(Appointment.appointment_date) <= week_end,
                    Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
                )
            ).count()
            scheduled.append(week_scheduled)
            
            week_cancelled = db.query(Appointment).filter(
                and_(
                    func.date(Appointment.appointment_date) >= week_start,
                    func.date(Appointment.appointment_date) <= week_end,
                    Appointment.status == AppointmentStatus.CANCELLED
                )
            ).count()
            cancelled.append(week_cancelled)
        
        return {
            "labels": labels,
            "completed": completed,
            "scheduled": scheduled,
            "cancelled": cancelled
        }
    
    else:  # year
        # Last 12 months
        labels = []
        completed = []
        scheduled = []
        cancelled = []
        
        for i in range(11, -1, -1):
            month_date = today.replace(day=1) - timedelta(days=i * 30)
            labels.append(month_date.strftime("%b"))
            
            # Simplified
            month_start = month_date.replace(day=1)
            try:
                if month_date.month == 12:
                    month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
                
                month_completed = db.query(Appointment).filter(
                    and_(
                        func.date(Appointment.appointment_date) >= month_start,
                        func.date(Appointment.appointment_date) <= month_end,
                        Appointment.status == AppointmentStatus.COMPLETED
                    )
                ).count()
            except:
                month_completed = 0
            
            completed.append(month_completed)
            scheduled.append(0)
            cancelled.append(0)
        
        return {
            "labels": labels,
            "completed": completed,
            "scheduled": scheduled,
            "cancelled": cancelled
        }


@router.get("/department-stats")
async def get_department_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics by department.
    
    GET /api/dashboard/department-stats
    """
    departments = []
    
    specializations = db.query(Doctor.specialization).distinct().all()
    
    for (spec,) in specializations:
        if not spec:
            continue
            
        doctors_count = db.query(Doctor).filter(
            Doctor.specialization == spec,
            Doctor.is_active == True
        ).count()
        
        # Get user_ids for doctors in this specialization
        doctor_user_ids = [d.user_id for d in db.query(Doctor).filter(Doctor.specialization == spec).all() if d.user_id]
        
        if doctor_user_ids:
            appointments_count = db.query(Appointment).filter(
                Appointment.doctor_id.in_(doctor_user_ids)
            ).count()
            
            patients_count = db.query(func.count(func.distinct(Appointment.patient_id))).filter(
                Appointment.doctor_id.in_(doctor_user_ids)
            ).scalar() or 0
        else:
            appointments_count = 0
            patients_count = 0
        
        departments.append({
            "name": spec,
            "patients": patients_count,
            "appointments": appointments_count,
            "doctors": doctors_count
        })
    
    return {"departments": departments}


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent system activity.
    
    GET /api/dashboard/recent-activity?limit=10
    """
    activities = []
    
    # Recent appointments
    recent_appointments = db.query(Appointment).order_by(
        Appointment.created_at.desc()
    ).limit(limit // 2).all()
    
    for apt in recent_appointments:
        activities.append({
            "id": apt.id,
            "type": "appointment_created",
            "description": f"Appointment scheduled with {apt.doctor.name if apt.doctor else 'Unknown'}",
            "user_name": apt.patient.name if apt.patient else "Unknown",
            "timestamp": apt.created_at.isoformat() if apt.created_at else None
        })
    
    # Recent patient registrations
    recent_patients = db.query(Patient).order_by(
        Patient.created_at.desc()
    ).limit(limit // 2).all()
    
    for patient in recent_patients:
        activities.append({
            "id": patient.id,
            "type": "patient_registered",
            "description": "New patient registered",
            "user_name": patient.name,
            "timestamp": patient.created_at.isoformat() if patient.created_at else None
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    
    return {"activities": activities[:limit]}
