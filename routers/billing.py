from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from config.database import get_db
from schemas.billing import (
    InvoiceCreate, InvoiceResponse, InvoiceDetailResponse,
    PaymentCreate, PaymentResponse
)
from services.billing_service import BillingService
from utils.security import get_current_user
from models.user import User, UserRole
from models.billing import InvoiceStatus

router = APIRouter(prefix="/api/v1/billing", tags=["Billing & Payments"])


@router.post("/invoices", response_model=InvoiceDetailResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new invoice (Admin/Staff only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and staff can create invoices"
        )
    
    invoice = BillingService.create_invoice(db=db, invoice_data=invoice_data)
    return invoice


@router.get("/invoices/my-invoices")
def get_my_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[InvoiceStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's invoices"""
    invoices, total = BillingService.get_patient_invoices(
        db=db,
        patient_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    return {
        "invoices": invoices,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/invoices/{invoice_id}", response_model=InvoiceDetailResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific invoice"""
    invoice = BillingService.get_invoice_by_id(
        db=db,
        invoice_id=invoice_id,
        user_id=current_user.id
    )
    return invoice


@router.post("/invoices/{invoice_id}/payments", response_model=PaymentResponse)
def make_payment(
    invoice_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Make a payment for an invoice"""
    payment = BillingService.process_payment(
        db=db,
        invoice_id=invoice_id,
        patient_id=current_user.id,
        payment_data=payment_data
    )
    return payment


@router.get("/invoices/{invoice_id}/payments")
def get_invoice_payments(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments for an invoice"""
    payments = BillingService.get_invoice_payments(
        db=db,
        invoice_id=invoice_id,
        user_id=current_user.id
    )
    return {"payments": payments}


@router.post("/invoices/{invoice_id}/cancel", response_model=InvoiceResponse)
def cancel_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an invoice (Admin/Staff only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and staff can cancel invoices"
        )
    
    invoice = BillingService.cancel_invoice(db=db, invoice_id=invoice_id)
    return invoice
