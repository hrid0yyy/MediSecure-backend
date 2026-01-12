from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from models.prescription import PrescriptionStatus


class MedicationCreate(BaseModel):
    medication_name: str = Field(..., min_length=2, max_length=255)
    dosage: str = Field(..., min_length=2, max_length=100)
    frequency: str = Field(..., min_length=2, max_length=100)
    duration_days: int = Field(..., gt=0, le=365)
    quantity: int = Field(..., gt=0)
    instructions: Optional[str] = None
    refills_allowed: int = Field(default=0, ge=0, le=12)

    class Config:
        from_attributes = True


class PrescriptionCreate(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    diagnosis: str = Field(..., min_length=10, max_length=2000)
    medications: list[MedicationCreate]
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class PrescriptionResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    prescription_number: str
    status: PrescriptionStatus
    diagnosis: str
    notes: Optional[str]
    issued_date: datetime
    expiry_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class MedicationResponse(BaseModel):
    id: int
    medication_name: str
    dosage: str
    frequency: str
    duration_days: int
    quantity: int
    instructions: Optional[str]
    refills_allowed: int
    refills_remaining: int

    class Config:
        from_attributes = True


class PrescriptionDetailResponse(PrescriptionResponse):
    medications: list[MedicationResponse]

    class Config:
        from_attributes = True
