# MediSecure Quick Start Guide

## Prerequisites
1. PostgreSQL running on port 5432
2. Redis container (ID: d59f8abe8785...)
3. Python 3.12+ with virtual environment activated

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create/update `.env` file with:
```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cs_project_db

# JWT
SECRET_KEY=your-secret-key-here

# Encryption (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_MASTER_KEY=your-encryption-key-here

# Email
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

### 3. Run Database Migrations
```bash
alembic upgrade head
```

### 4. Start the Server

**Option 1: Use the batch file (easiest)**
```bash
start.bat
```

**Option 2: Manual start**
```bash
# Start Redis
docker start d59f8abe87858e71f425285e8ab10b8f73d3af979a81fe2b7ba1a9093ab2d440

# Start FastAPI
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Access the API

- **API Server:** http://localhost:8000
- **Interactive Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## Create Your First Admin User

1. Sign up via API:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "SecurePass123"}'
```

2. Verify email with code sent to your email

3. Promote to admin (in PostgreSQL):
```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

4. Login to get token:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "SecurePass123"}'
```

5. Use the returned token for admin endpoints:
```bash
curl -X GET http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Key Features Available

### For All Users:
- ✅ User registration with email verification
- ✅ Login with device fingerprinting
- ✅ View/update profile
- ✅ Change password (with history check)
- ✅ Manage trusted devices
- ✅ Create encrypted user profile with PII

### For Admins:
- ✅ List and manage all users
- ✅ View audit logs
- ✅ Dashboard with statistics
- ✅ Update user roles
- ✅ Delete user accounts

## Testing

Test the endpoints using:
1. **Swagger UI:** http://localhost:8000/docs (interactive)
2. **curl** commands (see IMPLEMENTATION_SUMMARY.md)
3. **Postman** or similar API client

## Troubleshooting

**Server won't start:**
- Check PostgreSQL is running
- Check Redis container is running
- Verify `.env` file exists and has correct values

**Migration errors:**
- Ensure database exists: `createdb cs_project_db`
- Run: `alembic upgrade head`

**Encryption errors:**
- Set `ENCRYPTION_MASTER_KEY` in `.env`
- Generate new key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

**Can't access admin endpoints:**
- Ensure user role is 'admin' in database
- Use valid JWT token in Authorization header

## Development Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Check current version
alembic current

# View migration history
alembic history
```

## Security Notes

⚠️ **Important for Production:**
1. Change `SECRET_KEY` to a strong random value
2. Generate and secure `ENCRYPTION_MASTER_KEY`
3. Use strong database passwords
4. Enable SSL for PostgreSQL
5. Use environment-specific `.env` files
6. Enable HTTPS and uncomment HSTS in security middleware
7. Restrict CORS origins
8. Use secure Redis password
9. Implement rate limiting on all endpoints
10. Regular security audits of audit logs

## Next Steps

1. Create your first user and test authentication
2. Create a user profile with encrypted PII
3. Test password change with history check
4. Explore admin dashboard endpoints
5. Review audit logs for system activity

For detailed implementation information, see `IMPLEMENTATION_SUMMARY.md`
