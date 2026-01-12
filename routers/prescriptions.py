from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from config.database import get_db
from schemas.prescription import PrescriptionCreate, PrescriptionResponse, PrescriptionDetailResponse
from services.prescription_service import PrescriptionService
from utils.security import get_current_user
from models.user import User, UserRole
from models.prescription import PrescriptionStatus

router = APIRouter(prefix="/api/v1/prescriptions", tags=["Prescriptions"])


@router.post("/", response_model=PrescriptionDetailResponse, status_code=status.HTTP_201_CREATED)
def create_prescription(
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new prescription (Doctors only)"""
    prescription = PrescriptionService.create_prescription(
        db=db,
        doctor_id=current_user.id,
        prescription_data=prescription_data
    )
    return prescription


@router.get("/my-prescriptions")
def get_my_prescriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[PrescriptionStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's prescriptions"""
    prescriptions, total = PrescriptionService.get_patient_prescriptions(
        db=db,
        patient_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    return {
        "prescriptions": prescriptions,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/{prescription_id}", response_model=PrescriptionDetailResponse)
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific prescription"""
    prescription = PrescriptionService.get_prescription_by_id(
        db=db,
        prescription_id=prescription_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    return prescription


@router.post("/{prescription_id}/cancel", response_model=PrescriptionResponse)
def cancel_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a prescription (Doctor who prescribed only)"""
    prescription = PrescriptionService.cancel_prescription(
        db=db,
        prescription_id=prescription_id,
        doctor_id=current_user.id
    )
    return prescription


@router.post("/medications/{medication_id}/refill")
def request_refill(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request a medication refill"""
    medication = PrescriptionService.request_refill(
        db=db,
        medication_id=medication_id,
        patient_id=current_user.id
    )
    return {
        "message": "Refill processed successfully",
        "refills_remaining": medication.refills_remaining
    }
