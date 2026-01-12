from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from models.billing import InvoiceStatus, PaymentMethod


class InvoiceItemCreate(BaseModel):
    description: str = Field(..., min_length=5, max_length=255)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    service_code: Optional[str] = None

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    items: list[InvoiceItemCreate]
    tax_amount: float = Field(default=0.0, ge=0)
    discount_amount: float = Field(default=0.0, ge=0)
    due_date: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    payment_method: PaymentMethod
    amount: float = Field(..., gt=0)
    transaction_id: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class InvoiceItemResponse(BaseModel):
    id: int
    description: str
    quantity: int
    unit_price: float
    total_price: float
    service_code: Optional[str]

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    patient_id: int
    invoice_number: str
    status: InvoiceStatus
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    amount_paid: float
    balance_due: float
    issue_date: datetime
    due_date: datetime
    paid_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceDetailResponse(InvoiceResponse):
    items: list[InvoiceItemResponse]

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    payment_method: PaymentMethod
    amount: float
    transaction_id: Optional[str]
    payment_date: datetime
    is_successful: bool

    class Config:
        from_attributes = True
