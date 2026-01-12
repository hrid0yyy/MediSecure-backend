from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime

class AuditLog(Base):
    """
    Audit log table to track all important operations in the system.
    Stores who did what, when, and from where.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for system operations
    action = Column(String(100), nullable=False)  # e.g., "LOGIN", "LOGOUT", "PASSWORD_CHANGE", "USER_UPDATE"
    resource = Column(String(100), nullable=True)  # e.g., "users", "medical_records"
    resource_id = Column(String(100), nullable=True)  # ID of the affected resource
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    details = Column(Text, nullable=True)  # Additional JSON or text details
    status = Column(String(20), nullable=False)  # "SUCCESS" or "FAILURE"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", backref="audit_logs")

class PasswordHistory(Base):
    """
    Password history table to prevent password reuse.
    Stores hashed passwords to compare against new passwords.
    """
    __tablename__ = "password_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hashed_password = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", backref="password_history")
