from fastapi import FastAPI
from routers import users, auth
from middleware import setup_middleware
from fastapi_limiter import FastAPILimiter
from config.redis_db import redis_client
from config.database import engine, Base

# Create tables (for development purposes)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MediSecure",
    description="Computer Security Project",
    version="1.0.0"
)

setup_middleware(app)

@app.on_event("startup")
async def startup():
    await FastAPILimiter.init(redis_client)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
async def root():
    """Root endpoint - returns welcome message"""
    return {"message": "Welcome to MediSecure!", "docs": "/docs", "redoc": "/redoc"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

