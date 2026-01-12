# API Endpoints - Version 2.0

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Get a token by logging in via `/auth/login`

---

## 📋 User Management Endpoints (`/api/v1/users`)

### GET /api/v1/users/me
**Description:** Get current user's information  
**Auth Required:** Yes  
**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "patient",
  "is_verified": true
}
```

---

### PUT /api/v1/users/me
**Description:** Update current user's email  
**Auth Required:** Yes  
**Request Body:**
```json
{
  "email": "newemail@example.com"
}
```
**Response:**
```json
{
  "message": "Email updated successfully. Please verify your new email."
}
```
**Note:** Email change requires re-verification

---

### DELETE /api/v1/users/me
**Description:** Delete current user's account  
**Auth Required:** Yes  
**Response:**
```json
{
  "message": "Account deletion requested. Contact support to complete the process."
}
```

---

### GET /api/v1/users/me/devices
**Description:** List all trusted devices  
**Auth Required:** Yes  
**Response:**
```json
{
  "devices": [
    {
      "id": 1,
      "fingerprint_hash": "a1b2c3d4e5f6g7h8...",
      "last_login": "2026-01-12T10:30:00",
      "created_at": "2026-01-10T09:00:00"
    }
  ]
}
```

---

### DELETE /api/v1/users/me/devices/{device_id}
**Description:** Remove a trusted device  
**Auth Required:** Yes  
**Path Parameters:**
- `device_id` (integer) - Device ID to remove

**Response:**
```json
{
  "message": "Device removed successfully"
}
```

---

### POST /api/v1/users/me/change-password
**Description:** Change password with history check  
**Auth Required:** Yes  
**Request Body:**
```json
{
  "current_password": "CurrentPass123",
  "new_password": "NewSecurePass456"
}
```
**Response:**
```json
{
  "message": "Password changed successfully"
}
```
**Validation:**
- Current password must be correct
- New password must be at least 8 characters
- Cannot reuse last 5 passwords

---

### GET /api/v1/users/me/profile
**Description:** Get user profile with decrypted PII  
**Auth Required:** Yes  
**Response:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "phone": "555-0123",
  "address": "123 Main St, City, State 12345",
  "medical_record_number": "MRN123456",
  "insurance_number": "INS789012",
  "blood_type": "A+",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "555-0124",
  "profile_picture_url": null,
  "created_at": "2026-01-12T10:00:00",
  "updated_at": "2026-01-12T10:00:00"
}
```
**Note:** Sensitive fields are automatically decrypted

---

### POST /api/v1/users/me/profile
**Description:** Create or update user profile  
**Auth Required:** Yes  
**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "phone": "555-0123",
  "address": "123 Main St, City, State 12345",
  "medical_record_number": "MRN123456",
  "insurance_number": "INS789012",
  "blood_type": "A+",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "555-0124"
}
```
**Response:**
```json
{
  "message": "Profile saved successfully",
  "profile_id": 1
}
```
**Note:** Sensitive fields are automatically encrypted before storage

**Encrypted Fields:**
- first_name, last_name, date_of_birth
- phone, address
- medical_record_number, insurance_number
- emergency_contact_name, emergency_contact_phone

---

## 👑 Admin Endpoints (`/api/v1/admin`)

**Note:** All admin endpoints require user role to be 'admin'

### GET /api/v1/admin/users
**Description:** List all users with pagination  
**Auth Required:** Yes (Admin)  
**Query Parameters:**
- `skip` (integer, default: 0) - Number of records to skip
- `limit` (integer, default: 100) - Maximum records to return
- `role` (string, optional) - Filter by role (patient/doctor/admin/staff)
- `verified` (boolean, optional) - Filter by verification status

**Example:**
```
GET /api/v1/admin/users?skip=0&limit=10&role=patient&verified=true
```

**Response:**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "role": "patient",
    "is_verified": true
  }
]
```

---

### GET /api/v1/admin/users/{user_id}
**Description:** Get specific user details  
**Auth Required:** Yes (Admin)  
**Path Parameters:**
- `user_id` (integer) - User ID

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "patient",
  "is_verified": true
}
```

---

### PUT /api/v1/admin/users/{user_id}/role
**Description:** Update user's role  
**Auth Required:** Yes (Admin)  
**Path Parameters:**
- `user_id` (integer) - User ID

**Query Parameters:**
- `new_role` (string) - New role (patient/doctor/admin/staff)

**Example:**
```
PUT /api/v1/admin/users/2/role?new_role=doctor
```

**Response:**
```json
{
  "message": "User role updated to doctor"
}
```

**Restrictions:**
- Cannot change own role

---

### DELETE /api/v1/admin/users/{user_id}
**Description:** Delete user account  
**Auth Required:** Yes (Admin)  
**Path Parameters:**
- `user_id` (integer) - User ID

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

**Restrictions:**
- Cannot delete own account
- Also deletes associated devices

---

### GET /api/v1/admin/audit-logs
**Description:** Get paginated audit logs  
**Auth Required:** Yes (Admin)  
**Query Parameters:**
- `skip` (integer, default: 0) - Records to skip
- `limit` (integer, default: 100) - Max records
- `user_id` (integer, optional) - Filter by user
- `action` (string, optional) - Filter by action type
- `status` (string, optional) - Filter by status (SUCCESS/FAILURE)

**Example:**
```
GET /api/v1/admin/audit-logs?skip=0&limit=50&action=LOGIN&status=FAILURE
```

**Response:**
```json
{
  "total": 150,
  "skip": 0,
  "limit": 50,
  "logs": [
    {
      "id": 1,
      "user_id": 2,
      "action": "LOGIN",
      "resource": "auth",
      "resource_id": null,
      "ip_address": "192.168.1.1",
      "status": "FAILURE",
      "details": "{\"reason\": \"invalid_password\"}",
      "created_at": "2026-01-12T10:30:00"
    }
  ]
}
```

---

### GET /api/v1/admin/stats
**Description:** Get dashboard statistics  
**Auth Required:** Yes (Admin)  
**Response:**
```json
{
  "users": {
    "total": 150,
    "verified": 145,
    "by_role": {
      "patient": 130,
      "doctor": 15,
      "admin": 3,
      "staff": 2
    }
  },
  "devices": {
    "total": 287
  },
  "activity_last_24h": {
    "total_actions": 523,
    "failed_logins": 8
  }
}
```

---

### GET /api/v1/admin/audit-logs/user/{user_id}
**Description:** Get audit logs for specific user  
**Auth Required:** Yes (Admin)  
**Path Parameters:**
- `user_id` (integer) - User ID

**Query Parameters:**
- `skip` (integer, default: 0) - Records to skip
- `limit` (integer, default: 100) - Max records

**Example:**
```
GET /api/v1/admin/audit-logs/user/2?skip=0&limit=50
```

**Response:**
```json
{
  "user_id": 2,
  "user_email": "user@example.com",
  "total": 75,
  "logs": [
    {
      "id": 1,
      "action": "LOGIN",
      "resource": "auth",
      "ip_address": "192.168.1.1",
      "status": "SUCCESS",
      "created_at": "2026-01-12T10:30:00"
    }
  ]
}
```

---

## 🔐 Security Features

### Audit Actions
All actions are logged with the following types:
- `LOGIN`, `LOGOUT`, `SIGNUP`
- `PASSWORD_CHANGE`, `PASSWORD_RESET`
- `EMAIL_UPDATE`, `PROFILE_UPDATE`
- `CREATE`, `READ`, `UPDATE`, `DELETE`
- `DEVICE_REMOVE`, `ACCOUNT_DELETE`

### Encrypted Profile Fields
The following fields are encrypted at rest:
- Personal: first_name, last_name, date_of_birth
- Contact: phone, address
- Medical: medical_record_number, insurance_number
- Emergency: emergency_contact_name, emergency_contact_phone

### Password Policy
- Minimum 8 characters
- Cannot reuse last 5 passwords
- Hashed with Argon2id
- Per-user salt

### Security Headers
All responses include:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Content-Security-Policy
- Referrer-Policy
- Permissions-Policy

### Request Limits
- Maximum request body size: 10 MB
- Rate limiting: 5 requests/minute for auth endpoints

---

## 📊 HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Not authenticated or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - Request body exceeds limit
- `500 Internal Server Error` - Server error

---

## 🧪 Testing Examples

### Test User Endpoints

```bash
# Get your info
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create profile
curl -X POST http://localhost:8000/api/v1/users/me/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "555-0123",
    "date_of_birth": "1990-01-15"
  }'

# Change password
curl -X POST http://localhost:8000/api/v1/users/me/change-password \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPass123",
    "new_password": "NewSecurePass456"
  }'
```

### Test Admin Endpoints

```bash
# Get all users
curl -X GET "http://localhost:8000/api/v1/admin/users?skip=0&limit=10" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Get stats
curl -X GET http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Get audit logs
curl -X GET "http://localhost:8000/api/v1/admin/audit-logs?limit=50" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 📖 Interactive Documentation

For interactive API testing, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Both provide:
- Complete endpoint documentation
- Request/response schemas
- Try-it-out functionality
- Authentication support

---

**Version:** 2.0.0  
**Last Updated:** January 12, 2026
