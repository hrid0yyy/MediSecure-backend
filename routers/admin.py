from fastapi import APIRouter, Depends, HTTPException, status, Query
import sys
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from config.database import get_db
from models.user import User, UserDevice, UserRole
from models.audit import AuditLog
from schemas.user import UserResponse
from utils.security import get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


def get_admin_user(current_user: User = Depends(get_current_user)):
    """Dependency to check if current user is an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    verified: Optional[bool] = Query(None, description="Filter by verification status"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of all users (admin only).
    Supports filtering by role and verification status.
    """
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if verified is not None:
        query = query.filter(User.is_verified == verified)
    
    users = query.offset(skip).limit(limit).all()
    
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            is_verified=user.is_verified
        )
        for user in users
    ]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get specific user details by ID (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_verified=user.is_verified
    )


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a user's role (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    user.role = new_role
    db.commit()
    
    return {"message": f"User role updated to {new_role.value}"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user account (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Delete related devices first
    db.query(UserDevice).filter(UserDevice.user_id == user_id).delete()
    
    # Delete user
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    status: Optional[str] = Query(None, description="Filter by status (SUCCESS/FAILURE)"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated audit logs (admin only).
    Supports filtering by user, action, and status.
    """
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action.upper())
    
    if status:
        query = query.filter(AuditLog.status == status.upper())
    
    # Order by most recent first
    query = query.order_by(desc(AuditLog.created_at))
    
    total = query.count()
    logs = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource": log.resource,
                "resource_id": log.resource_id,
                "ip_address": log.ip_address,
                "status": log.status,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }


@router.get("/stats")
async def get_dashboard_stats(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics (admin only).
    Returns counts of users, devices, and recent activity.
    """
    # Total users count
    total_users = db.query(func.count(User.id)).scalar()
    
    # Verified users count
    verified_users = db.query(func.count(User.id)).filter(User.is_verified == True).scalar()
    
    # Users by role
    users_by_role = db.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()
    
    # Total devices
    total_devices = db.query(func.count(UserDevice.id)).scalar()
    
    # Recent audit logs (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_actions = db.query(func.count(AuditLog.id)).filter(
        AuditLog.created_at >= yesterday
    ).scalar()
    
    # Failed login attempts (last 24 hours)
    failed_logins = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "LOGIN",
        AuditLog.status == "FAILURE",
        AuditLog.created_at >= yesterday
    ).scalar()
    
    return {
        "users": {
            "total": total_users,
            "verified": verified_users,
            "by_role": {role.value: count for role, count in users_by_role}
        },
        "devices": {
            "total": total_devices
        },
        "activity_last_24h": {
            "total_actions": recent_actions,
            "failed_logins": failed_logins
        }
    }


@router.get("/audit-logs/user/{user_id}")
async def get_user_audit_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific user (admin only).
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    query = db.query(AuditLog).filter(AuditLog.user_id == user_id)
    query = query.order_by(desc(AuditLog.created_at))
    
    total = query.count()
    logs = query.offset(skip).limit(limit).all()
    
    return {
        "user_id": user_id,
        "user_email": user.email,
        "total": total,
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "resource": log.resource,
                "ip_address": log.ip_address,
                "status": log.status,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }
