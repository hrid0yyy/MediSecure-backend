"""
Seed Script for MediSecure Database
Adds dummy doctors, patients, and sample data for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from config.database import engine, SessionLocal
from models import User, UserRole, Doctor, Patient
from models.profile import UserProfile
from utils.security import get_password_hash, generate_salt
from datetime import datetime, date
import random

# Sample data
DOCTOR_DATA = [
    {"name": "Dr. Sarah Johnson", "specialization": "Cardiology", "email": "sarah.johnson@medisecure.com", "phone": "+1-555-0101", "bio": "Board-certified cardiologist with 15 years of experience in cardiovascular diseases.", "fee": 200.00},
    {"name": "Dr. Michael Chen", "specialization": "Neurology", "email": "michael.chen@medisecure.com", "phone": "+1-555-0102", "bio": "Specialist in neurological disorders including epilepsy and stroke management.", "fee": 250.00},
    {"name": "Dr. Emily Williams", "specialization": "Pediatrics", "email": "emily.williams@medisecure.com", "phone": "+1-555-0103", "bio": "Passionate pediatrician dedicated to children's health and wellness.", "fee": 150.00},
    {"name": "Dr. James Rodriguez", "specialization": "Orthopedics", "email": "james.rodriguez@medisecure.com", "phone": "+1-555-0104", "bio": "Expert in sports medicine and joint replacement surgery.", "fee": 220.00},
    {"name": "Dr. Lisa Park", "specialization": "Dermatology", "email": "lisa.park@medisecure.com", "phone": "+1-555-0105", "bio": "Specializes in skin conditions, cosmetic dermatology, and skin cancer treatment.", "fee": 180.00},
    {"name": "Dr. Robert Thompson", "specialization": "General Medicine", "email": "robert.thompson@medisecure.com", "phone": "+1-555-0106", "bio": "Family medicine physician providing comprehensive primary care.", "fee": 120.00},
    {"name": "Dr. Amanda Foster", "specialization": "Gynecology", "email": "amanda.foster@medisecure.com", "phone": "+1-555-0107", "bio": "Women's health specialist with expertise in reproductive medicine.", "fee": 190.00},
    {"name": "Dr. David Kim", "specialization": "Psychiatry", "email": "david.kim@medisecure.com", "phone": "+1-555-0108", "bio": "Mental health professional specializing in anxiety and depression treatment.", "fee": 200.00},
    {"name": "Dr. Jennifer Martinez", "specialization": "Oncology", "email": "jennifer.martinez@medisecure.com", "phone": "+1-555-0109", "bio": "Oncologist dedicated to cancer treatment and patient support.", "fee": 300.00},
    {"name": "Dr. William Brown", "specialization": "ENT", "email": "william.brown@medisecure.com", "phone": "+1-555-0110", "bio": "Ear, nose, and throat specialist with surgical expertise.", "fee": 175.00},
]

PATIENT_DATA = [
    {"name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-1001", "gender": "male", "blood_type": "A+", "dob": date(1985, 3, 15)},
    {"name": "Maria Garcia", "email": "maria.garcia@example.com", "phone": "+1-555-1002", "gender": "female", "blood_type": "B+", "dob": date(1990, 7, 22)},
    {"name": "David Lee", "email": "david.lee@example.com", "phone": "+1-555-1003", "gender": "male", "blood_type": "O-", "dob": date(1978, 11, 8)},
    {"name": "Sarah Wilson", "email": "sarah.wilson@example.com", "phone": "+1-555-1004", "gender": "female", "blood_type": "AB+", "dob": date(1995, 1, 30)},
    {"name": "Michael Johnson", "email": "michael.j@example.com", "phone": "+1-555-1005", "gender": "male", "blood_type": "A-", "dob": date(1982, 6, 12)},
]

def seed_doctors(db: Session):
    """Add dummy doctors to database"""
    print("\n🩺 Seeding doctors...")
    
    for doc in DOCTOR_DATA:
        # Check if doctor already exists
        existing = db.query(Doctor).filter(Doctor.email == doc["email"]).first()
        if existing:
            print(f"  ⏭️  Doctor {doc['name']} already exists, skipping...")
            continue
        
        # Create user account for doctor
        salt = generate_salt()
        hashed_password = get_password_hash("Doctor@123", salt)  # Default password
        
        user = User(
            email=doc["email"],
            name=doc["name"],
            hashed_password=hashed_password,
            salt=salt,
            role=UserRole.DOCTOR,
            is_verified=True,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.flush()  # Get the user ID
        
        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            name=doc["name"],
            email=doc["email"],
            phone=doc["phone"],
            specialization=doc["specialization"],
            bio=doc["bio"],
            consultation_fee=doc["fee"],
            license_number=f"LIC-{random.randint(100000, 999999)}",
            department=doc["specialization"],
            available_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            available_hours={"start": "09:00", "end": "17:00"},
            experience_years=random.randint(5, 20),
            qualifications=["MBBS", "MD"],
            is_available=True,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(doctor)
        print(f"  ✅ Added: {doc['name']} ({doc['specialization']})")
    
    db.commit()
    print(f"✅ Doctors seeded successfully!")


def seed_patients(db: Session):
    """Add dummy patients to database"""
    print("\n👥 Seeding patients...")
    
    for pat in PATIENT_DATA:
        # Check if patient already exists
        existing = db.query(Patient).filter(Patient.email == pat["email"]).first()
        if existing:
            print(f"  ⏭️  Patient {pat['name']} already exists, skipping...")
            continue
        
        # Create patient record (not linked to user account)
        patient = Patient(
            name=pat["name"],
            email=pat["email"],
            phone=pat["phone"],
            gender=pat["gender"],
            blood_type=pat["blood_type"],
            date_of_birth=pat["dob"],
            address="123 Main Street",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="+1-555-9999",
            medical_history="No significant medical history",
            allergies=["Penicillin"] if random.random() > 0.5 else [],
            status="active",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(patient)
        print(f"  ✅ Added: {pat['name']}")
    
    db.commit()
    print(f"✅ Patients seeded successfully!")


def seed_admin(db: Session):
    """Add admin user if not exists"""
    print("\n👑 Checking admin user...")
    
    admin_email = "admin@medisecure.com"
    existing = db.query(User).filter(User.email == admin_email).first()
    
    if existing:
        print(f"  ⏭️  Admin already exists")
        return
    
    salt = generate_salt()
    hashed_password = get_password_hash("Admin@123", salt)
    
    admin = User(
        email=admin_email,
        name="System Administrator",
        hashed_password=hashed_password,
        salt=salt,
        role=UserRole.ADMIN,
        is_verified=True,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(admin)
    db.commit()
    print(f"  ✅ Added admin: {admin_email}")


def main():
    print("=" * 50)
    print("🏥 MediSecure Database Seeder")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        seed_admin(db)
        seed_doctors(db)
        seed_patients(db)
        
        print("\n" + "=" * 50)
        print("✅ Database seeding completed!")
        print("=" * 50)
        print("\n📋 Default Credentials:")
        print("   Admin: admin@medisecure.com / Admin@123")
        print("   Doctors: [email] / Doctor@123")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
