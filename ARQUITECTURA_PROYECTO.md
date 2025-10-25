# 🏗️ Arquitectura del Proyecto - API de Análisis QA

## 📋 Descripción General

Sistema de análisis de casos de prueba basado en IA que integra Jira, Confluence y modelos de lenguaje para generar planes de pruebas estructurados y casos de prueba automatizados.

## 🎯 Objetivos del Sistema

- **Análisis Inteligente**: Generar casos de prueba a partir de requerimientos
- **Integración Jira**: Obtener datos de work items automáticamente
- **Documentación Confluence**: Crear planes de pruebas estructurados
- **Estándares ISTQB**: Aplicar metodologías de testing reconocidas
- **Observabilidad**: Tracking completo con Langfuse

## 🏛️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Frontend/API)                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/HTTPS
┌─────────────────────▼───────────────────────────────────────────┐
│                    FASTAPI SERVER                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                ENDPOINTS EN ESPAÑOL                     │   │
│  │  • /analizar - Análisis de contenido                    │   │
│  │  • /analizar-jira - Análisis de Jira                    │   │
│  │  • /generar-pruebas-avanzadas - Generación avanzada     │   │
│  │  • /analisis/requisitos/verificacion-istqb - ISTQB     │   │
│  │  • /analizar-jira-confluence - Planes Confluence       │   │
│  │  • /analizar-jira-confluence-simple - Versión rápida   │   │
│  │  • /salud - Health check                               │   │
│  │  • /diagnostico-llm - Diagnóstico LLM                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    SERVICIOS CORE                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ LLM WRAPPER │  │TRACKER CLIENT│  │PROMPT TEMPLATES│         │
│  │             │  │             │  │             │             │
│  │ • Gemini    │  │ • Jira API  │  │ • Templates │             │
│  │ • Langfuse  │  │ • Auth      │  │ • Versiones │             │
│  │ • Tracking  │  │ • Queries   │  │ • Variables │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    SERVICIOS EXTERNOS                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   JIRA      │  │  CONFLUENCE │  │   GEMINI    │             │
│  │             │  │             │  │             │             │
│  │ • Issues    │  │ • Spaces    │  │ • AI Model  │             │
│  │ • Projects  │  │ • Pages     │  │ • Analysis  │             │
│  │ • Workflows │  │ • Content   │  │ • Generation│             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
ia-analisis/
├── 📄 main.py                          # Aplicación FastAPI principal
├── 📄 tracker_client.py                # Cliente para integración con Jira
├── 📄 llm_wrapper.py                   # Wrapper para modelos de IA
├── 📄 prompt_templates.py              # Plantillas de prompts versionadas
├── 📄 sanitizer.py                    # Sanitización de datos sensibles
├── 📄 requirements.txt                 # Dependencias del proyecto
├── 📄 Dockerfile                      # Imagen Docker
├── 📄 docker-compose.yml              # Orquestación de servicios
├── 📄 config.env                      # Variables de entorno
├── 📄 railway.env                     # Configuración para Railway
├── 📄 postman_collection_completa_espanol.json  # Colección Postman
├── 📄 postman_environment_confluence.json      # Variables Postman
├── 📄 test_*.py                       # Scripts de prueba
├── 📁 tests/                          # Tests unitarios
│   ├── test_main.py
│   └── test_tracker_client.py
└── 📄 ARQUITECTURA_PROYECTO.md        # Este archivo
```

## 🔧 Componentes Principales

### 1. **FastAPI Server** (`main.py`)
- **Framework**: FastAPI con documentación automática
- **Endpoints**: 8 endpoints en español
- **Validación**: Pydantic models para request/response
- **Middleware**: CORS, logging, error handling
- **Background Tasks**: Tracking asíncrono

### 2. **Tracker Client** (`tracker_client.py`)
- **Integración Jira**: Obtener work items y proyectos
- **Autenticación**: Token-based authentication
- **Queries**: JQL para búsquedas avanzadas
- **Health Check**: Verificación de conectividad

### 3. **LLM Wrapper** (`llm_wrapper.py`)
- **Modelo**: Google Gemini Pro
- **Tracking**: Integración con Langfuse
- **Análisis**: Procesamiento de requerimientos
- **Generación**: Casos de prueba estructurados

### 4. **Prompt Templates** (`prompt_templates.py`)
- **Versionado**: Templates versionados y mantenibles
- **Variables**: Sustitución dinámica de variables
- **Tipos**: Diferentes templates por tipo de análisis
- **Validación**: Verificación de templates

### 5. **Sanitizer** (`sanitizer.py`)
- **PII Removal**: Eliminación de datos personales
- **Sensitive Data**: Filtrado de información sensible
- **Compliance**: Cumplimiento de regulaciones
- **Logging**: Registro de sanitización

## 🌐 Endpoints de la API

### **Análisis de Contenido**
- **`POST /analizar`** - Análisis unificado de contenido
- **`POST /analizar-jira`** - Análisis de work items de Jira
- **`POST /generar-pruebas-avanzadas`** - Generación con técnicas avanzadas

### **Análisis Especializado**
- **`POST /analisis/requisitos/verificacion-istqb`** - Análisis ISTQB
- **`POST /analizar-jira-confluence`** - Planes de pruebas para Confluence
- **`POST /analizar-jira-confluence-simple`** - Versión simplificada

### **Monitoreo y Diagnóstico**
- **`GET /salud`** - Health check del servicio
- **`GET /diagnostico-llm`** - Diagnóstico del LLM
- **`GET /config`** - Configuración del servicio

## 🔄 Flujo de Datos

### **Análisis de Contenido**
```
Cliente → FastAPI → Prompt Templates → LLM Wrapper → Gemini → Langfuse
                ↓
            Sanitizer → Response → Cliente
```

### **Análisis de Jira**
```
Cliente → FastAPI → Tracker Client → Jira API → Work Item Data
                ↓
            Prompt Templates → LLM Wrapper → Gemini → Langfuse
                ↓
            Response → Cliente
```

### **Plan de Pruebas Confluence**
```
Cliente → FastAPI → Tracker Client → Jira API → Work Item Data
                ↓
            Prompt Templates → LLM Wrapper → Gemini → Langfuse
                ↓
            Confluence Content → Response → Cliente
```

## 🛠️ Tecnologías Utilizadas

### **Backend**
- **FastAPI**: Framework web moderno y rápido
- **Pydantic**: Validación de datos y serialización
- **asyncio**: Programación asíncrona
- **structlog**: Logging estructurado

### **IA y ML**
- **Google Gemini**: Modelo de lenguaje para análisis
- **Langfuse**: Observabilidad y tracking de LLM
- **Prompt Engineering**: Optimización de prompts

### **Integraciones**
- **Jira API**: Integración con Atlassian Jira
- **Confluence**: Generación de contenido estructurado
- **HTTP Client**: httpx para requests asíncronos

### **DevOps y Deployment**
- **Docker**: Containerización
- **Railway**: Plataforma de deployment
- **Environment Variables**: Configuración segura

## 🔐 Seguridad y Compliance

### **Sanitización de Datos**
- **PII Removal**: Eliminación automática de datos personales
- **Sensitive Data**: Filtrado de información sensible
- **Compliance**: Cumplimiento de regulaciones (LGPD, GDPR)

### **Autenticación**
- **Jira Token**: Autenticación con Jira
- **API Keys**: Claves seguras para servicios externos
- **Environment Variables**: Configuración segura

### **Logging y Monitoreo**
- **Structured Logging**: Logs estructurados con structlog
- **Langfuse Tracking**: Tracking completo de LLM
- **Health Checks**: Verificación de salud del sistema

## 📊 Modelos de Datos

### **Request Models**
- **AnalysisRequest**: Análisis de contenido
- **JiraAnalysisRequest**: Análisis de Jira
- **AdvancedTestGenerationRequest**: Generación avanzada
- **ConfluenceTestPlanRequest**: Planes de Confluence

### **Response Models**
- **AnalysisResponse**: Respuesta de análisis
- **JiraAnalysisResponse**: Respuesta de Jira
- **AdvancedTestGenerationResponse**: Respuesta avanzada
- **ConfluenceTestPlanResponse**: Respuesta de Confluence

### **Data Models**
- **TestCase**: Caso de prueba estructurado
- **Suggestion**: Sugerencia de mejora
- **TestPlanSection**: Sección del plan de pruebas
- **TestExecutionPhase**: Fase de ejecución

## 🧪 Testing y Calidad

### **Scripts de Prueba**
- **`test_todos_endpoints_espanol.py`**: Pruebas completas
- **`test_confluence_espanol.py`**: Pruebas de Confluence
- **`test_confluence_simple.py`**: Pruebas simplificadas
- **`test_endpoints_espanol_final.py`**: Pruebas finales

### **Colección Postman**
- **`postman_collection_completa_espanol.json`**: 16 requests
- **`postman_environment_confluence.json`**: Variables de entorno
- **Tests Automáticos**: Validación de respuestas

### **Tests Unitarios**
- **`tests/test_main.py`**: Tests de endpoints
- **`tests/test_tracker_client.py`**: Tests de cliente Jira

## 🚀 Deployment y Configuración

### **Variables de Entorno**
```bash
# Google AI
GOOGLE_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-pro

# Langfuse
LANGFUSE_PUBLIC_KEY=tu_public_key
LANGFUSE_SECRET_KEY=tu_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# Jira
JIRA_BASE_URL=https://tu-empresa.atlassian.net
JIRA_EMAIL=tu-email@empresa.com
JIRA_TOKEN=tu_token_aqui

# Configuración
ENVIRONMENT=production
PORT=8000
```

### **Docker**
```bash
# Construir imagen
docker build -t ia-analisis .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file config.env ia-analisis
```

### **Railway**
```bash
# Deploy automático desde GitHub
# Variables de entorno en Railway dashboard
# Health check en /salud
```

## 📈 Monitoreo y Observabilidad

### **Health Checks**
- **`/salud`**: Estado general del servicio
- **`/diagnostico-llm`**: Estado del LLM
- **`/config`**: Configuración del servicio

### **Logging**
- **Structured Logs**: Logs estructurados con contexto
- **Langfuse**: Tracking de LLM y análisis
- **Error Tracking**: Captura de errores y excepciones

### **Métricas**
- **Response Time**: Tiempo de respuesta por endpoint
- **Success Rate**: Tasa de éxito de requests
- **LLM Usage**: Uso y costos del LLM
- **Error Rate**: Tasa de errores por tipo

## 🔄 Flujo de Desarrollo

### **1. Desarrollo Local**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp config.env.example config.env

# Ejecutar servidor
python main.py
```

### **2. Testing**
```bash
# Ejecutar tests unitarios
python -m pytest tests/

# Ejecutar pruebas de endpoints
python test_todos_endpoints_espanol.py

# Probar con Postman
# Importar postman_collection_completa_espanol.json
```

### **3. Deployment**
```bash
# Deploy a Railway
git push origin main

# Verificar deployment
curl https://ia-analisis-production.up.railway.app/salud
```

## 🎯 Casos de Uso Principales

### **1. Análisis de Requerimientos**
- Input: Requerimiento de texto
- Output: Casos de prueba estructurados
- Beneficio: Automatización de diseño de pruebas

### **2. Análisis de Jira**
- Input: ID de work item
- Output: Casos de prueba basados en Jira
- Beneficio: Integración con flujo de trabajo existente

### **3. Planes de Pruebas**
- Input: Issue de Jira
- Output: Plan de pruebas para Confluence
- Beneficio: Documentación automática y estructurada

### **4. Análisis ISTQB**
- Input: Requerimiento
- Output: Análisis de calidad ISTQB
- Beneficio: Cumplimiento de estándares de testing

## 🔮 Roadmap y Mejoras Futuras

### **Corto Plazo**
- [ ] Cache de respuestas para mejorar performance
- [ ] Rate limiting para control de uso
- [ ] Métricas avanzadas de monitoreo
- [ ] Tests de carga y performance

### **Mediano Plazo**
- [ ] Integración con más herramientas (Azure DevOps, GitHub)
- [ ] Templates personalizables por organización
- [ ] Análisis de cobertura de pruebas
- [ ] Generación de reportes automáticos

### **Largo Plazo**
- [ ] Machine Learning para mejora continua
- [ ] Integración con CI/CD pipelines
- [ ] Análisis predictivo de riesgos
- [ ] Plataforma multi-tenant

## 📚 Documentación Adicional

### **Archivos de Configuración**
- **`requirements.txt`**: Dependencias Python
- **`Dockerfile`**: Configuración Docker
- **`docker-compose.yml`**: Orquestación local
- **`config.env`**: Variables de entorno

### **Scripts de Utilidad**
- **`test_*.py`**: Scripts de prueba y validación
- **`debug_*.py`**: Scripts de debugging
- **`ejemplo_*.py`**: Ejemplos de uso

### **Colecciones de Prueba**
- **Postman**: Colección completa con tests automáticos
- **Environment**: Variables de entorno para diferentes ambientes
- **Documentation**: Documentación interactiva en Swagger UI

---

## 🎉 Conclusión

Este sistema representa una **solución integral** para la automatización del análisis de casos de prueba, integrando las mejores prácticas de testing con tecnologías de IA modernas. La arquitectura modular y escalable permite adaptarse a diferentes necesidades organizacionales mientras mantiene la calidad y confiabilidad del sistema.

**Características Clave:**
- ✅ **Endpoints en español** para mejor UX
- ✅ **Integración completa** con Jira y Confluence
- ✅ **IA avanzada** con Google Gemini
- ✅ **Observabilidad** con Langfuse
- ✅ **Seguridad** con sanitización de datos
- ✅ **Escalabilidad** con arquitectura modular
- ✅ **Testing completo** con validación automática
