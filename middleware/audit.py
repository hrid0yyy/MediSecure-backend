from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from models.audit import AuditLog
from config.database import SessionLocal
from datetime import datetime
import json

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests and responses for audit purposes.
    Captures user actions, IP addresses, and operation details.
    """
    
    SENSITIVE_PATHS = ["/auth/login", "/auth/signup", "/auth/reset-password"]
    EXCLUDE_PATHS = ["/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"]
    
    async def dispatch(self, request: Request, call_next):
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.EXCLUDE_PATHS):
            return await call_next(request)
        
        # Get request details
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        method = request.method
        path = request.url.path
        
        # Get user ID from request state (set by auth dependency)
        user_id = getattr(request.state, "user_id", None)
        
        # Process the request
        response = await call_next(request)
        
        # Determine action from path and method
        action = self._determine_action(method, path)
        
        # Determine status
        status = "SUCCESS" if 200 <= response.status_code < 400 else "FAILURE"
        
        # Log to database asynchronously (in a separate thread to avoid blocking)
        self._log_to_database(
            user_id=user_id,
            action=action,
            resource=self._extract_resource(path),
            ip_address=client_host,
            user_agent=user_agent,
            status=status,
            status_code=response.status_code,
            path=path,
            method=method
        )
        
        return response
    
    def _determine_action(self, method: str, path: str) -> str:
        """Determine the action type from HTTP method and path"""
        if "/login" in path:
            return "LOGIN"
        elif "/logout" in path:
            return "LOGOUT"
        elif "/signup" in path:
            return "SIGNUP"
        elif "/verify" in path:
            return "VERIFICATION"
        elif "/forgot-password" in path:
            return "PASSWORD_RESET_REQUEST"
        elif "/reset-password" in path:
            return "PASSWORD_RESET"
        elif "/change-password" in path:
            return "PASSWORD_CHANGE"
        elif method == "GET":
            return "READ"
        elif method == "POST":
            return "CREATE"
        elif method in ["PUT", "PATCH"]:
            return "UPDATE"
        elif method == "DELETE":
            return "DELETE"
        else:
            return method
    
    def _extract_resource(self, path: str) -> str:
        """Extract resource name from path"""
        parts = path.strip("/").split("/")
        if len(parts) > 0:
            # Return the first meaningful part (e.g., 'users', 'auth', 'admin')
            return parts[0] if parts[0] else "unknown"
        return "unknown"
    
    def _log_to_database(self, user_id, action, resource, ip_address, 
                        user_agent, status, status_code, path, method):
        """Log the audit entry to the database"""
        try:
            db = SessionLocal()
            
            details = {
                "method": method,
                "path": path,
                "status_code": status_code
            }
            
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else None,  # Limit length
                details=json.dumps(details),
                status=status,
                created_at=datetime.utcnow()
            )
            
            db.add(audit_log)
            db.commit()
        except Exception as e:
            print(f"Error logging audit entry: {e}")
        finally:
            db.close()


def log_audit_event(db: Session, user_id: int, action: str, resource: str, 
                   resource_id: str = None, ip_address: str = None, 
                   details: dict = None, status: str = "SUCCESS"):
    """
    Helper function to manually log audit events from anywhere in the application.
    
    Args:
        db: Database session
        user_id: ID of the user performing the action
        action: Type of action (e.g., "LOGIN", "DATA_EXPORT")
        resource: Resource being acted upon
        resource_id: ID of the specific resource
        ip_address: IP address of the request
        details: Additional details as a dictionary
        status: "SUCCESS" or "FAILURE"
    """
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=str(resource_id) if resource_id else None,
            ip_address=ip_address,
            details=json.dumps(details) if details else None,
            status=status,
            created_at=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Error in manual audit logging: {e}")
        db.rollback()
