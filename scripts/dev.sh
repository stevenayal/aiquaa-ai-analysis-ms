#!/bin/bash
# Development script for AIQUAA AI Analysis MS

set -e

echo "🚀 Starting AIQUAA AI Analysis MS in development mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created. Please configure your environment variables."
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "🎯 Starting FastAPI server..."
python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000 --log-level info

echo "✅ Development server started!"
echo "📖 Swagger UI: http://localhost:8000/docs"
echo "📘 ReDoc: http://localhost:8000/redoc"
echo "📄 OpenAPI Schema: http://localhost:8000/openapi.json"
