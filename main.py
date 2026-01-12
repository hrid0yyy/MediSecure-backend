from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import users, auth, user_management, admin, appointments, prescriptions, messaging, billing
# Import from root middleware.py file
from middleware import setup_middleware
# Import from middleware folder files
import sys
sys.path.insert(0, "middleware")
from audit import AuditLoggingMiddleware
from security import SecurityHeadersMiddleware, RequestSizeLimitMiddleware
sys.path.remove("middleware")
from fastapi_limiter import FastAPILimiter
from config.redis_db import redis_client
from config.database import engine, Base


# Create tables (for development purposes)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await FastAPILimiter.init(redis_client)
    yield

app = FastAPI(
    title="MediSecure",
    description="Computer Security Project - Healthcare Data Management Platform",
    version="2.0.0",
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_request_size=10 * 1024 * 1024)  # 10 MB
app.add_middleware(AuditLoggingMiddleware)

# Include routers with versioning
app.include_router(auth.router)  # Keep auth at root for backward compatibility
app.include_router(user_management.router)  # New versioned user endpoints
app.include_router(admin.router)  # New versioned admin endpoints
app.include_router(users.router)  # Legacy endpoints

# New service routers
app.include_router(appointments.router)
app.include_router(prescriptions.router)
app.include_router(messaging.router)
app.include_router(billing.router)

@app.get("/")
async def root():
    """Root endpoint - returns welcome message"""
    return {
        "message": "Welcome to MediSecure!",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}

