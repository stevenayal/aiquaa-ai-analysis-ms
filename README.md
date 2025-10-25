# 🤖 API de Análisis QA con IA

Sistema de análisis automatizado de casos de prueba que integra Jira, Confluence y modelos de IA para generar planes de pruebas estructurados y casos de prueba automatizados.

## 🚀 Quick Start

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp config.env.example config.env
# Editar config.env con tus credenciales

# 3. Iniciar servicio
python main.py

# 4. Abrir documentación
# http://localhost:8000/docs
```

## 🌐 Endpoints Principales

### **Análisis de Contenido**
- **`POST /analizar`** - Análisis unificado de contenido
- **`POST /analizar-jira`** - Análisis de work items de Jira
- **`POST /generar-pruebas-avanzadas`** - Generación con técnicas avanzadas

### **Análisis Especializado**
- **`POST /analisis/requisitos/verificacion-istqb`** - Análisis ISTQB
- **`POST /analizar-jira-confluence`** - Planes de pruebas para Confluence
- **`POST /analizar-jira-confluence-simple`** - Versión simplificada (recomendada)

### **Monitoreo**
- **`GET /salud`** - Health check del servicio
- **`GET /diagnostico-llm`** - Diagnóstico del LLM

## 🔧 Configuración

### Variables de Entorno Requeridas
```bash
# Google AI (REQUERIDA)
GOOGLE_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-pro

# Langfuse (Opcional)
LANGFUSE_PUBLIC_KEY=tu_public_key
LANGFUSE_SECRET_KEY=tu_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# Jira (Opcional)
JIRA_BASE_URL=https://tu-empresa.atlassian.net
JIRA_EMAIL=tu-email@empresa.com
JIRA_TOKEN=tu_token_aqui
```

## 🧪 Testing

### Scripts de Prueba
```bash
# Pruebas completas
python test_todos_endpoints_espanol.py

# Pruebas de Confluence
python test_confluence_espanol.py

# Pruebas simplificadas
python test_confluence_simple.py
```

### Postman
- Importar `postman_collection_completa_espanol.json`
- Configurar variables en `postman_environment_confluence.json`

## 🐳 Docker

```bash
# Construir imagen
docker build -t ia-analisis .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file config.env ia-analisis
```

## 🚀 Deployment

### Railway
```bash
# Deploy automático desde GitHub
# Configurar variables de entorno en Railway dashboard
```

## 📊 Monitoreo

- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/salud
- **Diagnóstico LLM**: http://localhost:8000/diagnostico-llm

## 🔒 Seguridad

- **Sanitización PII**: Eliminación automática de datos personales
- **Variables de Entorno**: Configuración segura
- **Logging Estructurado**: Logs seguros con structlog

## 📚 Documentación

- **[ARQUITECTURA_PROYECTO.md](ARQUITECTURA_PROYECTO.md)** - Arquitectura completa del sistema
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentación de la API
- **[ISTQB_DOCUMENTATION.md](ISTQB_DOCUMENTATION.md)** - Metodologías ISTQB
- **[SECURITY.md](SECURITY.md)** - Políticas de seguridad

## 🎯 Características Principales

- ✅ **Endpoints en español** para mejor UX
- ✅ **Integración completa** con Jira y Confluence
- ✅ **IA avanzada** con Google Gemini
- ✅ **Observabilidad** con Langfuse
- ✅ **Seguridad** con sanitización de datos
- ✅ **Testing completo** con validación automática
- ✅ **Solución a timeouts** con endpoint simplificado

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
- Revisar documentación en `/docs`
- Consultar [ARQUITECTURA_PROYECTO.md](ARQUITECTURA_PROYECTO.md) para detalles técnicos