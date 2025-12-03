# FastAPI Backend Requirements for MediSecure

## Setup

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-jose[cryptography] passlib[bcrypt] python-multipart redis
```

## 1. Auth Endpoints

**SECURITY: HttpOnly Cookie Authentication**

Backend MUST set tokens as HttpOnly cookies (NOT in response body):

- `Set-Cookie: access_token=<jwt>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900`
- `Set-Cookie: refresh_token=<jwt>; HttpOnly; Secure; SameSite=Strict; Path=/api/auth/refresh; Max-Age=604800`

**Benefits:**

- ✅ Protected from XSS attacks (JavaScript cannot access)
- ✅ Automatic inclusion in requests (browser handles it)
- ✅ SameSite protection against CSRF
- ✅ Secure flag ensures HTTPS only

**Backend Implementation:**

```python
from fastapi import Cookie, HTTPException

# Extract token from HttpOnly cookie
def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Decode JWT and return user
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

### POST /api/auth/login

**Request:**

```json
{
  "email": "string",
  "password": "string"
}
```

**Response 200:**

```json
{
  "user": {
    "id": "string",
    "email": "string",
    "name": "string",
    "role": "admin" | "doctor" | "staff" | "patient"
  }
}
```

**Response Headers:**

```
Set-Cookie: access_token=<jwt>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900
Set-Cookie: refresh_token=<jwt>; HttpOnly; Secure; SameSite=Strict; Path=/api/auth/refresh; Max-Age=604800
```

**Response 401:**

```json
{
  "detail": "Invalid email or password"
}
```

**Response 429:**

```json
{
  "detail": "Too many failed attempts. Please try again in X minute(s)."
}
```

### POST /api/auth/register

**Request:**

```json
{
  "name": "string",
  "email": "string",
  "password": "string",
  "role": "admin" | "doctor" | "staff" | "patient",
  "phone": "string" (optional),
  "specialization": "string" (optional, doctor only),
  "department": "string" (optional, staff only)
}
```

**Response 201:**

```json
{
  "id": "string",
  "email": "string",
  "name": "string",
  "role": "string"
}
```

### POST /api/auth/refresh

**Request:** No body needed - refresh_token sent automatically via HttpOnly cookie

**Response 200:**

```json
{
  "message": "Token refreshed"
}
```

**Response Headers:**

```
Set-Cookie: access_token=<new_jwt>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900
```

**Note:** Browser automatically sends refresh_token cookie. Backend validates it and sets new access_token cookie.

### POST /api/auth/logout

**Request:** No body needed - cookies sent automatically

**Response 200:**

```json
{
  "message": "Logged out successfully"
}
```

**Response Headers:**

```
Set-Cookie: access_token=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Path=/api/auth/refresh; Max-Age=0
```

**Note:** Backend clears cookies by setting Max-Age=0

## 2. User Endpoints

### GET /api/users/me

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Response 200:**

```json
{
  "id": "string",
  "email": "string",
  "name": "string",
  "role": "string",
  "phone": "string",
  "specialization": "string" (doctor only),
  "department": "string" (staff only),
  "created_at": "datetime"
}
```

### PATCH /api/users/me

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Request:**

```json
{
  "name": "string" (optional),
  "phone": "string" (optional),
  "specialization": "string" (optional),
  "department": "string" (optional)
}
```

**Response 200:** Same as GET /api/users/me

## 3. Patient Endpoints

### GET /api/patients

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Query Params:** `?page=1&limit=10&search=string`
**Response 200:**

```json
{
  "patients": [
    {
      "id": "string",
      "name": "string",
      "email": "string",
      "phone": "string",
      "dateOfBirth": "date",
      "gender": "string",
      "address": "string",
      "created_at": "datetime"
    }
  ],
  "total": 0,
  "page": 1,
  "limit": 10
}
```

### GET /api/patients/:id

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Response 200:**

```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "phone": "string",
  "dateOfBirth": "date",
  "gender": "string",
  "address": "string",
  "bloodType": "string",
  "allergies": "string",
  "medicalHistory": "string",
  "created_at": "datetime"
}
```

### POST /api/patients

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Role:** admin, staff
**Request:**

```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "dateOfBirth": "date",
  "gender": "male" | "female" | "other",
  "address": "string",
  "bloodType": "string" (optional),
  "allergies": "string" (optional)
}
```

**Response 201:** Same as GET /api/patients/:id

## 4. Doctor Endpoints

### GET /api/doctors

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Query Params:** `?page=1&limit=10`
**Response 200:**

```json
{
  "doctors": [
    {
      "id": "string",
      "name": "string",
      "email": "string",
      "specialization": "string",
      "phone": "string"
    }
  ],
  "total": 0
}
```

### GET /api/doctors/:id

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Response 200:**

```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "specialization": "string",
  "phone": "string",
  "assignedPatients": 0
}
```

## 5. Appointment Endpoints

### GET /api/appointments

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Query Params:** `?page=1&limit=10&date=YYYY-MM-DD&status=scheduled|completed|cancelled`
**Response 200:**

```json
{
  "appointments": [
    {
      "id": "string",
      "patientId": "string",
      "patientName": "string",
      "doctorId": "string",
      "doctorName": "string",
      "date": "datetime",
      "status": "scheduled" | "completed" | "cancelled",
      "reason": "string",
      "notes": "string"
    }
  ],
  "total": 0
}
```

### POST /api/appointments

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Role:** staff, doctor, patient
**Request:**

```json
{
  "patientId": "string",
  "doctorId": "string",
  "date": "datetime",
  "reason": "string",
  "notes": "string" (optional)
}
```

**Response 201:** Same as appointment object

### PATCH /api/appointments/:id

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Request:**

```json
{
  "date": "datetime" (optional),
  "status": "scheduled" | "completed" | "cancelled" (optional),
  "notes": "string" (optional)
}
```

**Response 200:** Same as appointment object

## 6. Medical Records Endpoints

### GET /api/records

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Query Params:** `?patientId=string&page=1&limit=10`
**Response 200:**

```json
{
  "records": [
    {
      "id": "string",
      "patientId": "string",
      "patientName": "string",
      "doctorId": "string",
      "doctorName": "string",
      "date": "datetime",
      "diagnosis": "string",
      "prescription": "string",
      "notes": "string",
      "attachments": ["string"]
    }
  ],
  "total": 0
}
```

### POST /api/records

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Role:** doctor
**Request:**

```json
{
  "patientId": "string",
  "diagnosis": "string",
  "prescription": "string",
  "notes": "string",
  "attachments": ["string"] (optional)
}
```

**Response 201:** Same as record object

## 7. Dashboard Stats Endpoints

### GET /api/dashboard/stats

**Authentication:** Automatic via HttpOnly cookie (no Authorization header needed)
**Response 200 (Admin):**

```json
{
  "totalPatients": 1240,
  "totalDoctors": 48,
  "totalAppointments": 324,
  "revenue": 125400
}
```

**Response 200 (Doctor):**

```json
{
  "assignedPatients": 24,
  "todayAppointments": 8,
  "pendingReports": 5
}
```

**Response 200 (Staff):**

```json
{
  "managedPatients": 156,
  "scheduledAppointments": 45,
  "pendingRegistrations": 12
}
```

**Response 200 (Patient):**

```json
{
  "upcomingAppointments": 2,
  "medicalRecords": 8,
  "prescriptions": 3
}
```

## Security Requirements

### JWT Token Structure

```json
{
  "sub": "user_id",
  "email": "string",
  "role": "string",
  "exp": 1234567890
}
```

### Rate Limiting (Redis)

- Login endpoint: 5 attempts per 15 minutes per email
- All other endpoints: 100 requests per minute per user

### Password Requirements

- Minimum 6 characters
- Hashed with bcrypt (cost factor 12)

### CORS Settings

**CRITICAL for HttpOnly Cookies:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alt dev port
        # Add production domains
    ],
    allow_credentials=True,  # REQUIRED for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Frontend must set:**

```typescript
// In axios config
axios.defaults.withCredentials = true;

// Or per request
axiosInstance.create({
  baseURL: '...',
  withCredentials: true  // REQUIRED to send cookies
})
```

## Environment Variables (.env)

```
DATABASE_URL=postgresql://user:pass@localhost/medisecure
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Database Schema (SQLAlchemy Models)

### User

- id: UUID (PK)
- email: String (unique)
- password_hash: String
- name: String
- role: Enum(admin, doctor, staff, patient)
- phone: String (nullable)
- specialization: String (nullable)
- department: String (nullable)
- created_at: DateTime
- updated_at: DateTime

### Patient

- id: UUID (PK)
- user_id: UUID (FK to User, nullable)
- name: String
- email: String
- phone: String
- date_of_birth: Date
- gender: Enum(male, female, other)
- address: String
- blood_type: String (nullable)
- allergies: Text (nullable)
- medical_history: Text (nullable)
- created_at: DateTime

### Appointment

- id: UUID (PK)
- patient_id: UUID (FK)
- doctor_id: UUID (FK)
- date: DateTime
- status: Enum(scheduled, completed, cancelled)
- reason: String
- notes: Text (nullable)
- created_at: DateTime

### MedicalRecord

- id: UUID (PK)
- patient_id: UUID (FK)
- doctor_id: UUID (FK)
- date: DateTime
- diagnosis: Text
- prescription: Text
- notes: Text (nullable)
- attachments: JSON (nullable)
- created_at: DateTime

### LoginAttempt (Redis)

- key: `login:attempts:{email}`
- value: `{count: int, first_attempt: timestamp}`
- ttl: 900 seconds (15 minutes)

## Error Response Format (All Endpoints)

```json
{
  "detail": "Error message"
}
```

## HTTP Status Codes

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error
