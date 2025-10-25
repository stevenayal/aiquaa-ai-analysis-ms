#!/bin/bash
# Linting and code quality checks

set -e

echo "🔍 Running linting and code quality checks..."

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Install dev dependencies if needed
echo "📦 Installing dev dependencies..."
pip install -q black isort flake8 mypy pylint 2>/dev/null || true

# Black - Code formatting
echo "🎨 Running Black (code formatter)..."
black --check apps/ core/ domain/ infrastructure/ schemas/ || {
    echo "❌ Black found formatting issues. Run 'black apps/ core/ domain/ infrastructure/ schemas/' to fix."
    BLACK_FAILED=1
}

# isort - Import sorting
echo "📦 Running isort (import sorter)..."
isort --check-only apps/ core/ domain/ infrastructure/ schemas/ || {
    echo "❌ isort found import sorting issues. Run 'isort apps/ core/ domain/ infrastructure/ schemas/' to fix."
    ISORT_FAILED=1
}

# flake8 - Linting
echo "🔍 Running flake8 (linter)..."
flake8 apps/ core/ domain/ infrastructure/ schemas/ --max-line-length=120 --extend-ignore=E203,W503 || {
    echo "❌ flake8 found linting issues."
    FLAKE8_FAILED=1
}

# mypy - Type checking
echo "🔬 Running mypy (type checker)..."
mypy apps/ core/ domain/ infrastructure/ schemas/ --ignore-missing-imports || {
    echo "⚠️  mypy found type issues (non-blocking)."
}

# Summary
echo ""
echo "========================================="
if [ -z "$BLACK_FAILED" ] && [ -z "$ISORT_FAILED" ] && [ -z "$FLAKE8_FAILED" ]; then
    echo "✅ All linting checks passed!"
    exit 0
else
    echo "❌ Some linting checks failed. Please fix the issues above."
    exit 1
fi
