from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from models.billing import Invoice, InvoiceItem, Payment, InvoiceStatus
from schemas.billing import InvoiceCreate, PaymentCreate
import secrets


class BillingService:
    """Business logic for billing and payment management"""

    @staticmethod
    def _generate_invoice_number() -> str:
        """Generate unique invoice number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_part = secrets.token_hex(3).upper()
        return f"INV-{timestamp}-{random_part}"

    @staticmethod
    def create_invoice(
        db: Session,
        invoice_data: InvoiceCreate
    ) -> Invoice:
        """Create a new invoice"""
        
        # Calculate totals
        subtotal = sum(item.quantity * item.unit_price for item in invoice_data.items)
        total_amount = subtotal + invoice_data.tax_amount - invoice_data.discount_amount
        
        # Create invoice
        invoice = Invoice(
            patient_id=invoice_data.patient_id,
            appointment_id=invoice_data.appointment_id,
            invoice_number=BillingService._generate_invoice_number(),
            status=InvoiceStatus.PENDING,
            subtotal=subtotal,
            tax_amount=invoice_data.tax_amount,
            discount_amount=invoice_data.discount_amount,
            total_amount=total_amount,
            balance_due=total_amount,
            due_date=invoice_data.due_date,
            notes=invoice_data.notes
        )
        
        db.add(invoice)
        db.flush()
        
        # Add invoice items
        for item_data in invoice_data.items:
            total_price = item_data.quantity * item_data.unit_price
            item = InvoiceItem(
                invoice_id=invoice.id,
                **item_data.model_dump(),
                total_price=total_price
            )
            db.add(item)
        
        db.commit()
        db.refresh(invoice)
        
        return invoice

    @staticmethod
    def get_patient_invoices(
        db: Session,
        patient_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[InvoiceStatus] = None
    ) -> tuple[List[Invoice], int]:
        """Get all invoices for a patient"""
        query = db.query(Invoice).filter(Invoice.patient_id == patient_id)
        
        if status:
            query = query.filter(Invoice.status == status)
        
        total = query.count()
        invoices = query.order_by(Invoice.issue_date.desc()).offset(skip).limit(limit).all()
        
        return invoices, total

    @staticmethod
    def get_invoice_by_id(
        db: Session,
        invoice_id: int,
        user_id: int
    ) -> Invoice:
        """Get a specific invoice"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Verify user has permission to view
        if invoice.patient_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this invoice"
            )
        
        return invoice

    @staticmethod
    def process_payment(
        db: Session,
        invoice_id: int,
        patient_id: int,
        payment_data: PaymentCreate
    ) -> Payment:
        """Process a payment for an invoice"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        if invoice.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        if payment_data.amount > invoice.balance_due:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount exceeds balance due"
            )
        
        # Create payment record
        payment = Payment(
            invoice_id=invoice_id,
            patient_id=patient_id,
            **payment_data.model_dump()
        )
        db.add(payment)
        
        # Update invoice
        invoice.amount_paid += payment_data.amount
        invoice.balance_due -= payment_data.amount
        
        if invoice.balance_due == 0:
            invoice.status = InvoiceStatus.PAID
            invoice.paid_date = datetime.utcnow()
        elif invoice.amount_paid > 0:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        
        invoice.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(payment)
        
        return payment

    @staticmethod
    def get_invoice_payments(
        db: Session,
        invoice_id: int,
        user_id: int
    ) -> List[Payment]:
        """Get all payments for an invoice"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        if invoice.patient_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        payments = db.query(Payment).filter(Payment.invoice_id == invoice_id).all()
        
        return payments

    @staticmethod
    def cancel_invoice(
        db: Session,
        invoice_id: int
    ) -> Invoice:
        """Cancel an invoice"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        if invoice.status == InvoiceStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel a paid invoice"
            )
        
        invoice.status = InvoiceStatus.CANCELLED
        invoice.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(invoice)
        
        return invoice
