# MediSecure API Documentation

**Base URL:** `http://localhost:8000`  
**API Version:** 2.0.0  
**Authentication:** JWT Bearer Token (except auth endpoints)

---

## Table of Contents
1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Admin Operations](#admin-operations)
4. [Appointments](#appointments)
5. [Prescriptions](#prescriptions)
6. [Messaging](#messaging)
7. [Billing & Payments](#billing--payments)
8. [Error Handling](#error-handling)

---

## Authentication

All authenticated endpoints require JWT token in header:
```
Authorization: Bearer <your-jwt-token>
```

### 1. User Signup
**Endpoint:** `POST /auth/signup`  
**Authentication:** None  
**Rate Limit:** 5 requests/minute

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!@#"
}
```

**Response (201 Created):**
```json
{
  "message": "User created successfully. Please verify your email.",
  "user_id": 1,
  "email": "user@example.com"
}
```

**Errors:**
- `400` - Email already exists
- `422` - Validation error (weak password, invalid email)

---

### 2. Email Verification
**Endpoint:** `POST /auth/verify`  
**Authentication:** None

**Request Body:**
```json
{
  "email": "user@example.com",
  "verification_code": "123456"
}
```

**Response (200 OK):**
```json
{
  "message": "Email verified successfully"
}
```

**Errors:**
- `400` - Invalid or expired code
- `404` - User not found

---

### 3. Login
**Endpoint:** `POST /auth/login`  
**Authentication:** None  
**Rate Limit:** 5 requests/minute

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!@#",
  "device_name": "Chrome on Windows",
  "device_fingerprint": "unique-device-id"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "patient",
    "is_verified": true
  }
}
```

**Errors:**
- `401` - Invalid credentials
- `403` - Email not verified or device verification required

---

### 4. Device Verification
**Endpoint:** `POST /auth/verify-device`  
**Authentication:** None

**Request Body:**
```json
{
  "email": "user@example.com",
  "verification_code": "123456",
  "device_fingerprint": "unique-device-id"
}
```

**Response (200 OK):**
```json
{
  "message": "Device verified successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 5. Forgot Password
**Endpoint:** `POST /auth/forgot-password`  
**Authentication:** None

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset code sent to your email"
}
```

---

### 6. Reset Password
**Endpoint:** `POST /auth/reset-password`  
**Authentication:** None

**Request Body:**
```json
{
  "email": "user@example.com",
  "reset_code": "123456",
  "new_password": "NewSecurePass123!@#"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

---

## User Management

### 7. Get Current User
**Endpoint:** `GET /api/v1/users/me`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "patient",
  "is_verified": true,
  "created_at": "2026-01-12T10:00:00"
}
```

---

### 8. Get User Profile
**Endpoint:** `GET /api/v1/users/profile`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "full_name": "John Doe",
  "date_of_birth": "1990-01-15",
  "phone": "+1234567890",
  "address": "123 Main St",
  "medical_record_number": "MRN123456",
  "created_at": "2026-01-12T10:00:00"
}
```

**Errors:**
- `404` - Profile not found

---

### 9. Create/Update Profile
**Endpoint:** `POST /api/v1/users/profile`  
**Authentication:** Required

**Request Body:**
```json
{
  "full_name": "John Doe",
  "date_of_birth": "1990-01-15",
  "phone": "+1234567890",
  "address": "123 Main St",
  "ssn": "123-45-6789",
  "medical_record_number": "MRN123456",
  "insurance_number": "INS987654"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "profile": {
    "id": 1,
    "full_name": "John Doe",
    "date_of_birth": "1990-01-15",
    "phone": "+1234567890"
  }
}
```

---

### 10. Update User Information
**Endpoint:** `PUT /api/v1/users/me`  
**Authentication:** Required

**Request Body:**
```json
{
  "email": "newemail@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "User information updated successfully",
  "user": {
    "id": 1,
    "email": "newemail@example.com",
    "role": "patient"
  }
}
```

---

### 11. Change Password
**Endpoint:** `POST /api/v1/users/change-password`  
**Authentication:** Required

**Request Body:**
```json
{
  "current_password": "OldPass123!@#",
  "new_password": "NewPass123!@#"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Errors:**
- `400` - Incorrect current password
- `400` - New password cannot be same as last 5 passwords

---

### 12. Get Active Devices
**Endpoint:** `GET /api/v1/users/devices`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "devices": [
    {
      "id": 1,
      "device_name": "Chrome on Windows",
      "device_fingerprint": "abc123...",
      "last_used": "2026-01-12T10:00:00",
      "is_current": true
    }
  ]
}
```

---

### 13. Remove Device
**Endpoint:** `DELETE /api/v1/users/devices/{device_id}`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "message": "Device removed successfully"
}
```

---

### 14. Delete Account
**Endpoint:** `DELETE /api/v1/users/me`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "message": "Account deleted successfully"
}
```

---

## Admin Operations

**Required Role:** `admin` or `superadmin`

### 15. Get All Users
**Endpoint:** `GET /api/v1/admin/users`  
**Authentication:** Required (Admin)

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 20, max: 100) - Number of records to return
- `role` (string, optional) - Filter by role: patient, doctor, admin, staff, superadmin
- `is_verified` (boolean, optional) - Filter by verification status

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "role": "patient",
      "is_verified": true,
      "created_at": "2026-01-12T10:00:00"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

---

### 16. Get User by ID
**Endpoint:** `GET /api/v1/admin/users/{user_id}`  
**Authentication:** Required (Admin)

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "patient",
  "is_verified": true,
  "created_at": "2026-01-12T10:00:00",
  "profile": {
    "full_name": "John Doe",
    "phone": "+1234567890"
  }
}
```

---

### 17. Update User Role
**Endpoint:** `PUT /api/v1/admin/users/{user_id}/role`  
**Authentication:** Required (Admin)

**Request Body:**
```json
{
  "role": "doctor"
}
```

**Response (200 OK):**
```json
{
  "message": "User role updated successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "doctor"
  }
}
```

**Valid Roles:** patient, doctor, admin, staff, superadmin

---

### 18. Delete User
**Endpoint:** `DELETE /api/v1/admin/users/{user_id}`  
**Authentication:** Required (Admin)

**Response (200 OK):**
```json
{
  "message": "User deleted successfully"
}
```

---

### 19. Get Audit Logs
**Endpoint:** `GET /api/v1/admin/audit-logs`  
**Authentication:** Required (Admin)

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 50, max: 200)
- `user_id` (int, optional)
- `action` (string, optional)
- `start_date` (datetime, optional)
- `end_date` (datetime, optional)

**Response (200 OK):**
```json
{
  "logs": [
    {
      "id": 1,
      "user_id": 1,
      "action": "LOGIN",
      "endpoint": "/auth/login",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2026-01-12T10:00:00"
    }
  ],
  "total": 500,
  "page": 1,
  "page_size": 50
}
```

---

### 20. Admin Dashboard
**Endpoint:** `GET /api/v1/admin/dashboard`  
**Authentication:** Required (Admin)

**Response (200 OK):**
```json
{
  "total_users": 150,
  "verified_users": 140,
  "total_doctors": 15,
  "total_patients": 130,
  "recent_signups": 5,
  "active_sessions": 42,
  "total_appointments": 250,
  "pending_appointments": 15
}
```

---

## Appointments

### 21. Create Appointment
**Endpoint:** `POST /api/v1/appointments/`  
**Authentication:** Required (Patient)

**Request Body:**
```json
{
  "doctor_id": 2,
  "appointment_date": "2026-01-15T10:00:00",
  "duration_minutes": 30,
  "reason": "Regular checkup and consultation for my condition"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "patient_id": 1,
  "doctor_id": 2,
  "appointment_date": "2026-01-15T10:00:00",
  "duration_minutes": 30,
  "reason": "Regular checkup and consultation for my condition",
  "status": "scheduled",
  "notes": null,
  "created_at": "2026-01-12T10:00:00",
  "updated_at": "2026-01-12T10:00:00"
}
```

**Errors:**
- `400` - Invalid doctor ID or scheduling conflict
- `422` - Validation error (reason too short, invalid date)

---

### 22. Get My Appointments
**Endpoint:** `GET /api/v1/appointments/my-appointments`  
**Authentication:** Required

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 20, max: 100)
- `status` (string, optional) - Filter by status: scheduled, confirmed, cancelled, completed, no_show, rescheduled

**Response (200 OK):**
```json
{
  "appointments": [
    {
      "id": 1,
      "patient_id": 1,
      "doctor_id": 2,
      "appointment_date": "2026-01-15T10:00:00",
      "duration_minutes": 30,
      "reason": "Regular checkup",
      "status": "scheduled",
      "created_at": "2026-01-12T10:00:00"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

---

### 23. Get Doctor Appointments
**Endpoint:** `GET /api/v1/appointments/doctor/{doctor_id}`  
**Authentication:** Required

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 20)
- `date_from` (datetime, optional)
- `date_to` (datetime, optional)

**Response (200 OK):**
```json
{
  "appointments": [...],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

---

### 24. Get Appointment Details
**Endpoint:** `GET /api/v1/appointments/{appointment_id}`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "patient_id": 1,
  "doctor_id": 2,
  "appointment_date": "2026-01-15T10:00:00",
  "duration_minutes": 30,
  "reason": "Regular checkup",
  "status": "scheduled",
  "notes": null,
  "cancellation_reason": null,
  "created_at": "2026-01-12T10:00:00",
  "updated_at": "2026-01-12T10:00:00"
}
```

---

### 25. Update Appointment
**Endpoint:** `PUT /api/v1/appointments/{appointment_id}`  
**Authentication:** Required

**Request Body:**
```json
{
  "appointment_date": "2026-01-16T11:00:00",
  "duration_minutes": 45,
  "reason": "Updated reason for visit",
  "notes": "Patient requested time change"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "appointment_date": "2026-01-16T11:00:00",
  "duration_minutes": 45,
  "status": "rescheduled",
  "updated_at": "2026-01-12T11:00:00"
}
```

---

### 26. Cancel Appointment
**Endpoint:** `POST /api/v1/appointments/{appointment_id}/cancel`  
**Authentication:** Required

**Request Body:**
```json
{
  "cancellation_reason": "Unable to attend due to emergency"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "cancelled",
  "cancellation_reason": "Unable to attend due to emergency",
  "updated_at": "2026-01-12T12:00:00"
}
```

---

## Prescriptions

### 27. Create Prescription
**Endpoint:** `POST /api/v1/prescriptions/`  
**Authentication:** Required (Doctor only)

**Request Body:**
```json
{
  "patient_id": 5,
  "appointment_id": 10,
  "diagnosis": "Bacterial infection - requires antibiotic treatment",
  "notes": "Take with food to avoid stomach upset",
  "medications": [
    {
      "medication_name": "Amoxicillin",
      "dosage": "500mg",
      "frequency": "3 times daily",
      "duration_days": 7,
      "quantity": 21,
      "instructions": "Take after meals",
      "refills_allowed": 1
    },
    {
      "medication_name": "Ibuprofen",
      "dosage": "400mg",
      "frequency": "As needed for pain",
      "duration_days": 7,
      "quantity": 14,
      "instructions": "Do not exceed 3 doses per day",
      "refills_allowed": 0
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "patient_id": 5,
  "doctor_id": 2,
  "prescription_number": "RX-20260112100000-A1B2C3D4",
  "status": "active",
  "diagnosis": "Bacterial infection - requires antibiotic treatment",
  "notes": "Take with food to avoid stomach upset",
  "issued_date": "2026-01-12T10:00:00",
  "expiry_date": "2027-01-12T10:00:00",
  "created_at": "2026-01-12T10:00:00",
  "medications": [
    {
      "id": 1,
      "medication_name": "Amoxicillin",
      "dosage": "500mg",
      "frequency": "3 times daily",
      "duration_days": 7,
      "quantity": 21,
      "instructions": "Take after meals",
      "refills_allowed": 1,
      "refills_remaining": 1
    }
  ]
}
```

**Errors:**
- `403` - Only doctors can create prescriptions
- `404` - Patient not found
- `422` - Validation error

---

### 28. Get My Prescriptions
**Endpoint:** `GET /api/v1/prescriptions/my-prescriptions`  
**Authentication:** Required

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 20, max: 100)
- `status` (string, optional) - Filter: active, completed, cancelled, expired

**Response (200 OK):**
```json
{
  "prescriptions": [
    {
      "id": 1,
      "prescription_number": "RX-20260112100000-A1B2C3D4",
      "doctor_id": 2,
      "status": "active",
      "diagnosis": "Bacterial infection",
      "issued_date": "2026-01-12T10:00:00",
      "expiry_date": "2027-01-12T10:00:00"
    }
  ],
  "total": 3,
  "page": 1,
  "page_size": 20
}
```

---

### 29. Get Prescription Details
**Endpoint:** `GET /api/v1/prescriptions/{prescription_id}`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "patient_id": 5,
  "doctor_id": 2,
  "prescription_number": "RX-20260112100000-A1B2C3D4",
  "status": "active",
  "diagnosis": "Bacterial infection",
  "notes": "Take with food",
  "issued_date": "2026-01-12T10:00:00",
  "expiry_date": "2027-01-12T10:00:00",
  "medications": [
    {
      "id": 1,
      "medication_name": "Amoxicillin",
      "dosage": "500mg",
      "frequency": "3 times daily",
      "duration_days": 7,
      "quantity": 21,
      "instructions": "Take after meals",
      "refills_allowed": 1,
      "refills_remaining": 1
    }
  ]
}
```

---

### 30. Cancel Prescription
**Endpoint:** `POST /api/v1/prescriptions/{prescription_id}/cancel`  
**Authentication:** Required (Doctor who prescribed)

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "cancelled",
  "updated_at": "2026-01-12T11:00:00"
}
```

**Errors:**
- `403` - Only the prescribing doctor can cancel
- `404` - Prescription not found

---

### 31. Request Medication Refill
**Endpoint:** `POST /api/v1/prescriptions/medications/{medication_id}/refill`  
**Authentication:** Required (Patient)

**Response (200 OK):**
```json
{
  "message": "Refill processed successfully",
  "refills_remaining": 0
}
```

**Errors:**
- `400` - No refills remaining, contact doctor
- `403` - Not authorized
- `404` - Medication not found

---

## Messaging

### 32. Send Message
**Endpoint:** `POST /api/v1/messages/`  
**Authentication:** Required

**Request Body:**
```json
{
  "recipient_id": 2,
  "subject": "Question about medication",
  "content": "Hello Doctor, I have a question about my prescription. Should I take the medication before or after meals?",
  "is_emergency": false,
  "parent_message_id": null
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "sender_id": 1,
  "recipient_id": 2,
  "subject": "Question about medication",
  "content": "Hello Doctor, I have a question about my prescription...",
  "is_read": false,
  "read_at": null,
  "is_emergency": false,
  "parent_message_id": null,
  "created_at": "2026-01-12T10:00:00"
}
```

**Note:** Content is encrypted at rest and decrypted for display.

---

### 33. Get Inbox
**Endpoint:** `GET /api/v1/messages/inbox`  
**Authentication:** Required

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 50, max: 100)
- `unread_only` (boolean, default: false)

**Response (200 OK):**
```json
{
  "messages": [
    {
      "id": 1,
      "sender_id": 2,
      "recipient_id": 1,
      "subject": "Re: Question about medication",
      "content": "You should take it after meals...",
      "is_read": false,
      "read_at": null,
      "is_emergency": false,
      "created_at": "2026-01-12T11:00:00"
    }
  ],
  "total": 15,
  "unread_count": 3,
  "page": 1,
  "page_size": 50
}
```

---

### 34. Get Sent Messages
**Endpoint:** `GET /api/v1/messages/sent`  
**Authentication:** Required

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 50)

**Response (200 OK):**
```json
{
  "messages": [
    {
      "id": 1,
      "sender_id": 1,
      "recipient_id": 2,
      "subject": "Question about medication",
      "content": "Hello Doctor...",
      "is_read": true,
      "read_at": "2026-01-12T10:30:00",
      "created_at": "2026-01-12T10:00:00"
    }
  ],
  "total": 8,
  "page": 1,
  "page_size": 50
}
```

---

### 35. Get Message Details
**Endpoint:** `GET /api/v1/messages/{message_id}`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "sender_id": 2,
  "recipient_id": 1,
  "subject": "Re: Question about medication",
  "content": "You should take it after meals to avoid stomach upset. Also, make sure to complete the full course...",
  "is_read": true,
  "read_at": "2026-01-12T10:30:00",
  "is_emergency": false,
  "parent_message_id": null,
  "created_at": "2026-01-12T11:00:00"
}
```

**Note:** Automatically marks message as read if recipient views it.

---

### 36. Delete Message
**Endpoint:** `DELETE /api/v1/messages/{message_id}`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "message": "Message deleted successfully"
}
```

**Errors:**
- `403` - Only recipient can delete messages
- `404` - Message not found

---

### 37. Mark Message as Read
**Endpoint:** `POST /api/v1/messages/{message_id}/mark-read`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "is_read": true,
  "read_at": "2026-01-12T12:00:00"
}
```

---

## Billing & Payments

### 38. Create Invoice
**Endpoint:** `POST /api/v1/billing/invoices`  
**Authentication:** Required (Admin/Staff only)

**Request Body:**
```json
{
  "patient_id": 5,
  "appointment_id": 10,
  "items": [
    {
      "description": "Consultation Fee",
      "quantity": 1,
      "unit_price": 150.00,
      "service_code": "99213"
    },
    {
      "description": "Lab Test - Complete Blood Count",
      "quantity": 1,
      "unit_price": 50.00,
      "service_code": "85025"
    }
  ],
  "tax_amount": 20.00,
  "discount_amount": 0.00,
  "due_date": "2026-01-30T23:59:59",
  "notes": "Payment due within 30 days"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "patient_id": 5,
  "invoice_number": "INV-20260112-A1B2C3",
  "status": "pending",
  "subtotal": 200.00,
  "tax_amount": 20.00,
  "discount_amount": 0.00,
  "total_amount": 220.00,
  "amount_paid": 0.00,
  "balance_due": 220.00,
  "issue_date": "2026-01-12T10:00:00",
  "due_date": "2026-01-30T23:59:59",
  "notes": "Payment due within 30 days",
  "created_at": "2026-01-12T10:00:00",
  "items": [
    {
      "id": 1,
      "description": "Consultation Fee",
      "quantity": 1,
      "unit_price": 150.00,
      "total_price": 150.00,
      "service_code": "99213"
    },
    {
      "id": 2,
      "description": "Lab Test - Complete Blood Count",
      "quantity": 1,
      "unit_price": 50.00,
      "total_price": 50.00,
      "service_code": "85025"
    }
  ]
}
```

**Errors:**
- `403` - Only admin/staff can create invoices
- `404` - Patient not found

---

### 39. Get My Invoices
**Endpoint:** `GET /api/v1/billing/invoices/my-invoices`  
**Authentication:** Required

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 20)
- `status` (string, optional) - Filter: draft, pending, paid, partially_paid, overdue, cancelled

**Response (200 OK):**
```json
{
  "invoices": [
    {
      "id": 1,
      "invoice_number": "INV-20260112-A1B2C3",
      "status": "pending",
      "total_amount": 220.00,
      "amount_paid": 0.00,
      "balance_due": 220.00,
      "issue_date": "2026-01-12T10:00:00",
      "due_date": "2026-01-30T23:59:59",
      "created_at": "2026-01-12T10:00:00"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

---

### 40. Get Invoice Details
**Endpoint:** `GET /api/v1/billing/invoices/{invoice_id}`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "patient_id": 5,
  "invoice_number": "INV-20260112-A1B2C3",
  "status": "pending",
  "subtotal": 200.00,
  "tax_amount": 20.00,
  "discount_amount": 0.00,
  "total_amount": 220.00,
  "amount_paid": 0.00,
  "balance_due": 220.00,
  "issue_date": "2026-01-12T10:00:00",
  "due_date": "2026-01-30T23:59:59",
  "paid_date": null,
  "notes": "Payment due within 30 days",
  "items": [
    {
      "id": 1,
      "description": "Consultation Fee",
      "quantity": 1,
      "unit_price": 150.00,
      "total_price": 150.00,
      "service_code": "99213"
    }
  ]
}
```

---

### 41. Make Payment
**Endpoint:** `POST /api/v1/billing/invoices/{invoice_id}/payments`  
**Authentication:** Required

**Request Body:**
```json
{
  "payment_method": "credit_card",
  "amount": 220.00,
  "transaction_id": null,
  "notes": "Paid via credit card",
  "card_number": "4111111111111111",
  "cvv": "123",
  "expiry": "12/25"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "invoice_id": 1,
  "payment_method": "credit_card",
  "amount": 220.00,
  "transaction_id": "TXN-20260112100000-A1B2C3D4",
  "payment_date": "2026-01-12T10:00:00",
  "is_successful": true
}
```

**Payment Methods:** cash, credit_card, debit_card, insurance, bank_transfer, online

**Errors:**
- `400` - Payment amount exceeds balance due
- `403` - Not authorized
- `404` - Invoice not found

**Note:** Uses dummy payment processor. In production, integrate real payment gateway.

---

### 42. Get Invoice Payments
**Endpoint:** `GET /api/v1/billing/invoices/{invoice_id}/payments`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "payments": [
    {
      "id": 1,
      "payment_method": "credit_card",
      "amount": 220.00,
      "transaction_id": "TXN-20260112100000-A1B2C3D4",
      "payment_date": "2026-01-12T10:00:00",
      "is_successful": true,
      "notes": "Paid via credit card"
    }
  ]
}
```

---

### 43. Cancel Invoice
**Endpoint:** `POST /api/v1/billing/invoices/{invoice_id}/cancel`  
**Authentication:** Required (Admin/Staff only)

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "cancelled",
  "updated_at": "2026-01-12T11:00:00"
}
```

**Errors:**
- `400` - Cannot cancel a paid invoice
- `403` - Only admin/staff can cancel invoices

---

## Error Handling

### Standard Error Response Format

All errors follow this structure:

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error, business logic error)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

### Common Error Examples

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Authentication Error (401):**
```json
{
  "detail": "Could not validate credentials"
}
```

**Permission Error (403):**
```json
{
  "detail": "Only doctors can create prescriptions"
}
```

**Not Found (404):**
```json
{
  "detail": "User not found"
}
```

**Rate Limit (429):**
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## Rate Limits

### Authentication Endpoints
- `/auth/signup` - 5 requests/minute
- `/auth/login` - 5 requests/minute
- `/auth/forgot-password` - 3 requests/minute

### Other Endpoints
- General API calls - 100 requests/minute per user

---

## Pagination

Most list endpoints support pagination:

**Query Parameters:**
- `skip` - Number of records to skip (default: 0)
- `limit` - Number of records to return (default varies, max: 100)

**Response includes:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

---

## Authentication Flow

1. **Signup** → `POST /auth/signup`
2. **Verify Email** → `POST /auth/verify` (code sent to email)
3. **Login** → `POST /auth/login`
4. **If new device** → `POST /auth/verify-device` (code sent to email)
5. **Use token** → Include in `Authorization: Bearer <token>` header

---

## Testing Credentials

### Test Card Numbers (Dummy Payment):
- `4111111111111111` - Successful payment
- `4111111111110000` - Declined payment

### Test Phone Numbers:
- Any valid format (10+ digits)

---

## Swagger Documentation

Interactive API documentation available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

**Last Updated:** January 12, 2026  
**API Version:** 2.0.0
