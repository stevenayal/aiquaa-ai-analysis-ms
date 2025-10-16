# ⚙️ Configuración Completa del Microservicio QA

Esta guía detalla todas las opciones de configuración disponibles para el microservicio.

## 🔧 Variables de Entorno

### Configuración Básica

```bash
# ==================== APLICACIÓN ====================
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
PORT=8000                        # Puerto del servidor
ENVIRONMENT=development          # development, staging, production
HOST=0.0.0.0                    # Host del servidor

# ==================== LANGFUSE ====================
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxx  # Clave pública de Langfuse
LANGFUSE_SECRET_KEY=sk-lf-xxxxx  # Clave secreta de Langfuse
LANGFUSE_HOST=https://cloud.langfuse.com  # URL de Langfuse
LANGFUSE_FLUSH_INTERVAL=10       # Intervalo de flush (segundos)
LANGFUSE_MAX_RETRIES=3           # Máximo reintentos

# ==================== JIRA ====================
JIRA_BASE_URL=https://domain.atlassian.net  # URL base de Jira
JIRA_TOKEN=your_token_here      # Token de autenticación
JIRA_ORG_ID=your_org_id         # ID de organización
JIRA_TIMEOUT=30                 # Timeout de requests (segundos)
JIRA_MAX_RETRIES=3              # Máximo reintentos

# ==================== GEMINI ====================
LLM_PROVIDER=gemini             # Proveedor de LLM
GOOGLE_API_KEY=your_api_key     # API Key de Google
GOOGLE_PROJECT_ID=your_project  # ID del proyecto Google
GEMINI_MODEL=gemini-pro         # Modelo a usar
GEMINI_TEMPERATURE=0.7          # Temperatura del modelo (0-1)
GEMINI_MAX_TOKENS=2048          # Máximo tokens de respuesta
GEMINI_TIMEOUT=60               # Timeout de requests (segundos)

# ==================== SEGURIDAD ====================
PII_SANITIZATION=true           # Habilitar sanitización PII
PII_LOG_LEVEL=INFO              # Nivel de log para PII
SECRET_MASKING=true             # Enmascarar secretos en logs
CORS_ORIGINS=*                  # Orígenes CORS permitidos

# ==================== CACHE ====================
REDIS_URL=redis://localhost:6379  # URL de Redis
CACHE_TTL=3600                  # TTL del cache (segundos)
CACHE_ENABLED=true              # Habilitar cache

# ==================== MONITOREO ====================
PROMETHEUS_ENABLED=true         # Habilitar métricas Prometheus
PROMETHEUS_PORT=9090            # Puerto de Prometheus
GRAFANA_ENABLED=true            # Habilitar Grafana
GRAFANA_PORT=3000               # Puerto de Grafana
```

## 🏗️ Configuración de Servicios

### Langfuse

#### Crear Cuenta y Proyecto
1. Ir a https://cloud.langfuse.com
2. Crear cuenta o iniciar sesión
3. Crear nuevo proyecto
4. Obtener claves de API

#### Configuración Avanzada
```python
# En llm_wrapper.py
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
    flush_at=10,  # Flush cada 10 requests
    flush_interval=10,  # Flush cada 10 segundos
    max_retries=3,
    timeout=30
)
```

### Jira

#### Obtener Token de API
1. Ir a https://id.atlassian.com/manage-profile/security/api-tokens
2. Crear nuevo token
3. Copiar token generado

#### Configuración de Permisos
El token necesita estos permisos:
- `read:jira-work`
- `write:jira-work`
- `manage:jira-project`

#### Configuración Avanzada
```python
# En tracker_client.py
jira_headers = {
    "Authorization": f"Bearer {self.jira_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Atlassian-Token": "no-check"  # Para requests de formulario
}
```

### Google Gemini

#### Obtener API Key
1. Ir a https://makersuite.google.com/app/apikey
2. Crear nueva API key
3. Configurar restricciones de uso

#### Configuración de Modelo
```python
# En llm_wrapper.py
generation_config = {
    "temperature": float(os.getenv("GEMINI_TEMPERATURE", 0.7)),
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": int(os.getenv("GEMINI_MAX_TOKENS", 2048)),
}
```

## 🔒 Configuración de Seguridad

### Sanitización de PII

#### Patrones Personalizados
```python
# En sanitizer.py
sanitizer.add_custom_pattern(
    name="custom_id",
    pattern=r'\b[A-Z]{2}\d{6}\b',
    replacement="[CUSTOM_ID_REDACTED]",
    category="custom"
)
```

#### Configuración de Logging Seguro
```python
# En main.py
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        sanitize_processor,  # Procesador personalizado
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
```

### CORS y Headers de Seguridad
```python
# En main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)
```

## 📊 Configuración de Monitoreo

### Prometheus

#### Configuración de Métricas
```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'qa-analysis'
    static_configs:
      - targets: ['qa-analysis:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

#### Métricas Personalizadas
```python
# En main.py
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')
```

### Grafana

#### Dashboard de QA Analysis
```json
{
  "dashboard": {
    "title": "QA Analysis Service",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      }
    ]
  }
}
```

## 🐳 Configuración de Docker

### Dockerfile Optimizado
```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY --chown=app:app . .

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose para Producción
```yaml
version: '3.8'

services:
  qa-analysis:
    build: .
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs:rw
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔄 Configuración de CI/CD

### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-cov
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Comandos de despliegue
```

## 🧪 Configuración de Testing

### Pytest Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

### Test Data
```python
# tests/fixtures.py
import pytest

@pytest.fixture
def sample_test_case():
    return {
        "test_case_id": "TC-001",
        "test_case_content": "Test case content",
        "project_key": "TEST",
        "priority": "High",
        "labels": ["test", "qa"]
    }

@pytest.fixture
def mock_llm_response():
    return {
        "suggestions": [
            {
                "type": "clarity",
                "title": "Test suggestion",
                "description": "Test description",
                "priority": "high",
                "category": "improvement"
            }
        ],
        "confidence_score": 0.85
    }
```

## 📈 Configuración de Performance

### Optimizaciones de FastAPI
```python
# En main.py
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(
    title="QA Analysis Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware de compresión
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Configuración de Uvicorn
```bash
# uvicorn.ini
[uvicorn]
host = 0.0.0.0
port = 8000
workers = 4
worker-class = uvicorn.workers.UvicornWorker
max-requests = 1000
max-requests-jitter = 100
timeout-keep-alive = 5
```

## 🔍 Configuración de Logging

### Logging Estructurado
```python
# En main.py
import structlog
from structlog.stdlib import LoggerFactory

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### Rotación de Logs
```python
# En main.py
import logging
from logging.handlers import RotatingFileHandler

# Configurar rotación de logs
handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setLevel(logging.INFO)
```

## 🚀 Configuración de Producción

### Checklist de Producción
- [ ] Variables de entorno configuradas
- [ ] HTTPS habilitado
- [ ] Logs centralizados
- [ ] Monitoreo configurado
- [ ] Backup de datos
- [ ] Health checks
- [ ] Rate limiting
- [ ] Autenticación/autorización
- [ ] Certificados SSL
- [ ] Firewall configurado

### Variables de Entorno de Producción
```bash
# .env.production
ENVIRONMENT=production
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8000

# Seguridad
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
SECRET_KEY=your-secret-key-here

# Base de datos (si se agrega)
DATABASE_URL=postgresql://user:pass@localhost/db

# Cache
REDIS_URL=redis://redis:6379/0

# Monitoreo
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

Esta configuración completa te permitirá desplegar el microservicio en cualquier entorno con la máxima flexibilidad y seguridad.
