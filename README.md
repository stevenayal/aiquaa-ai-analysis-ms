# 🤖 Microservicio de Análisis QA con Técnicas ISTQB

Análisis automatizado de casos de prueba con técnicas ISTQB Foundation Level, observabilidad completa usando FastAPI, Langfuse y Gemini.

## 🚀 Quick Start

```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy config.env .env
# Editar .env con tus credenciales (NUNCA subir credenciales reales al repositorio)

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
- 🎯 **ISTQB** - Técnicas de diseño de pruebas Foundation Level

## 🔒 Seguridad

**IMPORTANTE**: Este proyecto NO incluye credenciales reales por seguridad.

### Variables de Entorno Requeridas:
- `GOOGLE_API_KEY` - API key de Google Gemini (REQUERIDA)
- `GEMINI_MODEL` - Modelo de Gemini (por defecto: gemini-1.5-flash)

### Variables Opcionales:
- `LANGFUSE_PUBLIC_KEY` - Para observabilidad
- `LANGFUSE_SECRET_KEY` - Para observabilidad  
- `JIRA_BASE_URL` - Para integración con Jira
- `JIRA_TOKEN` - Token de Jira
- `JIRA_ORG_ID` - ID de organización de Jira

### Para Railway:
Ver [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) para configuración completa.

## 🔗 Endpoints Principales

### 🎯 Generación ISTQB (NUEVO)
```http
POST /generate-istqb-tests
Content-Type: application/json

{
  "programa": "SISTEMA_AUTH",
  "dominio": "Autenticación de usuarios con validación de credenciales",
  "modulos": ["AUTORIZACION", "VALIDACION", "AUDITORIA"],
  "factores": {
    "TIPO_USUARIO": ["ADMIN", "USER", "GUEST"],
    "ESTADO_CREDENCIAL": ["VALIDA", "INVALIDA", "EXPIRADA"]
  },
  "limites": {
    "CAMPO_USUARIO_len": {"min": 1, "max": 64},
    "REINTENTOS": 3
  },
  "reglas": [
    "R1: si TIPO_USUARIO=ADMIN y ESTADO_CREDENCIAL=VALIDA -> ACCESO_TOTAL"
  ],
  "tecnicas": {
    "equivalencia": true,
    "valores_limite": true,
    "tabla_decision": true
  },
  "cantidad_max": 150
}
```

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

### Análisis de Requerimientos
```http
POST /analyze-requirements
Content-Type: application/json

{
  "requirement_id": "REQ-001",
  "requirement_content": "El sistema debe permitir...",
  "project_key": "PROJ",
  "test_types": ["functional", "integration"],
  "coverage_level": "high"
}
```

### Integración Jira
```http
POST /analyze-jira-workitem
Content-Type: application/json

{
  "work_item_id": "PROJ-123",
  "project_key": "PROJ",
  "test_types": ["functional", "ui"],
  "coverage_level": "medium"
}
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
- [ISTQB_DOCUMENTATION.md](ISTQB_DOCUMENTATION.md) - **NUEVO**: Documentación completa del sistema ISTQB
- [ejemplo_istqb_usage.py](ejemplo_istqb_usage.py) - **NUEVO**: Ejemplos prácticos de uso

## 🎯 Técnicas ISTQB Implementadas

### Técnicas de Diseño de Pruebas
1. **Equivalencia** - Partición de clases de equivalencia válidas/inválidas
2. **Valores Límite** - Análisis de casos min-1, min, min+1, max-1, max, max+1
3. **Tabla de Decisión** - Matrices compactas de condiciones y acciones
4. **Transición de Estados** - Estados y transiciones principales del sistema
5. **Árbol de Clasificación** - Clases/atributos y restricciones entre factores
6. **Pairwise** - Combinaciones mínimas que cubren todas las parejas
7. **Casos de Uso** - Flujos principales y alternos relevantes
8. **Error Guessing** - Hipótesis de fallos del dominio
9. **Checklist** - Verificación genérica de calidad

### Formato de Salida Estructurado
- **Sección A**: CSV con casos de prueba (CP - NNN - PROGRAMA - MODULO - CONDICION - ESCENARIO)
- **Sección B**: Fichas detalladas con precondiciones y resultados esperados
- **Sección C**: Artefactos técnicos según técnicas seleccionadas
- **Sección D**: Plan de ejecución automatizado (opcional)

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
