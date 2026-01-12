from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from config.database import get_db
from models.user import User, UserDevice
from models.audit import AuditLog, PasswordHistory
from models.profile import UserProfile
from schemas.user import UserResponse, UserUpdate, ChangePasswordRequest
from utils.security import get_current_user, verify_password, get_password_hash, generate_salt
from utils.sanitization import InputSanitizer, sanitize_user_input
from utils.encryption import encrypt_sensitive_data, decrypt_sensitive_data
import sys
sys.path.insert(0, "middleware")
from audit import log_audit_event
sys.path.remove("middleware")

router = APIRouter(prefix="/api/v1/users", tags=["User Management"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile information.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_verified=current_user.is_verified
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    """
    try:
        # Sanitize input
        if user_update.email:
            user_update.email = InputSanitizer.sanitize_email(user_update.email)
            
            # Check if email is already taken
            existing_user = db.query(User).filter(
                User.email == user_update.email,
                User.id != current_user.id
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            current_user.email = user_update.email
            current_user.is_verified = False  # Require re-verification
        
        db.commit()
        db.refresh(current_user)
        
        # Log audit event
        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="UPDATE",
            resource="users",
            resource_id=str(current_user.id),
            ip_address=request.client.host if request.client else None,
            details={"fields_updated": ["email"] if user_update.email else []},
            status="SUCCESS"
        )
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            role=current_user.role,
            is_verified=current_user.is_verified
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.delete("/me")
async def delete_current_user_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete current user's account.
    """
    try:
        # Soft delete - mark as inactive instead of actually deleting
        # In a real system, you'd add an 'is_active' or 'deleted_at' column
        
        # For now, we'll log the deletion attempt
        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="DELETE",
            resource="users",
            resource_id=str(current_user.id),
            ip_address=request.client.host if request.client else None,
            details={"account_deletion_requested": True},
            status="SUCCESS"
        )
        
        # TODO: Implement actual soft delete with is_active column
        # current_user.is_active = False
        # current_user.deleted_at = datetime.utcnow()
        # db.commit()
        
        return {"message": "Account deletion requested. Contact support to complete the process."}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )


@router.get("/me/devices")
async def get_user_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all devices associated with current user.
    """
    devices = db.query(UserDevice).filter(UserDevice.user_id == current_user.id).all()
    
    return {
        "devices": [
            {
                "id": device.id,
                "fingerprint_hash": device.fingerprint_hash[:16] + "...",  # Show partial hash
                "last_login": device.last_login.isoformat() if device.last_login else None,
                "created_at": device.created_at.isoformat() if device.created_at else None
            }
            for device in devices
        ]
    }


@router.delete("/me/devices/{device_id}")
async def remove_user_device(
    device_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a specific device from current user's trusted devices.
    """
    device = db.query(UserDevice).filter(
        UserDevice.id == device_id,
        UserDevice.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    db.delete(device)
    db.commit()
    
    # Log audit event
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        resource="devices",
        resource_id=str(device_id),
        ip_address=request.client.host if request.client else None,
        details={"device_removed": True},
        status="SUCCESS"
    )
    
    return {"message": "Device removed successfully"}


@router.post("/me/change-password")
async def change_password(
    password_change: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    Requires current password for verification.
    Implements password history check to prevent reuse.
    """
    # Verify current password
    if not verify_password(
        password_change.current_password,
        current_user.hashed_password,
        current_user.salt
    ):
        # Log failed attempt
        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="PASSWORD_CHANGE",
            resource="users",
            resource_id=str(current_user.id),
            ip_address=request.client.host if request.client else None,
            details={"reason": "incorrect_current_password"},
            status="FAILURE"
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    if len(password_change.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Check password history (prevent reuse of last 5 passwords)
    password_history = db.query(PasswordHistory).filter(
        PasswordHistory.user_id == current_user.id
    ).order_by(PasswordHistory.created_at.desc()).limit(5).all()
    
    for old_password in password_history:
        if verify_password(
            password_change.new_password,
            old_password.hashed_password,
            old_password.salt
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reuse recent passwords"
            )
    
    # Save old password to password_history table
    old_password_entry = PasswordHistory(
        user_id=current_user.id,
        hashed_password=current_user.hashed_password,
        salt=current_user.salt,
        created_at=datetime.utcnow()
    )
    db.add(old_password_entry)
    
    # Generate new salt and hash
    new_salt = generate_salt()
    new_hashed_password = get_password_hash(password_change.new_password, new_salt)
    
    # Update password
    current_user.hashed_password = new_hashed_password
    current_user.salt = new_salt
    
    db.commit()
    
    # Log successful password change
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="PASSWORD_CHANGE",
        resource="users",
        resource_id=str(current_user.id),
        ip_address=request.client.host if request.client else None,
        details={"password_changed": True},
        status="SUCCESS"
    )
    
    return {"message": "Password changed successfully"}


@router.get("/me/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile with decrypted sensitive information.
    """
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        return {"message": "Profile not found. Please create a profile."}
    
    # Decrypt sensitive fields
    sensitive_fields = [
        'first_name', 'last_name', 'date_of_birth', 'phone', 'address',
        'medical_record_number', 'insurance_number',
        'emergency_contact_name', 'emergency_contact_phone'
    ]
    
    profile_data = {
        "id": profile.id,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "date_of_birth": profile.date_of_birth,
        "phone": profile.phone,
        "address": profile.address,
        "medical_record_number": profile.medical_record_number,
        "insurance_number": profile.insurance_number,
        "blood_type": profile.blood_type,
        "emergency_contact_name": profile.emergency_contact_name,
        "emergency_contact_phone": profile.emergency_contact_phone,
        "profile_picture_url": profile.profile_picture_url,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
    }
    
    # Decrypt sensitive data
    decrypted_data = decrypt_sensitive_data(profile_data, sensitive_fields)
    
    return decrypted_data


@router.post("/me/profile")
async def create_or_update_profile(
    profile_data: dict,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update current user's profile.
    Automatically encrypts sensitive PII fields.
    """
    # Sanitize input data
    profile_data = sanitize_user_input(profile_data)
    
    # Define sensitive fields to encrypt
    sensitive_fields = [
        'first_name', 'last_name', 'date_of_birth', 'phone', 'address',
        'medical_record_number', 'insurance_number',
        'emergency_contact_name', 'emergency_contact_phone'
    ]
    
    # Encrypt sensitive data
    encrypted_data = encrypt_sensitive_data(profile_data, sensitive_fields)
    
    # Check if profile exists
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    if profile:
        # Update existing profile
        for key, value in encrypted_data.items():
            if hasattr(profile, key) and key != 'id':
                setattr(profile, key, value)
        profile.updated_at = datetime.utcnow()
    else:
        # Create new profile
        profile = UserProfile(
            user_id=current_user.id,
            **encrypted_data
        )
        db.add(profile)
    
    db.commit()
    
    # Log the action
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="PROFILE_UPDATE",
        resource="user_profiles",
        resource_id=str(profile.id),
        ip_address=request.client.host if request.client else None,
        status="SUCCESS"
    )
    
    return {"message": "Profile saved successfully", "profile_id": profile.id}
