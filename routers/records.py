"""
Medical Records API Router
Routes: /api/records/*

Full CRUD operations for medical records management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from config.database import get_db
from models import User, UserRole, MedicalRecord, Patient, Doctor
from utils.security import get_current_user, get_current_admin

router = APIRouter(prefix="/api/records", tags=["Medical Records"])


# ============ SCHEMAS ============

class VitalSigns(BaseModel):
    blood_pressure: Optional[str] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    oxygen_saturation: Optional[int] = None


class RecordAttachment(BaseModel):
    id: int
    filename: str
    url: str
    uploaded_at: Optional[str] = None


class RecordCreate(BaseModel):
    patient_id: int
    type: str = "consultation"  # consultation, lab_result, imaging, procedure, etc.
    diagnosis: Optional[str] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    vital_signs: Optional[VitalSigns] = None


class RecordUpdate(BaseModel):
    diagnosis: Optional[str] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    vital_signs: Optional[VitalSigns] = None


class RecordResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: Optional[str] = None
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = None
    type: str
    diagnosis: Optional[str] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    vital_signs: Optional[dict] = None
    attachments: List[RecordAttachment] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecordsListResponse(BaseModel):
    records: List[RecordResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# ============ HELPER FUNCTIONS ============

def record_to_response(record: MedicalRecord, db: Session) -> dict:
    """Convert MedicalRecord model to response format"""
    patient = db.query(Patient).filter(Patient.id == record.patient_id).first() if record.patient_id else None
    doctor = db.query(Doctor).filter(Doctor.id == record.doctor_id).first() if record.doctor_id else None
    
    return {
        "id": record.id,
        "patient_id": record.patient_id,
        "patient_name": patient.name if patient else None,
        "doctor_id": record.doctor_id,
        "doctor_name": doctor.name if doctor else None,
        "type": record.record_type if hasattr(record, 'record_type') else "consultation",
        "diagnosis": record.diagnosis,
        "symptoms": record.symptoms if hasattr(record, 'symptoms') else None,
        "treatment": record.treatment,
        "notes": record.notes,
        "vital_signs": record.vital_signs if hasattr(record, 'vital_signs') else None,
        "attachments": [],  # TODO: Implement attachments
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if hasattr(record, 'updated_at') and record.updated_at else None
    }


# ============ ENDPOINTS ============

@router.get("", response_model=RecordsListResponse)
@router.get("/", response_model=RecordsListResponse)
async def get_records(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    patient_id: Optional[int] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get medical records (filtered by role).
    
    GET /api/records?page=1&limit=10&patient_id=5&type=consultation
    """
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.STAFF, UserRole.DOCTOR]:
        raise HTTPException(status_code=403, detail="Not authorized to view records")
    
    query = db.query(MedicalRecord)
    
    # Filter by patient
    if patient_id:
        query = query.filter(MedicalRecord.patient_id == patient_id)
    
    # Filter by type
    if type:
        if hasattr(MedicalRecord, 'record_type'):
            query = query.filter(MedicalRecord.record_type == type)
    
    # If doctor, only show their records
    if current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor:
            query = query.filter(MedicalRecord.doctor_id == doctor.id)
    
    total = query.count()
    skip = (page - 1) * limit
    records = query.order_by(MedicalRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "records": [record_to_response(r, db) for r in records],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/my-records", response_model=RecordsListResponse)
async def get_my_records(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get records for current patient.
    
    GET /api/records/my-records
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Only patients can access this endpoint")
    
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        return {
            "records": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "total_pages": 0
        }
    
    query = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.id)
    
    total = query.count()
    skip = (page - 1) * limit
    records = query.order_by(MedicalRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "records": [record_to_response(r, db) for r in records],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/{record_id}")
async def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific medical record.
    
    GET /api/records/{record_id}
    """
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Check permissions
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or record.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this record")
    
    return record_to_response(record, db)


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_record(
    record_data: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new medical record.
    
    POST /api/records
    """
    # Only doctors and admins can create records
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Only doctors can create medical records")
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == record_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get doctor ID if doctor is creating
    doctor_id = None
    if current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor:
            doctor_id = doctor.id
    
    new_record = MedicalRecord(
        patient_id=record_data.patient_id,
        doctor_id=doctor_id,
        diagnosis=record_data.diagnosis,
        treatment=record_data.treatment,
        notes=record_data.notes,
        created_at=datetime.utcnow()
    )
    
    # Set optional fields if model supports them
    if hasattr(new_record, 'record_type'):
        new_record.record_type = record_data.type
    if hasattr(new_record, 'symptoms'):
        new_record.symptoms = record_data.symptoms
    if hasattr(new_record, 'vital_signs') and record_data.vital_signs:
        new_record.vital_signs = record_data.vital_signs.model_dump()
    
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return record_to_response(new_record, db)


@router.put("/{record_id}")
async def update_record(
    record_id: int,
    record_data: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a medical record.
    
    PUT /api/records/{record_id}
    """
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Check permissions - only creator doctor or admin can update
    if current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or record.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Only the creating doctor can update this record")
    elif current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to update records")
    
    update_data = record_data.model_dump(exclude_unset=True)
    
    if "vital_signs" in update_data and update_data["vital_signs"]:
        if hasattr(update_data["vital_signs"], "model_dump"):
            update_data["vital_signs"] = update_data["vital_signs"].model_dump()
    
    for field, value in update_data.items():
        if hasattr(record, field):
            setattr(record, field, value)
    
    if hasattr(record, 'updated_at'):
        record.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(record)
    
    return record_to_response(record, db)


@router.delete("/{record_id}")
async def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Delete a medical record (Admin only).
    
    DELETE /api/records/{record_id}
    """
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db.delete(record)
    db.commit()
    
    return {"message": "Record deleted successfully"}


@router.post("/{record_id}/attachments", status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    record_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload attachment to a record.
    
    POST /api/records/{record_id}/attachments
    """
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Check permissions
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to upload attachments")
    
    # TODO: Implement file upload to storage (S3, local, etc.)
    # For now, return mock response
    
    return {
        "id": 1,
        "filename": file.filename,
        "url": f"/uploads/records/{record_id}/{file.filename}",
        "uploaded_at": datetime.utcnow().isoformat()
    }


@router.delete("/{record_id}/attachments/{attachment_id}")
async def delete_attachment(
    record_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an attachment.
    
    DELETE /api/records/{record_id}/attachments/{attachment_id}
    """
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # TODO: Implement actual file deletion
    
    return {"message": "Attachment deleted successfully"}
