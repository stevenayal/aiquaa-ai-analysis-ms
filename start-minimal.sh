#!/bin/bash
# Minimal startup for Railway debugging

set -e

echo "🔍 MINIMAL RAILWAY STARTUP"
echo "=========================="

# Environment info
echo "Environment: ${ENVIRONMENT:-not-set}"
echo "Port: ${PORT:-not-set}"
echo "Python: $(python --version)"

# Set Python path
export PYTHONPATH=/app

# Working directory
echo "Working dir: $(pwd)"
echo "Files: $(ls -la | head -10)"

# Verify minimal app can import
echo ""
echo "Testing import..."
python -c "from apps.api.main_minimal import app; print('✅ Minimal app imports OK')" || {
    echo "❌ Import failed, trying direct import..."
    python -c "import sys; sys.path.insert(0, '/app'); from apps.api.main_minimal import app; print('✅ Direct import OK')"
}

# Start minimal app
echo ""
echo "🚀 Starting minimal Uvicorn..."
exec python -m uvicorn apps.api.main_minimal:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --log-level info
