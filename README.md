# 🤖 Microservicio de Análisis QA con Langfuse

Análisis automatizado de casos de prueba con observabilidad completa usando FastAPI, Langfuse y Gemini.

## 🚀 Quick Start

```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy .env.example .env
# Editar .env con tus credenciales

# 4. Iniciar servicio
python -m uvicorn main:app --reload

# 5. Abrir API Docs
start http://localhost:8000/docs
```

## 📊 Stack Tecnológico

- ✅ **FastAPI** - Framework web moderno y rápido
- ✅ **Langfuse** - Observabilidad y tracking de LLM
- ✅ **Jira** - Integración con sistema de issues
- ✅ **Gemini** - Modelo de lenguaje de Google
- ✅ **Pydantic** - Validación de datos
- ✅ **Structlog** - Logging estructurado
- ✅ **Docker** - Containerización

## 🔗 Endpoints Principales

### Análisis de Casos de Prueba
```http
POST /analyze
Content-Type: application/json

{
  "test_case_id": "TC-001",
  "test_case_content": "Descripción del caso de prueba...",
  "project_key": "PROJ",
  "priority": "High",
  "labels": ["test", "qa"]
}
```

### Análisis en Lote
```http
POST /batch-analyze
Content-Type: application/json

[
  {
    "test_case_id": "TC-001",
    "test_case_content": "Caso 1...",
    "project_key": "PROJ"
  },
  {
    "test_case_id": "TC-002", 
    "test_case_content": "Caso 2...",
    "project_key": "PROJ"
  }
]
```

### Health Check
```http
GET /health
```

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│  Langfuse       │    │  Jira API       │
│   (main.py)     │    │  (Observabilidad)│    │  (Tracker)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         │
┌─────────────────┐    ┌─────────────────┐
│  Gemini LLM     │    │  PII Sanitizer  │
│  (Análisis)     │    │  (Seguridad)    │
└─────────────────┘    └─────────────────┘
```

## 📁 Estructura del Proyecto

```
microservicio-analisis-qa/
├── main.py                 # Aplicación FastAPI principal
├── tracker_client.py       # Cliente para Jira/Redmine
├── llm_wrapper.py         # Wrapper para LLM con Langfuse
├── prompt_templates.py    # Plantillas de prompts versionadas
├── sanitizer.py           # Sanitizador de PII
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Imagen Docker
├── docker-compose.yml    # Orquestación de servicios
├── .env.example          # Variables de entorno ejemplo
├── tests/                # Tests unitarios
│   ├── test_main.py
│   └── test_tracker_client.py
├── monitoring/           # Configuración de monitoreo
│   ├── prometheus/
│   └── grafana/
└── nginx/               # Configuración de proxy
```

## 🔧 Configuración

### Variables de Entorno Requeridas

```bash
# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com

# Jira
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_TOKEN=your_token_here
JIRA_ORG_ID=your_org_id_here

# Gemini
GOOGLE_API_KEY=your_key_here
GOOGLE_PROJECT_ID=your_project_id_here
GEMINI_MODEL=gemini-pro

# App
LOG_LEVEL=INFO
PORT=8000
ENVIRONMENT=development
```

## 🐳 Docker

### Construir y ejecutar
```bash
# Construir imagen
docker build -t qa-analysis .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env qa-analysis

# O usar docker-compose
docker-compose up -d
```

### Servicios incluidos
- **qa-analysis**: Aplicación principal
- **redis**: Cache y cola de mensajes
- **nginx**: Proxy reverso
- **prometheus**: Métricas
- **grafana**: Dashboards

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=.

# Tests específicos
pytest tests/test_main.py
```

## 📊 Monitoreo

### Dashboards Disponibles
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Langfuse**: https://us.cloud.langfuse.com

### Métricas Principales
- Latencia de análisis
- Tasa de éxito/error
- Uso de tokens LLM
- Calidad de sugerencias

## 🔒 Seguridad

### Sanitización de PII
El sistema incluye sanitización automática de:
- Emails
- Números de teléfono
- SSNs
- Tarjetas de crédito
- Direcciones IP
- URLs
- API Keys
- Tokens JWT

### Logging Seguro
- Logs estructurados en JSON
- Sanitización automática de datos sensibles
- Rotación de logs configurable

## 🚀 Despliegue

### Producción
1. Configurar variables de entorno de producción
2. Usar HTTPS con certificados válidos
3. Configurar backup de logs y métricas
4. Implementar health checks
5. Configurar alertas

### Escalabilidad
- Horizontal: Múltiples instancias con load balancer
- Vertical: Aumentar recursos del contenedor
- Cache: Redis para respuestas frecuentes
- Queue: Procesamiento asíncrono de lotes

## 📚 Documentación Adicional

- [QUICKSTART.md](QUICKSTART.md) - Guía de inicio rápido
- [CONFIGURACION_COMPLETA.md](CONFIGURACION_COMPLETA.md) - Configuración detallada
- [ALTERNATIVAS_LLM.md](ALTERNATIVAS_LLM.md) - Alternativas de modelos LLM

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch
3. Commit cambios
4. Push al branch
5. Crear Pull Request

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Para soporte técnico:
- Crear issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar documentación en `/docs`
