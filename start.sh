#!/bin/bash

# Inventory Optimization System - Startup Script

echo "🚀 Starting Inventory Optimization System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/Scripts/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please configure your environment variables."
    echo "   Copy .env.example to .env and fill in your configuration."
    exit 1
fi

# Navigate to backend directory
cd backend

# Start the FastAPI server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📊 Access the dashboard at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn auth_api:app --reload --host 0.0.0.0 --port 8000
