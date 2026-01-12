from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from models.medical_record import RecordType


class MedicalRecordCreate(BaseModel):
    patient_id: int
    record_type: RecordType
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    encrypted_data: Optional[str] = None
    diagnosis_code: Optional[str] = Field(None, max_length=50)
    recorded_date: datetime

    class Config:
        from_attributes = True


class MedicalRecordUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    encrypted_data: Optional[str] = None
    diagnosis_code: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    record_type: RecordType
    title: str
    description: str
    diagnosis_code: Optional[str]
    is_active: bool
    recorded_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicalRecordListResponse(BaseModel):
    records: list[MedicalRecordResponse]
    total: int
    page: int
    page_size: int

    class Config:
        from_attributes = True
