#!/bin/bash
# Railway startup script for AIQUAA AI Analysis MS

set -e

echo "🚀 Starting AIQUAA AI Analysis MS..."
echo "Environment: ${ENVIRONMENT:-production}"
echo "Port: ${PORT:-8000}"

# Set Python path to include current directory
export PYTHONPATH="${PYTHONPATH}:/app"

# Verify Python version
python --version

# Verify critical dependencies
echo "📦 Verifying dependencies..."
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"

# Check if required environment variables are set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  WARNING: GOOGLE_API_KEY not set. LLM features will be unavailable."
fi

# Verify app can be imported
echo "🔍 Verifying app import..."
python -c "from apps.api.main import app; print('✅ App imported successfully')"

# Start the application
echo "🎯 Starting Uvicorn server..."
exec python -m uvicorn apps.api.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers 1 \
    --log-level "${LOG_LEVEL:-info}" \
    --no-access-log
