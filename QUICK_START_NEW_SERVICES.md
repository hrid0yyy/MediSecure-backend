# Quick Start Guide - New Services

## 🚀 Getting Started

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run Database Migration
```powershell
alembic upgrade head
```

### 3. Start the Server
```powershell
uvicorn main:app --reload
```

### 4. Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 Testing the New APIs

### Create an Appointment
```powershell
$token = "your-jwt-token-here"
$body = @{
    doctor_id = 2
    appointment_date = "2026-01-15T10:00:00"
    duration_minutes = 30
    reason = "Regular checkup and consultation"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments/" `
    -Method POST `
    -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} `
    -Body $body
```

### Create a Prescription (Doctor only)
```powershell
$body = @{
    patient_id = 5
    diagnosis = "Bacterial infection - requires antibiotic treatment"
    medications = @(
        @{
            medication_name = "Amoxicillin"
            dosage = "500mg"
            frequency = "3 times daily"
            duration_days = 7
            quantity = 21
            refills_allowed = 1
        }
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prescriptions/" `
    -Method POST `
    -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} `
    -Body $body
```

### Send a Secure Message
```powershell
$body = @{
    recipient_id = 2
    subject = "Question about medication"
    content = "Hello Doctor, I have a question about my prescription..."
    is_emergency = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/messages/" `
    -Method POST `
    -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} `
    -Body $body
```

### Create an Invoice (Admin/Staff only)
```powershell
$body = @{
    patient_id = 5
    items = @(
        @{
            description = "Consultation Fee"
            quantity = 1
            unit_price = 150.00
        },
        @{
            description = "Lab Test - Complete Blood Count"
            quantity = 1
            unit_price = 50.00
        }
    )
    tax_amount = 20.00
    discount_amount = 0.00
    due_date = "2026-01-30T23:59:59"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/billing/invoices" `
    -Method POST `
    -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} `
    -Body $body
```

## 🔐 Authentication Required

All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## 📊 Available Endpoints

### Appointments
- `POST /api/v1/appointments/` - Create appointment
- `GET /api/v1/appointments/my-appointments` - List my appointments
- `GET /api/v1/appointments/{id}` - Get appointment details
- `PUT /api/v1/appointments/{id}` - Update appointment
- `POST /api/v1/appointments/{id}/cancel` - Cancel appointment

### Prescriptions
- `POST /api/v1/prescriptions/` - Create prescription
- `GET /api/v1/prescriptions/my-prescriptions` - List my prescriptions
- `GET /api/v1/prescriptions/{id}` - Get prescription details
- `POST /api/v1/prescriptions/{id}/cancel` - Cancel prescription
- `POST /api/v1/prescriptions/medications/{id}/refill` - Request refill

### Messages
- `POST /api/v1/messages/` - Send message
- `GET /api/v1/messages/inbox` - Get inbox
- `GET /api/v1/messages/sent` - Get sent messages
- `GET /api/v1/messages/{id}` - View message
- `DELETE /api/v1/messages/{id}` - Delete message

### Billing
- `POST /api/v1/billing/invoices` - Create invoice
- `GET /api/v1/billing/invoices/my-invoices` - List my invoices
- `GET /api/v1/billing/invoices/{id}` - Get invoice details
- `POST /api/v1/billing/invoices/{id}/payments` - Make payment
- `GET /api/v1/billing/invoices/{id}/payments` - List payments

## 🎭 User Roles

Different endpoints require different roles:

- **Patient** - Can create appointments, view prescriptions, send messages, view invoices, make payments
- **Doctor** - Can view appointments, create prescriptions, view medical records, send messages
- **Admin/Staff** - Can create invoices, manage all resources, access audit logs
- **Superadmin** - Full system access

## 🔍 Query Parameters

Most list endpoints support pagination:
- `skip` - Number of records to skip (default: 0)
- `limit` - Number of records to return (default: 20, max: 100)
- `status` - Filter by status (varies by endpoint)

Example:
```
GET /api/v1/appointments/my-appointments?skip=0&limit=10&status=SCHEDULED
```

## 🛠️ Development Tips

1. **Check Database Schema**: Use pgAdmin or `psql` to view tables
2. **View Logs**: Check console output for detailed error messages
3. **Use Swagger UI**: Interactive API testing at `/docs`
4. **Migration Issues**: Run `alembic history` to check migration chain

## 🐛 Troubleshooting

### Database Connection Error
```powershell
# Check if PostgreSQL is running
Get-Service postgresql*

# Update connection string in .env file
DATABASE_URL=postgresql://user:password@localhost/medisecure
```

### Import Errors
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Migration Errors
```powershell
# Check current version
alembic current

# View migration history
alembic history

# Downgrade if needed
alembic downgrade -1

# Then upgrade again
alembic upgrade head
```

## 📚 Additional Resources

- Full API Documentation: `/docs`
- Project Overview: `PROJECT_OVERVIEW.md`
- Implementation Details: `IMPLEMENTATION_SUMMARY.md`
- Potential Services: `POTENTIAL_SERVICES.md`
