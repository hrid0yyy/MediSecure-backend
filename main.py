from fastapi import FastAPI


app = FastAPI(
    title="MediSecure",
    description="Computer Security Project",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint - returns welcome message"""
    return {"message": "Welcome to MediSecure!", "docs": "/docs", "redoc": "/redoc"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

