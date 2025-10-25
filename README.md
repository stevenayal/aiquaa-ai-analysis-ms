# AIQUAA AI Analysis Microservice

**AI-powered test case generation and quality assurance analysis platform**

[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-green.svg)](https://swagger.io/specification/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](https://aiquaa.com/license)

## 🚀 Features

- **🤖 AI-Powered Analysis**: Generate comprehensive test cases using Google Gemini AI
- **📊 Coverage Analysis**: Automatic test coverage and gap analysis
- **🔗 Jira Integration**: Direct integration with Jira work items
- **📝 Confluence Integration**: Generate test plans for Confluence
- **🔒 PII Sanitization**: Automatic detection and sanitization of sensitive data
- **📈 Observability**: Full tracing with Langfuse integration
- **🌍 Multi-language Support**: English and Spanish parameters
- **📚 Complete OpenAPI/Swagger**: Production-ready API documentation

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [Testing](#testing)
- [OpenAPI Schema](#openapi-schema)

## 🏗️ Architecture

This microservice follows a **clean layered architecture**:

```
aiquaa-ai-analysis-ms/
├── apps/api/                   # API layer (FastAPI)
│   ├── main.py                # FastAPI app with OpenAPI config
│   ├── routes/v1/             # API endpoints by domain
│   ├── middleware/            # Custom middleware
│   └── deps/                  # Dependency injection
├── core/                      # Core utilities
│   ├── config/                # Centralized configuration
│   ├── logging/               # Structured logging
│   └── constants.py           # Application constants
├── domain/                    # Business logic layer
│   ├── models/                # Domain models
│   ├── services/              # Business services
│   └── errors/                # Domain exceptions
├── infrastructure/            # External dependencies
│   ├── ai/                    # Gemini AI & prompts
│   ├── http/                  # Jira HTTP client
│   ├── telemetry/             # Langfuse observability
│   └── sanitizer.py           # PII sanitization
├── schemas/                   # Pydantic models (API contracts)
│   ├── analysis.py
│   ├── jira.py
│   ├── confluence.py
│   └── common.py
├── scripts/                   # Automation scripts
├── deploy/                    # Deployment configs
├── docs/                      # Documentation & examples
└── tests/                     # Test suite

```

### Key Design Principles

✅ **Separation of Concerns**: Clear boundaries between layers
✅ **Dependency Injection**: Loosely coupled components
✅ **OpenAPI First**: Complete API documentation with examples
✅ **Type Safety**: Full Pydantic v2 validation
✅ **Observability**: Structured logging + Langfuse tracing

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Google API Key (for Gemini AI)
- Jira API Token (optional, for Jira integration)
- Langfuse account (optional, for observability)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/stevenayal/aiquaa-ai-analysis-ms.git
cd aiquaa-ai-analysis-ms
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application**:
```bash
# Using the dev script
chmod +x scripts/dev.sh
./scripts/dev.sh

# Or manually
python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the API**:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 📚 API Documentation

### OpenAPI/Swagger Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /docs` | **Swagger UI** - Interactive API documentation |
| `GET /redoc` | **ReDoc** - Alternative API documentation |
| `GET /openapi.json` | **OpenAPI Schema** - Machine-readable API spec |

### API Endpoints

#### Health & Diagnostics

- `GET /api/v1/salud` - Health check (no auth required)
- `GET /api/v1/diagnostico-llm` - LLM diagnostic (no auth required)

#### Analysis

- `POST /api/v1/analizar` - Analyze content and generate test cases
- `POST /api/v1/generar-pruebas-avanzadas` - Generate advanced ISTQB test cases

#### Jira Integration

- `POST /api/v1/analizar-jira` - Analyze Jira work item

#### Confluence Integration

- `POST /api/v1/analizar-jira-confluence` - Generate Confluence test plan

### Authentication

The API supports two authentication methods:

1. **API Key** (Header: `X-API-Key`)
2. **Bearer JWT** (Header: `Authorization: Bearer <token>`)

Health check endpoints are public (no authentication required).

### Example Requests

#### Analyze Content (English)
```bash
curl -X POST "http://localhost:8000/api/v1/analizar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "content": "As a user, I want to reset my password...",
    "content_type": "user_story",
    "analysis_level": "comprehensive"
  }'
```

#### Analyze Content (Spanish)
```bash
curl -X POST "http://localhost:8000/api/v1/analizar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "contenido": "Como usuario, quiero restablecer mi contraseña...",
    "tipo_contenido": "user_story",
    "nivel_analisis": "comprehensive"
  }'
```

#### Analyze Jira Work Item
```bash
curl -X POST "http://localhost:8000/api/v1/analizar-jira" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "work_item_id": "PROJ-123",
    "analysis_level": "detailed"
  }'
```

More examples available in `docs/examples/`.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (use `.env.example` as template):

```bash
# Application
APP_NAME=AIQUAA AI Analysis MS
ENVIRONMENT=development
DEBUG=true

# Google Gemini AI (Required)
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-pro

# Langfuse (Optional - for observability)
LANGFUSE_PUBLIC_KEY=your-public-key
LANGFUSE_SECRET_KEY=your-secret-key
LANGFUSE_ENABLED=true

# Jira (Optional - for Jira integration)
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_TOKEN=your-jira-api-token

# Feature Flags
USE_SPANISH_PARAMS=false
ENABLE_PII_SANITIZATION=true
ENABLE_RATE_LIMITING=true

# Security
SECRET_KEY=change-this-in-production
ALLOWED_API_KEYS=key1,key2,key3

# CORS
CORS_ORIGINS=http://localhost:3000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Configuration Management

All configuration is centralized in `core/config/settings.py` using Pydantic Settings:

- ✅ Type-safe configuration
- ✅ Automatic validation
- ✅ Environment variable parsing
- ✅ Default values
- ✅ Computed properties

## 🛠️ Development

### Project Structure

```
apps/api/          → FastAPI application & routes
core/              → Configuration, logging, constants
domain/            → Business logic & services
infrastructure/    → External clients (Gemini, Jira, Langfuse)
schemas/           → Pydantic models (request/response)
scripts/           → Development & automation scripts
tests/             → Test suite
```

### Development Scripts

```bash
# Start development server
./scripts/dev.sh

# Run linting
./scripts/lint.sh

# Run tests
./scripts/test.sh

# Generate OpenAPI schema
./scripts/gen-openapi.sh
```

### Code Quality

This project uses:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking (optional)
- **pytest** - Testing

Run all checks:
```bash
./scripts/lint.sh
```

## 🐳 Deployment

### Docker

Build and run with Docker:

```bash
# Build image
docker build -t aiquaa-ai-analysis:latest .

# Run container
docker run -p 8000:8000 --env-file .env aiquaa-ai-analysis:latest
```

### Docker Compose

Full stack with Redis, Nginx, Prometheus, Grafana:

```bash
cd deploy/docker
docker-compose up -d
```

Services:
- **API**: http://localhost:8000
- **Nginx**: http://localhost (reverse proxy)
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

### Kubernetes

Kubernetes manifests available in `deploy/k8s/`:

```bash
kubectl apply -f deploy/k8s/
```

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest

# With coverage
pytest --cov=apps --cov=core --cov=domain --cov=infrastructure

# Specific test file
pytest tests/unit/test_analysis_service.py

# With verbosity
pytest -v
```

Test structure:
```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
└── fixtures/          # Test fixtures & mocks
```

## 📄 OpenAPI Schema

### Generate OpenAPI Schema

```bash
# Using script
./scripts/gen-openapi.sh

# Manually
python -m apps.api.main --export-openapi docs/openapi/openapi.json
```

### Validate OpenAPI Schema

```bash
# Install validator
pip install openapi-spec-validator

# Validate
openapi-spec-validator docs/openapi/openapi.json
```

### CI/CD Validation

The GitHub Actions workflow automatically:
1. Generates OpenAPI schema
2. Validates schema with `openapi-spec-validator`
3. Tests endpoint availability (`/docs`, `/redoc`, `/openapi.json`)
4. Uploads schema as artifact

### OpenAPI Features

✅ Complete metadata (title, version, description, contact, license)
✅ Tags with descriptions and external documentation
✅ Security schemes (API Key + Bearer JWT)
✅ Multiple servers (local, production)
✅ Request/response examples
✅ Common error responses (400, 422, 429, 500)
✅ Swagger UI customization
✅ CLI export support

### Security Schemes

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### Standard Error Response

All errors follow this format:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid request data",
  "details": {
    "field": "content",
    "error": "Field required"
  }
}
```

Error codes:
- `VALIDATION_ERROR` - Invalid input (400/422)
- `NOT_FOUND` - Resource not found (404)
- `RATE_LIMIT_EXCEEDED` - Too many requests (429)
- `INTERNAL_SERVER_ERROR` - Server error (500)
- `EXTERNAL_SERVICE_ERROR` - External service failure

## 📊 Observability

### Structured Logging

All logs use structured JSON format with:
- `trace_id` - Request trace ID
- `timestamp` - ISO 8601 timestamp
- `level` - Log level
- `event` - Log event name
- `context` - Additional context

### Langfuse Tracing

When enabled, Langfuse provides:
- LLM call tracing
- Performance metrics
- Cost tracking
- Debug information

Access Langfuse dashboard: https://cloud.langfuse.com

### Metrics

Prometheus metrics available at `/metrics`:
- Request latency
- Request count by endpoint
- Error rates
- LLM call duration

## 🔒 Security

### Best Practices

✅ PII sanitization enabled by default
✅ API key authentication
✅ Rate limiting (60 req/min default)
✅ CORS configuration
✅ Input validation (Pydantic)
✅ Secrets via environment variables
✅ No secrets in logs/responses

### PII Sanitization

Automatically detects and sanitizes:
- Emails
- Phone numbers
- SSNs
- Credit cards
- IP addresses
- API keys
- Passwords
- JWT tokens

## 📝 License

Proprietary - Copyright © 2024 AIQUAA

## 🤝 Support

- **Email**: support@aiquaa.com
- **Documentation**: https://docs.aiquaa.com
- **Issues**: https://github.com/stevenayal/aiquaa-ai-analysis-ms/issues

---

**Made with ❤️ by the AIQUAA Team**

🤖 *Powered by Claude Code & Google Gemini AI*
