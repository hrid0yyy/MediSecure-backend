from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from models.prescription import Prescription, PrescriptionMedication, PrescriptionStatus
from models.user import User, UserRole
from schemas.prescription import PrescriptionCreate
import secrets


class PrescriptionService:
    """Business logic for prescription management"""

    @staticmethod
    def _generate_prescription_number() -> str:
        """Generate unique prescription number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(4).upper()
        return f"RX-{timestamp}-{random_part}"

    @staticmethod
    def create_prescription(
        db: Session,
        doctor_id: int,
        prescription_data: PrescriptionCreate
    ) -> Prescription:
        """Create a new prescription with medications"""
        
        # Verify doctor has doctor role
        doctor = db.query(User).filter(User.id == doctor_id).first()
        if not doctor or doctor.role != UserRole.DOCTOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only doctors can create prescriptions"
            )
        
        # Verify patient exists
        patient = db.query(User).filter(User.id == prescription_data.patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Create prescription
        prescription = Prescription(
            patient_id=prescription_data.patient_id,
            doctor_id=doctor_id,
            appointment_id=prescription_data.appointment_id,
            prescription_number=PrescriptionService._generate_prescription_number(),
            diagnosis=prescription_data.diagnosis,
            notes=prescription_data.notes,
            expiry_date=datetime.utcnow() + timedelta(days=365)
        )
        db.add(prescription)
        db.flush()
        
        # Add medications
        for med_data in prescription_data.medications:
            medication = PrescriptionMedication(
                prescription_id=prescription.id,
                **med_data.model_dump(),
                refills_remaining=med_data.refills_allowed
            )
            db.add(medication)
        
        db.commit()
        db.refresh(prescription)
        
        return prescription

    @staticmethod
    def get_patient_prescriptions(
        db: Session,
        patient_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[PrescriptionStatus] = None
    ) -> tuple[List[Prescription], int]:
        """Get all prescriptions for a patient"""
        query = db.query(Prescription).filter(Prescription.patient_id == patient_id)
        
        if status:
            query = query.filter(Prescription.status == status)
        
        total = query.count()
        prescriptions = query.order_by(Prescription.issued_date.desc()).offset(skip).limit(limit).all()
        
        return prescriptions, total

    @staticmethod
    def get_prescription_by_id(
        db: Session,
        prescription_id: int,
        user_id: int,
        user_role: UserRole
    ) -> Prescription:
        """Get a specific prescription"""
        prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
        
        if not prescription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prescription not found"
            )
        
        # Verify user has permission to view
        if user_role not in [UserRole.ADMIN, UserRole.DOCTOR]:
            if prescription.patient_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this prescription"
                )
        
        return prescription

    @staticmethod
    def cancel_prescription(
        db: Session,
        prescription_id: int,
        doctor_id: int
    ) -> Prescription:
        """Cancel a prescription"""
        prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
        
        if not prescription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prescription not found"
            )
        
        # Only the prescribing doctor can cancel
        if prescription.doctor_id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the prescribing doctor can cancel this prescription"
            )
        
        prescription.status = PrescriptionStatus.CANCELLED
        prescription.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(prescription)
        
        return prescription

    @staticmethod
    def request_refill(
        db: Session,
        medication_id: int,
        patient_id: int
    ) -> PrescriptionMedication:
        """Request a medication refill"""
        medication = db.query(PrescriptionMedication).filter(
            PrescriptionMedication.id == medication_id
        ).first()
        
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
        
        # Verify prescription belongs to patient
        prescription = db.query(Prescription).filter(Prescription.id == medication.prescription_id).first()
        if prescription.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        # Check refills available
        if medication.refills_remaining <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refills remaining. Please contact your doctor."
            )
        
        medication.refills_remaining -= 1
        db.commit()
        db.refresh(medication)
        
        return medication
