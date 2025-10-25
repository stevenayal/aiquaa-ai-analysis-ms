#!/bin/bash
# Run tests

set -e

echo "🧪 Running tests..."

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Install test dependencies
pip install -q pytest pytest-asyncio pytest-cov pytest-mock

# Run tests with coverage
echo "🔬 Running pytest with coverage..."
pytest tests/ \
    -v \
    --cov=apps \
    --cov=core \
    --cov=domain \
    --cov=infrastructure \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-fail-under=70

echo "✅ Tests completed!"
echo "📊 Coverage report: htmlcov/index.html"
