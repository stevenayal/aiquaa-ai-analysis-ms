# Microservicio de Análisis IA - AIQUAA

**Plataforma de generación de casos de prueba y análisis de calidad impulsada por IA**

[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-green.svg)](https://swagger.io/specification/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Licencia](https://img.shields.io/badge/Licencia-Propietaria-red.svg)](https://aiquaa.com/license)

## 🚀 Características

- **🤖 Análisis Impulsado por IA**: Genera casos de prueba completos usando Google Gemini AI
- **📊 Análisis de Cobertura**: Análisis automático de cobertura de pruebas y detección de brechas
- **🔗 Integración con Jira**: Integración directa con work items de Jira
- **📝 Integración con Confluence**: Genera planes de prueba para Confluence
- **🔒 Sanitización de PII**: Detección y sanitización automática de datos sensibles
- **📈 Observabilidad**: Trazabilidad completa con integración de Langfuse
- **🌍 Soporte Multi-idioma**: Parámetros en inglés y español
- **📚 OpenAPI/Swagger Completo**: Documentación API lista para producción

## 📋 Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Inicio Rápido](#inicio-rápido)
- [Documentación API](#documentación-api)
- [Configuración](#configuración)
- [Desarrollo](#desarrollo)
- [Despliegue](#despliegue)
- [Pruebas](#pruebas)
- [Esquema OpenAPI](#esquema-openapi)

## 🏗️ Arquitectura

Este microservicio sigue una **arquitectura limpia por capas**:

```
aiquaa-ai-analysis-ms/
├── apps/api/                   # Capa API (FastAPI)
│   ├── main.py                # App FastAPI con config OpenAPI
│   ├── routes/v1/             # Endpoints API por dominio
│   ├── middleware/            # Middleware personalizado
│   └── deps/                  # Inyección de dependencias
├── core/                      # Utilidades core
│   ├── config/                # Configuración centralizada
│   ├── logging/               # Logging estructurado
│   └── constants.py           # Constantes de aplicación
├── domain/                    # Capa de lógica de negocio
│   ├── models/                # Modelos de dominio
│   ├── services/              # Servicios de negocio
│   └── errors/                # Excepciones de dominio
├── infrastructure/            # Dependencias externas
│   ├── ai/                    # Gemini AI & prompts
│   ├── http/                  # Cliente HTTP Jira
│   ├── telemetry/             # Observabilidad Langfuse
│   └── sanitizer.py           # Sanitización PII
├── schemas/                   # Modelos Pydantic (contratos API)
│   ├── analysis.py
│   ├── jira.py
│   ├── confluence.py
│   └── common.py
├── scripts/                   # Scripts de automatización
├── deploy/                    # Configuraciones de despliegue
├── docs/                      # Documentación y ejemplos
└── tests/                     # Suite de pruebas
```

### Principios de Diseño Clave

✅ **Separación de Responsabilidades**: Límites claros entre capas
✅ **Inyección de Dependencias**: Componentes débilmente acoplados
✅ **OpenAPI Primero**: Documentación API completa con ejemplos
✅ **Type Safety**: Validación completa con Pydantic v2
✅ **Observabilidad**: Logging estructurado + trazabilidad Langfuse

## ⚡ Inicio Rápido

### Prerequisitos

- Python 3.11+
- Google API Key (para Gemini AI)
- Jira API Token (opcional, para integración Jira)
- Cuenta Langfuse (opcional, para observabilidad)

### Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/stevenayal/aiquaa-ai-analysis-ms.git
cd aiquaa-ai-analysis-ms
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar entorno**:
```bash
cp .env.example .env
# Editar .env con tu configuración
```

5. **Ejecutar la aplicación**:
```bash
# Usando el script de desarrollo
chmod +x scripts/dev.sh
./scripts/dev.sh

# O manualmente
python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Acceder a la API**:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Esquema OpenAPI**: http://localhost:8000/openapi.json

## 📚 Documentación API

### Endpoints OpenAPI/Swagger

| Endpoint | Descripción |
|----------|-------------|
| `GET /docs` | **Swagger UI** - Documentación interactiva de la API |
| `GET /redoc` | **ReDoc** - Documentación alternativa de la API |
| `GET /openapi.json` | **Esquema OpenAPI** - Especificación API legible por máquina |

### Endpoints de la API

#### Salud y Diagnósticos

- `GET /api/v1/salud` - Verificación de salud (sin autenticación)
- `GET /api/v1/diagnostico-llm` - Diagnóstico LLM (sin autenticación)

#### Análisis

- `POST /api/v1/analizar` - Analizar contenido y generar casos de prueba
- `POST /api/v1/generar-pruebas-avanzadas` - Generar casos de prueba ISTQB avanzados

#### Integración Jira

- `POST /api/v1/analizar-jira` - Analizar work item de Jira

#### Integración Confluence

- `POST /api/v1/analizar-jira-confluence` - Generar plan de pruebas para Confluence

### Autenticación

La API soporta dos métodos de autenticación:

1. **API Key** (Header: `X-API-Key`)
2. **Bearer JWT** (Header: `Authorization: Bearer <token>`)

Los endpoints de salud son públicos (no requieren autenticación).

### Ejemplos de Peticiones

#### Analizar Contenido (Español)
```bash
curl -X POST "http://localhost:8000/api/v1/analizar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key" \
  -d '{
    "contenido": "Como usuario, quiero restablecer mi contraseña para recuperar el acceso a mi cuenta si olvido mis credenciales...",
    "tipo_contenido": "user_story",
    "nivel_analisis": "comprehensive"
  }'
```

#### Analizar Contenido (Inglés)
```bash
curl -X POST "http://localhost:8000/api/v1/analizar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key" \
  -d '{
    "content": "As a user, I want to reset my password...",
    "content_type": "user_story",
    "analysis_level": "comprehensive"
  }'
```

#### Analizar Work Item de Jira
```bash
curl -X POST "http://localhost:8000/api/v1/analizar-jira" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key" \
  -d '{
    "id_work_item": "PROJ-123",
    "nivel_analisis": "detailed"
  }'
```

Más ejemplos disponibles en `docs/examples/`.

## ⚙️ Configuración

### Variables de Entorno

Crear un archivo `.env` (usar `.env.example` como plantilla):

```bash
# Aplicación
APP_NAME=AIQUAA AI Analysis MS
ENVIRONMENT=development
DEBUG=true

# Google Gemini AI (Requerido)
GOOGLE_API_KEY=tu-google-api-key-aqui
GEMINI_MODEL=gemini-pro

# Langfuse (Opcional - para observabilidad)
LANGFUSE_PUBLIC_KEY=tu-clave-publica
LANGFUSE_SECRET_KEY=tu-clave-secreta
LANGFUSE_ENABLED=true

# Jira (Opcional - para integración Jira)
JIRA_BASE_URL=https://tu-dominio.atlassian.net
JIRA_EMAIL=tu-email@ejemplo.com
JIRA_TOKEN=tu-jira-api-token

# Feature Flags
USE_SPANISH_PARAMS=false
ENABLE_PII_SANITIZATION=true
ENABLE_RATE_LIMITING=true

# Seguridad
SECRET_KEY=cambiar-esto-en-produccion
ALLOWED_API_KEYS=key1,key2,key3

# CORS
CORS_ORIGINS=http://localhost:3000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Gestión de Configuración

Toda la configuración está centralizada en `core/config/settings.py` usando Pydantic Settings:

- ✅ Configuración con type-safety
- ✅ Validación automática
- ✅ Parseo de variables de entorno
- ✅ Valores por defecto
- ✅ Propiedades computadas

## 🛠️ Desarrollo

### Estructura del Proyecto

```
apps/api/          → Aplicación FastAPI y rutas
core/              → Configuración, logging, constantes
domain/            → Lógica de negocio y servicios
infrastructure/    → Clientes externos (Gemini, Jira, Langfuse)
schemas/           → Modelos Pydantic (request/response)
scripts/           → Scripts de desarrollo y automatización
tests/             → Suite de pruebas
```

### Scripts de Desarrollo

```bash
# Iniciar servidor de desarrollo
./scripts/dev.sh

# Ejecutar linting
./scripts/lint.sh

# Ejecutar pruebas
./scripts/test.sh

# Generar esquema OpenAPI
./scripts/gen-openapi.sh
```

### Calidad de Código

Este proyecto usa:

- **Black** - Formateo de código
- **isort** - Ordenamiento de imports
- **flake8** - Linting
- **mypy** - Verificación de tipos (opcional)
- **pytest** - Testing

Ejecutar todas las verificaciones:
```bash
./scripts/lint.sh
```

## 🐳 Despliegue

### Docker

Construir y ejecutar con Docker:

```bash
# Construir imagen
docker build -t aiquaa-ai-analysis:latest .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env aiquaa-ai-analysis:latest
```

### Docker Compose

Stack completo con Redis, Nginx, Prometheus, Grafana:

```bash
cd deploy/docker
docker-compose up -d
```

Servicios:
- **API**: http://localhost:8000
- **Nginx**: http://localhost (reverse proxy)
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

### Kubernetes

Manifiestos de Kubernetes disponibles en `deploy/k8s/`:

```bash
kubectl apply -f deploy/k8s/
```

## 🧪 Pruebas

Ejecutar la suite de pruebas:

```bash
# Todas las pruebas
pytest

# Con cobertura
pytest --cov=apps --cov=core --cov=domain --cov=infrastructure

# Archivo de prueba específico
pytest tests/unit/test_analysis_service.py

# Con verbosidad
pytest -v
```

Estructura de pruebas:
```
tests/
├── unit/              # Pruebas unitarias
├── integration/       # Pruebas de integración
└── fixtures/          # Fixtures y mocks de prueba
```

## 📄 Esquema OpenAPI

### Generar Esquema OpenAPI

```bash
# Usando script
./scripts/gen-openapi.sh

# Manualmente
python -m apps.api.main --export-openapi docs/openapi/openapi.json
```

### Validar Esquema OpenAPI

```bash
# Instalar validador
pip install openapi-spec-validator

# Validar
openapi-spec-validator docs/openapi/openapi.json
```

### Validación CI/CD

El workflow de GitHub Actions automáticamente:
1. Genera el esquema OpenAPI
2. Valida el esquema con `openapi-spec-validator`
3. Prueba la disponibilidad de endpoints (`/docs`, `/redoc`, `/openapi.json`)
4. Sube el esquema como artefacto

### Características OpenAPI

✅ Metadatos completos (título, versión, descripción, contacto, licencia)
✅ Tags con descripciones y documentación externa
✅ Esquemas de seguridad (API Key + Bearer JWT)
✅ Múltiples servidores (local, producción)
✅ Ejemplos de request/response
✅ Respuestas de error comunes (400, 422, 429, 500)
✅ Personalización de Swagger UI
✅ Soporte de exportación por CLI

### Esquemas de Seguridad

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

### Respuesta de Error Estándar

Todos los errores siguen este formato:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Datos de solicitud inválidos",
  "details": {
    "field": "content",
    "error": "Campo requerido"
  }
}
```

Códigos de error:
- `VALIDATION_ERROR` - Entrada inválida (400/422)
- `NOT_FOUND` - Recurso no encontrado (404)
- `RATE_LIMIT_EXCEEDED` - Demasiadas solicitudes (429)
- `INTERNAL_SERVER_ERROR` - Error de servidor (500)
- `EXTERNAL_SERVICE_ERROR` - Fallo de servicio externo

## 📊 Observabilidad

### Logging Estructurado

Todos los logs usan formato JSON estructurado con:
- `trace_id` - ID de trazabilidad de la solicitud
- `timestamp` - Timestamp ISO 8601
- `level` - Nivel de log
- `event` - Nombre del evento de log
- `context` - Contexto adicional

### Trazabilidad Langfuse

Cuando está habilitado, Langfuse proporciona:
- Trazabilidad de llamadas LLM
- Métricas de rendimiento
- Seguimiento de costos
- Información de depuración

Acceder al dashboard de Langfuse: https://cloud.langfuse.com

### Métricas

Métricas de Prometheus disponibles en `/metrics`:
- Latencia de solicitudes
- Conteo de solicitudes por endpoint
- Tasas de error
- Duración de llamadas LLM

## 🔒 Seguridad

### Mejores Prácticas

✅ Sanitización de PII habilitada por defecto
✅ Autenticación por API key
✅ Rate limiting (60 req/min por defecto)
✅ Configuración CORS
✅ Validación de entrada (Pydantic)
✅ Secretos via variables de entorno
✅ Sin secretos en logs/respuestas

### Sanitización de PII

Detecta y sanitiza automáticamente:
- Emails
- Números de teléfono
- SSNs
- Tarjetas de crédito
- Direcciones IP
- API keys
- Contraseñas
- Tokens JWT

## 📝 Licencia

Propietaria - Copyright © 2024 AIQUAA

## 🤝 Soporte

- **Email**: support@aiquaa.com
- **Documentación**: https://docs.aiquaa.com
- **Issues**: https://github.com/stevenayal/aiquaa-ai-analysis-ms/issues

---

## 📖 Guía de Uso Rápida

### 1. Análisis Básico de Contenido

```bash
curl -X POST "http://localhost:8000/api/v1/analizar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key" \
  -d '{
    "contenido": "El sistema debe permitir a los usuarios iniciar sesión con email y contraseña",
    "tipo_contenido": "requirement",
    "nivel_analisis": "detailed"
  }'
```

**Respuesta**:
```json
{
  "id_contenido": "analysis_requirement_1729768200",
  "tipo_contenido": "requirement",
  "estado": "completed",
  "casos_prueba": [
    {
      "id": "TC-001",
      "title": "Verificar inicio de sesión exitoso con credenciales válidas",
      "description": "Probar que un usuario puede iniciar sesión con email y contraseña válidos",
      "steps": [
        "Navegar a la página de inicio de sesión",
        "Ingresar email válido",
        "Ingresar contraseña válida",
        "Hacer clic en el botón de iniciar sesión"
      ],
      "expected_result": "El usuario es redirigido al dashboard",
      "priority": "high",
      "category": "functional"
    }
  ],
  "analisis_cobertura": {
    "functional_coverage": 85.0,
    "edge_case_coverage": 60.0,
    "negative_test_coverage": 70.0
  },
  "puntuacion_confianza": 0.85,
  "tiempo_procesamiento": 12.5,
  "fecha_creacion": "2024-10-24T10:30:00Z"
}
```

### 2. Análisis de Work Item de Jira

```bash
curl -X POST "http://localhost:8000/api/v1/analizar-jira" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key" \
  -d '{
    "id_work_item": "PROJ-123",
    "nivel_analisis": "comprehensive"
  }'
```

### 3. Generación Avanzada con Técnicas ISTQB

```bash
curl -X POST "http://localhost:8000/api/v1/generar-pruebas-avanzadas" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key" \
  -d '{
    "requirement": "El sistema debe soportar autenticación OAuth 2.0",
    "strategies": [
      "equivalence_partitioning",
      "boundary_value",
      "decision_table"
    ],
    "include_istqb_format": true,
    "include_execution_plan": false
  }'
```

---

**Hecho con ❤️ por el Equipo AIQUAA**

🤖 *Impulsado por Claude Code & Google Gemini AI*
