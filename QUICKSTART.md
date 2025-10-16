# 🚀 Guía de Inicio Rápido

Esta guía te llevará paso a paso para configurar y ejecutar el Microservicio de Análisis QA.

## ⚡ Instalación en 5 minutos

### 1. Prerrequisitos
- Python 3.11+
- Git
- Cuenta en Langfuse
- Cuenta en Jira (opcional)
- API Key de Google Gemini

### 2. Clonar y Configurar
```bash
# Clonar repositorio
git clone <repository-url>
cd microservicio-analisis-qa

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tus credenciales
notepad .env
```

**Configuración mínima requerida:**
```bash
# Langfuse (REQUERIDO)
LANGFUSE_PUBLIC_KEY=pk-lf-tu-public-key
LANGFUSE_SECRET_KEY=sk-lf-tu-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com

# Gemini (REQUERIDO)
GOOGLE_API_KEY=tu-google-api-key
GEMINI_MODEL=gemini-pro

# App
LOG_LEVEL=INFO
PORT=8000
```

### 4. Ejecutar el Servicio
```bash
# Iniciar servidor de desarrollo
python -m uvicorn main:app --reload

# El servicio estará disponible en:
# http://localhost:8000
```

### 5. Verificar Instalación
```bash
# Health check
curl http://localhost:8000/health

# Abrir documentación interactiva
start http://localhost:8000/docs
```

## 🧪 Primer Análisis

### Usando la API Web
1. Abrir http://localhost:8000/docs
2. Expandir endpoint `POST /analyze`
3. Hacer clic en "Try it out"
4. Usar este ejemplo:

```json
{
  "test_case_id": "TC-001",
  "test_case_content": "Verificar que el usuario puede iniciar sesión con credenciales válidas. Pasos: 1) Ir a login 2) Ingresar email válido 3) Ingresar password válido 4) Hacer clic en Login. Resultado esperado: Usuario logueado exitosamente",
  "project_key": "TEST",
  "priority": "High",
  "labels": ["login", "authentication"]
}
```

### Usando cURL
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "test_case_id": "TC-001",
    "test_case_content": "Verificar login con credenciales válidas",
    "project_key": "TEST"
  }'
```

## 🔧 Configuración Avanzada

### Integración con Jira
```bash
# Agregar al .env
JIRA_BASE_URL=https://tu-dominio.atlassian.net
JIRA_TOKEN=tu-jira-token
JIRA_ORG_ID=tu-org-id
```

### Configuración de Logging
```bash
# Niveles disponibles: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=DEBUG

# Para desarrollo
ENVIRONMENT=development

# Para producción
ENVIRONMENT=production
```

## 🐳 Usando Docker

### Opción 1: Docker Compose (Recomendado)
```bash
# Ejecutar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f qa-analysis

# Detener servicios
docker-compose down
```

### Opción 2: Docker Individual
```bash
# Construir imagen
docker build -t qa-analysis .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env qa-analysis
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_main.py -v

# Con cobertura
pytest --cov=. --cov-report=html
```

### Test de Integración
```bash
# Test completo del flujo
python -c "
import asyncio
from main import analyze_test_case, TestCaseAnalysisRequest

async def test():
    request = TestCaseAnalysisRequest(
        test_case_id='TC-TEST',
        test_case_content='Test case content',
        project_key='TEST'
    )
    result = await analyze_test_case(request, None)
    print('Test passed:', result.status == 'completed')

asyncio.run(test())
"
```

## 📊 Monitoreo

### Verificar Salud del Sistema
```bash
# Health check completo
curl http://localhost:8000/health | jq

# Solo estado
curl http://localhost:8000/health | jq .status
```

### Logs en Tiempo Real
```bash
# Windows
Get-Content logs\app.log -Wait

# Linux/Mac
tail -f logs/app.log
```

## 🚨 Solución de Problemas

### Error: "Module not found"
```bash
# Verificar que el entorno virtual esté activo
which python
# Debe mostrar: .../venv/Scripts/python.exe

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error: "Connection refused"
```bash
# Verificar que el puerto esté libre
netstat -an | findstr :8000

# Cambiar puerto
set PORT=8001
python -m uvicorn main:app --reload --port 8001
```

### Error: "Invalid API key"
```bash
# Verificar variables de entorno
echo $GOOGLE_API_KEY
echo $LANGFUSE_PUBLIC_KEY

# Probar conexión a Gemini
python -c "
import google.generativeai as genai
genai.configure(api_key='tu-api-key')
print('Gemini connection OK')
"
```

### Error: "Langfuse connection failed"
```bash
# Verificar credenciales de Langfuse
python -c "
from langfuse import Langfuse
langfuse = Langfuse(public_key='tu-public-key', secret_key='tu-secret-key')
langfuse.flush()
print('Langfuse connection OK')
"
```

## 🎯 Próximos Pasos

1. **Configurar Jira**: Integrar con tu instancia de Jira
2. **Personalizar Prompts**: Modificar `prompt_templates.py`
3. **Agregar Tests**: Crear tests para tus casos específicos
4. **Configurar Monitoreo**: Configurar Grafana y Prometheus
5. **Desplegar**: Configurar para producción

## 📚 Recursos Adicionales

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación Langfuse](https://langfuse.com/docs)
- [API de Gemini](https://ai.google.dev/docs)
- [API de Jira](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)

## 🆘 Obtener Ayuda

- **Issues**: Crear issue en el repositorio
- **Discusiones**: Usar GitHub Discussions
- **Email**: contactar al equipo de desarrollo
- **Documentación**: Revisar `/docs` en la API
