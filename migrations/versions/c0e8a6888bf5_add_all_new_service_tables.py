"""add_all_new_service_tables

Revision ID: c0e8a6888bf5
Revises: 732f811a8566
Create Date: 2026-01-12 14:37:46.023678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0e8a6888bf5'
down_revision: Union[str, Sequence[str], None] = 'd5f9ff81772c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create appointments table
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('appointment_date', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('SCHEDULED', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'NO_SHOW', 'RESCHEDULED', name='appointmentstatus'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_id'), 'appointments', ['id'], unique=False)
    
    # Create prescriptions table
    op.create_table(
        'prescriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('prescription_number', sa.String(100), nullable=False, unique=True),
        sa.Column('status', sa.Enum('ACTIVE', 'COMPLETED', 'CANCELLED', 'EXPIRED', name='prescriptionstatus'), nullable=True),
        sa.Column('diagnosis', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('digital_signature', sa.Text(), nullable=True),
        sa.Column('issued_date', sa.DateTime(), nullable=True),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
        sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescriptions_id'), 'prescriptions', ['id'], unique=False)
    
    # Create prescription_medications table
    op.create_table(
        'prescription_medications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=False),
        sa.Column('medication_name', sa.String(255), nullable=False),
        sa.Column('dosage', sa.String(100), nullable=False),
        sa.Column('frequency', sa.String(100), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('refills_allowed', sa.Integer(), nullable=True),
        sa.Column('refills_remaining', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create medical_records table
    op.create_table(
        'medical_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('record_type', sa.Enum('DIAGNOSIS', 'TREATMENT', 'LAB_RESULT', 'IMAGING', 'ALLERGY', 'IMMUNIZATION', 'VITAL_SIGNS', 'SURGERY', name='recordtype'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('encrypted_data', sa.Text(), nullable=True),
        sa.Column('diagnosis_code', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('recorded_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create medication_reminders table
    op.create_table(
        'medication_reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=True),
        sa.Column('medication_name', sa.String(255), nullable=False),
        sa.Column('dosage', sa.String(100), nullable=False),
        sa.Column('reminder_times', sa.String(255), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'PAUSED', 'COMPLETED', name='reminderstatus'), nullable=True),
        sa.Column('notify_via_email', sa.Boolean(), nullable=True),
        sa.Column('notify_via_sms', sa.Boolean(), nullable=True),
        sa.Column('notify_caregiver', sa.Boolean(), nullable=True),
        sa.Column('caregiver_email', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create medication_adherence table
    op.create_table(
        'medication_adherence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reminder_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(), nullable=False),
        sa.Column('taken_at', sa.DateTime(), nullable=True),
        sa.Column('was_taken', sa.Boolean(), nullable=True),
        sa.Column('was_skipped', sa.Boolean(), nullable=True),
        sa.Column('skip_reason', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['reminder_id'], ['medication_reminders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create telemedicine_sessions table
    op.create_table(
        'telemedicine_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(500), nullable=True),
        sa.Column('room_id', sa.String(255), nullable=False, unique=True),
        sa.Column('status', sa.Enum('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'NO_SHOW', name='sessionstatus'), nullable=True),
        sa.Column('scheduled_start', sa.DateTime(), nullable=False),
        sa.Column('actual_start', sa.DateTime(), nullable=True),
        sa.Column('actual_end', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('recording_url', sa.String(500), nullable=True),
        sa.Column('recording_consent', sa.Boolean(), nullable=True),
        sa.Column('consultation_notes', sa.Text(), nullable=True),
        sa.Column('follow_up_required', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
        sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create health_metrics table
    op.create_table(
        'health_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('metric_type', sa.Enum('BLOOD_PRESSURE', 'HEART_RATE', 'TEMPERATURE', 'BLOOD_GLUCOSE', 'WEIGHT', 'HEIGHT', 'BMI', 'OXYGEN_SATURATION', 'STEPS', 'SLEEP_HOURS', name='metrictype'), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('systolic', sa.Float(), nullable=True),
        sa.Column('diastolic', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('device_name', sa.String(100), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create medical_documents table
    op.create_table(
        'medical_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.Enum('LAB_REPORT', 'IMAGING', 'PRESCRIPTION', 'INSURANCE', 'REFERRAL', 'CONSENT_FORM', 'MEDICAL_CERTIFICATE', 'OTHER', name='documenttype'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('encrypted', sa.Integer(), nullable=True),
        sa.Column('ocr_text', sa.Text(), nullable=True),
        sa.Column('document_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.Enum('APPOINTMENT_REMINDER', 'MEDICATION_REMINDER', 'TEST_RESULT', 'PRESCRIPTION_READY', 'APPOINTMENT_CANCELLED', 'NEW_MESSAGE', 'PAYMENT_DUE', 'SYSTEM_ALERT', name='notificationtype'), nullable=False),
        sa.Column('channel', sa.Enum('EMAIL', 'SMS', 'PUSH', 'IN_APP', name='notificationchannel'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SENT', 'DELIVERED', 'FAILED', 'READ', name='notificationstatus'), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('failed_reason', sa.Text(), nullable=True),
        sa.Column('extra_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(255), nullable=True),
        sa.Column('encrypted_content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('is_emergency', sa.Boolean(), nullable=True),
        sa.Column('parent_message_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_message_id'], ['messages.id'], ),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create message_attachments table
    op.create_table(
        'message_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('invoice_number', sa.String(100), nullable=False, unique=True),
        sa.Column('status', sa.Enum('DRAFT', 'PENDING', 'PAID', 'PARTIALLY_PAID', 'OVERDUE', 'CANCELLED', name='invoicestatus'), nullable=True),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('tax_amount', sa.Float(), nullable=True),
        sa.Column('discount_amount', sa.Float(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('amount_paid', sa.Float(), nullable=True),
        sa.Column('balance_due', sa.Float(), nullable=False),
        sa.Column('issue_date', sa.DateTime(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('paid_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create invoice_items table
    op.create_table(
        'invoice_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('service_code', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('payment_method', sa.Enum('CASH', 'CREDIT_CARD', 'DEBIT_CARD', 'INSURANCE', 'BANK_TRANSFER', 'ONLINE', name='paymentmethod'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('transaction_id', sa.String(255), nullable=True),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_successful', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create insurance_claims table
    op.create_table(
        'insurance_claims',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('claim_number', sa.String(100), nullable=False, unique=True),
        sa.Column('insurance_provider', sa.String(255), nullable=False),
        sa.Column('policy_number', sa.String(100), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'SUBMITTED', 'IN_REVIEW', 'APPROVED', 'PARTIALLY_APPROVED', 'DENIED', 'APPEALED', name='claimstatus'), nullable=True),
        sa.Column('claim_amount', sa.Float(), nullable=False),
        sa.Column('approved_amount', sa.Float(), nullable=True),
        sa.Column('denied_amount', sa.Float(), nullable=True),
        sa.Column('denial_reason', sa.Text(), nullable=True),
        sa.Column('submission_date', sa.DateTime(), nullable=True),
        sa.Column('response_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create phi_access_logs table
    op.create_table(
        'phi_access_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('access_reason', sa.Text(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('access_granted', sa.Boolean(), nullable=True),
        sa.Column('denial_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create consents table
    op.create_table(
        'consents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('consent_type', sa.String(100), nullable=False),
        sa.Column('consent_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False),
        sa.Column('consent_version', sa.String(50), nullable=True),
        sa.Column('granted_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('document_url', sa.String(500), nullable=True),
        sa.Column('signature_data', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop all tables in reverse order
    op.drop_table('consents')
    op.drop_table('phi_access_logs')
    op.drop_table('insurance_claims')
    op.drop_table('payments')
    op.drop_table('invoice_items')
    op.drop_table('invoices')
    op.drop_table('message_attachments')
    op.drop_table('messages')
    op.drop_table('notifications')
    op.drop_table('medical_documents')
    op.drop_table('health_metrics')
    op.drop_table('telemedicine_sessions')
    op.drop_table('medication_adherence')
    op.drop_table('medication_reminders')
    op.drop_table('medical_records')
    op.drop_table('prescription_medications')
    op.drop_table('prescriptions')
    op.drop_index(op.f('ix_appointments_id'), table_name='appointments')
    op.drop_table('appointments')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS appointmentstatus')
    op.execute('DROP TYPE IF EXISTS prescriptionstatus')
    op.execute('DROP TYPE IF EXISTS recordtype')
    op.execute('DROP TYPE IF EXISTS reminderstatus')
    op.execute('DROP TYPE IF EXISTS sessionstatus')
    op.execute('DROP TYPE IF EXISTS metrictype')
    op.execute('DROP TYPE IF EXISTS documenttype')
    op.execute('DROP TYPE IF EXISTS notificationtype')
    op.execute('DROP TYPE IF EXISTS notificationchannel')
    op.execute('DROP TYPE IF EXISTS notificationstatus')
    op.execute('DROP TYPE IF EXISTS invoicestatus')
    op.execute('DROP TYPE IF EXISTS paymentmethod')
    op.execute('DROP TYPE IF EXISTS claimstatus')
