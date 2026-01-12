@echo off
echo Starting MediSecure Backend...
echo.

echo [1/2] Starting Redis container...
docker start d59f8abe87858e71f425285e8ab10b8f73d3af979a81fe2b7ba1a9093ab2d440
if %ERRORLEVEL% NEQ 0 (
    echo Failed to start Redis container
    pause
    exit /b 1
)
echo Redis container started successfully!
echo.

echo [2/2] Starting FastAPI server...
echo Server will be available at http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
