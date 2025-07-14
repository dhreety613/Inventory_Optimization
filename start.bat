@echo off
REM Inventory Optimization System - Startup Script for Windows

echo 🚀 Starting Inventory Optimization System...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Please configure your environment variables.
    echo    Copy .env.example to .env and fill in your configuration.
    pause
    exit /b 1
)

REM Navigate to backend directory
cd backend

REM Start the FastAPI server
echo 🌐 Starting FastAPI server on http://localhost:8000
echo 📊 Access the dashboard at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn auth_api:app --reload --host 0.0.0.0 --port 8000
