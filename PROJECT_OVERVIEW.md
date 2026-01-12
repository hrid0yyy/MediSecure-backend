# MediSecure Backend - Project Overview

## 📋 Project Summary

**MediSecure** is a secure healthcare data management platform built with FastAPI. This is a Computer Security course project (version 2.0.0) that implements industry-standard security practices for handling sensitive medical information.

## 🏗️ Architecture Overview

### Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Cache/Session Store**: Redis
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: Argon2id
- **ORM**: SQLAlchemy
- **Migrations**: Alembic

### Infrastructure Components
The project uses Docker containers for:
- **PostgreSQL** (port 5432) - Main database
- **Redis Stack** (ports 6379, 8001) - Caching and session management
- **pgAdmin** (port 5050) - Database administration

## 🔐 Security Features

### 1. **Authentication & Authorization**
- **Email-based registration** with verification codes
- **JWT-based authentication** (5-hour token expiration)
- **Role-based access control** (Patient, Doctor, Admin, Staff)
- **Device fingerprinting** for multi-device security
- **2FA device verification** for new device logins
- **Password reset** with time-limited verification codes

### 2. **Password Security**
- **Argon2id hashing** algorithm (industry best practice)
- **Per-user salt generation** (16-character random salt)
- **Password history tracking** to prevent reuse
- **Secure password reset flow** with email verification

### 3. **Data Protection**
- **Field-level encryption** for sensitive PII (Personal Identifiable Information)
- **AES-256 encryption** for medical records and insurance numbers
- **Encrypted storage** of emergency contact information
- **Automatic decryption** on authorized access

### 4. **Security Middleware**
- **Security Headers Middleware**:
  - X-Frame-Options: DENY (clickjacking protection)
  - X-Content-Type-Options: nosniff
  - X-XSS-Protection: enabled
  - Content Security Policy (CSP)
  - Referrer-Policy
  - Permissions-Policy
  
- **Request Size Limit Middleware**: 10MB max (DoS protection)
- **Audit Logging Middleware**: Tracks all API requests
- **Rate Limiting**: Prevents brute force attacks
  - Signup: 5 requests/60 seconds
  - Login: 5 requests/60 seconds
  - Password reset: 3 requests/60 seconds

### 5. **Input Validation & Sanitization**
- **Email validation** using email-validator
- **HTML sanitization** using bleach library
- **SQL injection prevention** via SQLAlchemy ORM
- **XSS prevention** through input sanitization

### 6. **Audit Logging**
- Comprehensive logging of all user actions
- Tracks: user ID, action type, resource, IP address, user agent, timestamp
- Separate audit log database table
- Admin-accessible audit trail

## 📁 Project Structure

```
MediSecure-backend/
├── config/
│   ├── database.py          # PostgreSQL configuration
│   └── redis_db.py          # Redis configuration
├── models/
│   ├── user.py              # User and UserDevice models
│   ├── profile.py           # User profile with encrypted fields
│   └── audit.py             # Audit logging model
├── routers/
│   ├── auth.py              # Authentication endpoints
│   ├── user_management.py   # User CRUD operations
│   ├── admin.py             # Admin-only endpoints
│   └── users.py             # Legacy endpoints
├── schemas/
│   └── user.py              # Pydantic schemas for validation
├── middleware/
│   ├── audit.py             # Audit logging middleware
│   └── security.py          # Security headers & request limits
├── utils/
│   ├── security.py          # Password hashing, JWT, device fingerprinting
│   ├── encryption.py        # AES-256 field encryption
│   └── sanitization.py      # Input sanitization utilities
├── migrations/              # Alembic database migrations
├── main.py                  # FastAPI application entry point
└── requirements.txt         # Python dependencies
```

## 🔌 API Endpoints

### Authentication (`/auth`)
- `POST /auth/signup` - Register new user (sends verification email)
- `POST /auth/verify-email` - Verify email with code
- `POST /auth/login` - Login (returns JWT token)
- `POST /auth/verify-device` - Verify new device with code
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with code

### User Management (`/api/v1/users`)
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/me` - Delete account (soft delete)
- `GET /api/v1/users/me/devices` - List trusted devices
- `DELETE /api/v1/users/me/devices/{id}` - Remove device
- `POST /api/v1/users/me/change-password` - Change password
- `GET /api/v1/users/me/profile` - Get user profile (with decrypted data)
- `POST /api/v1/users/me/profile` - Create/update profile

### Admin (`/api/v1/admin`)
- `GET /api/v1/admin/users` - List all users (paginated, filterable)
- `GET /api/v1/admin/users/{id}` - Get user by ID
- `PUT /api/v1/admin/users/{id}/role` - Update user role
- `DELETE /api/v1/admin/users/{id}` - Delete user
- `GET /api/v1/admin/audit-logs` - Get audit logs (paginated, filterable)
- `GET /api/v1/admin/users/{id}/audit-logs` - Get user-specific audit logs
- `GET /api/v1/admin/dashboard` - Get dashboard statistics

### Health & Documentation
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## 🗄️ Database Models

### User Model
```python
- id: Integer (Primary Key)
- email: String (Unique, Indexed)
- hashed_password: String
- salt: String (16-char random)
- role: Enum (patient, doctor, admin, staff)
- is_verified: Boolean
```

### UserDevice Model
```python
- id: Integer (Primary Key)
- user_id: Foreign Key
- fingerprint_hash: String (SHA-256 of user-agent + IP)
- last_login: DateTime
- created_at: DateTime
```

### UserProfile Model
```python
- id: Integer (Primary Key)
- user_id: Foreign Key
- first_name: String
- last_name: String
- date_of_birth: Date
- phone: String
- address: String
- medical_record_number: String (Encrypted)
- insurance_number: String (Encrypted)
- emergency_contact_name: String (Encrypted)
- emergency_contact_phone: String (Encrypted)
```

### AuditLog Model
```python
- id: Integer (Primary Key)
- user_id: Foreign Key (Nullable)
- action: String (LOGIN, CREATE, UPDATE, DELETE, etc.)
- resource: String (users, auth, admin, etc.)
- resource_id: String (Optional)
- ip_address: String
- user_agent: String
- details: JSON
- status: String (SUCCESS/FAILURE)
- created_at: DateTime
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- PostgreSQL client (optional, for direct DB access)

### Installation Steps

1. **Clone the repository** (if applicable)

2. **Create virtual environment**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Start Docker containers**
   ```powershell
   # PostgreSQL
   docker run --name medisecure -e POSTGRES_PASSWORD=1234 -p 5432:5432 -d postgres
   
   # Redis
   docker run --name redis-stack -p 6379:6379 -p 8001:8001 -d redis/redis-stack:latest
   
   # pgAdmin (optional)
   docker run --name pgadmin -p 5050:80 -e PGADMIN_DEFAULT_EMAIL=admin@example.com -e PGADMIN_DEFAULT_PASSWORD=1234 -d dpage/pgadmin4
   ```

5. **Configure environment variables**
   Create a `.env` file with:
   ```env
   # Database
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=1234
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=cs_project_db
   
   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   
   # JWT
   SECRET_KEY=your-secret-key-here
   
   # Email (Gmail SMTP)
   GMAIL_EMAIL=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   ```

6. **Initialize database**
   ```powershell
   python init_db.py
   ```

7. **Run the application**
   ```powershell
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access the API**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Redis UI: http://localhost:8001

## 🧪 Testing

Test scripts are available in:
- `test-apis.ps1` - PowerShell script for API testing
- `test-commands.txt` - Manual test commands
- `quick-test.ps1` - Quick validation tests

Example test flow:
```powershell
# 1. Health check
curl http://localhost:8000/health

# 2. Sign up
$body = @{email="test@example.com"; password="SecurePass123!"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/auth/signup" -Method POST -Body $body -ContentType "application/json"

# 3. Verify email (check email for code)
$verify = @{email="test@example.com"; code="123456"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/auth/verify-email" -Method POST -Body $verify -ContentType "application/json"

# 4. Login
$login = @{email="test@example.com"; password="SecurePass123!"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body $login -ContentType "application/json"
$token = $response.access_token

# 5. Access protected endpoint
$headers = @{Authorization="Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me" -Headers $headers
```

## 📧 Email Configuration

The system uses Gmail SMTP for sending verification emails:
- Email verification codes (10-minute expiration)
- Password reset codes (10-minute expiration)
- New device verification codes (10-minute expiration)

**Setup Gmail App Password:**
1. Enable 2FA on your Google account
2. Generate an App Password at: https://myaccount.google.com/apppasswords
3. Add to `.env` file as `GMAIL_APP_PASSWORD`

## 🔒 Security Best Practices Implemented

1. ✅ **Password Security**: Argon2id + per-user salts
2. ✅ **Data Encryption**: AES-256 for sensitive fields
3. ✅ **Input Validation**: Pydantic schemas + sanitization
4. ✅ **Rate Limiting**: Prevents brute force attacks
5. ✅ **Audit Logging**: Complete activity tracking
6. ✅ **Device Fingerprinting**: Multi-device security
7. ✅ **Security Headers**: OWASP recommended headers
8. ✅ **SQL Injection Prevention**: ORM-based queries
9. ✅ **XSS Prevention**: Input sanitization + CSP
10. ✅ **CSRF Protection**: Token-based authentication
11. ✅ **DoS Protection**: Request size limits + rate limiting
12. ✅ **Session Management**: JWT with expiration
13. ✅ **Role-Based Access Control**: Granular permissions
14. ✅ **Secure Password Reset**: Time-limited verification codes

## 📊 Key Features

### For Patients
- Secure account registration with email verification
- Profile management with encrypted sensitive data
- Device management (view and remove trusted devices)
- Password change with history tracking
- Secure password reset flow

### For Admins
- User management (list, view, update roles, delete)
- Comprehensive audit log access
- Dashboard with system statistics
- User activity monitoring
- Filterable and paginated data views

### System-wide
- Automatic audit logging of all actions
- Email notifications for security events
- Device-based 2FA for new logins
- Encrypted storage of PII
- GDPR-compliant data handling

## 🛠️ Development Tools

- **Alembic**: Database migrations
- **pgAdmin**: Database administration UI
- **Redis Insight**: Redis data browser (built into redis-stack)
- **Swagger UI**: Interactive API documentation
- **ReDoc**: Alternative API documentation

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | postgres |
| `POSTGRES_PASSWORD` | PostgreSQL password | password |
| `POSTGRES_HOST` | PostgreSQL host | localhost |
| `POSTGRES_PORT` | PostgreSQL port | 5432 |
| `POSTGRES_DB` | Database name | cs_project_db |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |
| `SECRET_KEY` | JWT secret key | (required) |
| `GMAIL_EMAIL` | Gmail address for SMTP | (required) |
| `GMAIL_APP_PASSWORD` | Gmail app password | (required) |

## 🐛 Troubleshooting

### Database Connection Issues
```powershell
# Check if PostgreSQL container is running
docker ps

# View container logs
docker logs medisecure

# Get container IP (if needed)
docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" medisecure
```

### Redis Connection Issues
```powershell
# Check Redis container
docker ps | grep redis

# Test Redis connection
docker exec -it redis-stack redis-cli ping
```

### Email Not Sending
- Check Gmail credentials in `.env`
- Verify 2FA is enabled on Google account
- Ensure App Password is correctly generated
- Check `app.log` for error messages

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Argon2 Specification**: https://github.com/P-H-C/phc-winner-argon2
- **OWASP Security Guidelines**: https://owasp.org/

## 🎯 Project Goals (Computer Security Course)

This project demonstrates:
1. Secure authentication and authorization mechanisms
2. Data encryption at rest and in transit
3. Input validation and sanitization
4. Audit logging and monitoring
5. Defense against common web vulnerabilities (OWASP Top 10)
6. Implementation of security best practices
7. Compliance with data protection standards

## 📄 License

This is an educational project for a Computer Security course.

---

**Version**: 2.0.0  
**Last Updated**: January 2026  
**Course**: Computer Security - Fall 2025
