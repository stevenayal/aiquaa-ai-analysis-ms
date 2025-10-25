#!/bin/bash
# Generate OpenAPI schema

set -e

echo "📄 Generating OpenAPI schema..."

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Create docs directory if it doesn't exist
mkdir -p docs/openapi

# Export OpenAPI schema
echo "🔧 Exporting schema to docs/openapi/openapi.json..."
python -m apps.api.main --export-openapi docs/openapi/openapi.json

# Validate schema (optional - requires openapi-spec-validator)
if command -v openapi-spec-validator &> /dev/null; then
    echo "✅ Validating OpenAPI schema..."
    openapi-spec-validator docs/openapi/openapi.json && echo "✅ Schema is valid!" || echo "⚠️  Schema validation failed"
else
    echo "ℹ️  Install openapi-spec-validator to validate schema: pip install openapi-spec-validator"
fi

echo "✅ OpenAPI schema generated successfully!"
echo "📄 Location: docs/openapi/openapi.json"
echo "📖 View in Swagger Editor: https://editor.swagger.io/"
