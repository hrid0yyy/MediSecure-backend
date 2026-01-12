# MediSecure Backend API Endpoints

## Server Configuration
- **Base URL**: `http://localhost:8000`
- **Port**: `8000`
- **Host**: `0.0.0.0`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Documentation**: `http://localhost:8000/redoc` (ReDoc)

---

## General Endpoints

### Root Endpoint
```
GET /
```
**Description**: Returns welcome message and documentation links  
**Response**:
```json
{
  "message": "Welcome to MediSecure!",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### Health Check
```
GET /health
```
**Description**: Health check endpoint  
**Response**:
```json
{
  "status": "healthy"
}
```

---

## Authentication Endpoints

All authentication endpoints are prefixed with `/auth`

### 1. User Signup
```
POST /auth/signup
```
**Rate Limit**: 5 requests per 60 seconds  
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```
**Response** (201 Created):
```json
{
  "message": "Verification code sent. Please check your email."
}
```
**Notes**:
- Verification code expires in 10 minutes
- User role is automatically set to "patient"
- Email must be unique

---

### 2. Verify Email
```
POST /auth/verify-email
```
**Rate Limit**: 5 requests per 60 seconds  
**Request Body**:
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```
**Response** (200 OK):
```json
{
  "message": "Email verified and user registered successfully"
}
```
**Error Responses**:
- `400 Bad Request`: Invalid or expired verification code

---

### 3. User Login
```
POST /auth/login
```
**Rate Limit**: 5 requests per 60 seconds  
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```
**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
**Special Response** (401 Unauthorized - New Device Detected):
```json
{
  "detail": "New device detected. Please verify your device."
}
```
**Headers**: `X-Device-Verification-Required: true`

**Error Responses**:
- `403 Forbidden`: Invalid credentials or email not verified

**Notes**:
- Device fingerprinting is enabled
- First-time login from a new device requires additional verification

---

### 4. Verify New Device
```
POST /auth/verify-device
```
**Rate Limit**: 5 requests per 60 seconds  
**Request Body**:
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```
**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
**Error Responses**:
- `400 Bad Request`: Invalid or expired verification code, or device fingerprint mismatch
- `404 Not Found`: User not found

**Notes**:
- Verification code expires in 10 minutes
- Device fingerprint must match the one used during login

---

### 5. Forgot Password
```
POST /auth/forgot-password
```
**Rate Limit**: 3 requests per 60 seconds  
**Request Body**:
```json
{
  "email": "user@example.com"
}
```
**Response** (200 OK):
```json
{
  "message": "If the email exists, a reset code has been sent."
}
```
**Notes**:
- Response is intentionally vague for security
- Reset code expires in 10 minutes

---

### 6. Reset Password
```
POST /auth/reset-password
```
**Rate Limit**: 3 requests per 60 seconds  
**Request Body**:
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "newSecurePassword123"
}
```
**Response** (200 OK):
```json
{
  "message": "Password reset successfully"
}
```
**Error Responses**:
- `400 Bad Request`: Invalid or expired reset code
- `404 Not Found`: User not found

---

## User Endpoints

All user endpoints are prefixed with `/users`

### 1. Get Users
```
GET /users/
```
**Description**: Returns list of users  
**Response** (200 OK):
```json
[
  {"username": "Rick"},
  {"username": "Morty"}
]
```
**Notes**: Currently a placeholder implementation

---

## Authentication Flow

### Registration Flow
1. `POST /auth/signup` - User submits email and password
2. System sends verification code to email
3. `POST /auth/verify-email` - User submits verification code
4. User is registered and can login

### Login Flow (Known Device)
1. `POST /auth/login` - User submits credentials
2. System returns JWT token
3. User can access protected endpoints with token

### Login Flow (New Device)
1. `POST /auth/login` - User submits credentials
2. System detects new device and sends verification code
3. System returns 401 with device verification required
4. `POST /auth/verify-device` - User submits verification code
5. System returns JWT token

### Password Reset Flow
1. `POST /auth/forgot-password` - User submits email
2. System sends reset code to email
3. `POST /auth/reset-password` - User submits code and new password
4. Password is updated

---

## Security Features

- **Rate Limiting**: All endpoints have rate limits to prevent abuse
- **Device Fingerprinting**: Tracks known devices for enhanced security
- **Email Verification**: Required for all new accounts
- **JWT Tokens**: Used for authentication
- **Password Hashing**: Passwords are salted and hashed
- **Time-limited Codes**: All verification codes expire in 10 minutes

---

## Error Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request or expired code
- `401 Unauthorized`: Device verification required
- `403 Forbidden`: Invalid credentials or unverified email
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Database or server error

---

## Token Usage

After successful login, include the JWT token in the Authorization header for protected endpoints:

```
Authorization: Bearer <access_token>
```

Example:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Development Notes

- Default token expiration can be configured via environment variables
- SMTP credentials required for email functionality (Gmail)
- Redis required for temporary data storage
- PostgreSQL database required for persistent storage
