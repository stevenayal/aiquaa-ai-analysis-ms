# 📚 Documentación de la API de Análisis QA

## 🚀 Inicio Rápido

### 1. Levantar el Servidor

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp config.env .env
# Editar .env con tus credenciales

# Ejecutar el servidor
python main.py
```

### 2. Acceder a la Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📋 Endpoints Disponibles

### Información del Servicio

#### `GET /`
Obtiene información básica del microservicio.

**Respuesta:**
```json
{
  "message": "Microservicio de Análisis QA",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### `GET /health`
Verifica el estado de salud de todos los componentes.

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T19:16:44.520862",
  "version": "1.0.0",
  "components": {
    "langfuse": "healthy",
    "jira": "healthy",
    "llm": "healthy"
  }
}
```

### Análisis de Casos de Prueba

#### `POST /analyze`
Analiza un caso de prueba individual y genera sugerencias de mejora.

**Request Body:**
```json
{
  "test_case_id": "TC-001",
  "test_case_content": "Verificar que el usuario pueda iniciar sesión con credenciales válidas. Pasos: 1) Abrir la página de login, 2) Ingresar usuario válido, 3) Ingresar contraseña válida, 4) Hacer clic en 'Iniciar Sesión'. Resultado esperado: Usuario logueado exitosamente y redirigido al dashboard.",
  "project_key": "TEST",
  "priority": "High",
  "labels": ["login", "authentication", "smoke-test"]
}
```

**Response:**
```json
{
  "test_case_id": "TC-001",
  "analysis_id": "analysis_TC001_1760825804",
  "status": "completed",
  "suggestions": [
    {
      "type": "clarity",
      "title": "Definir datos de prueba específicos",
      "description": "El caso de prueba debe incluir datos específicos de usuario y contraseña",
      "priority": "high",
      "category": "improvement"
    }
  ],
  "confidence_score": 0.85,
  "processing_time": 8.81,
  "created_at": "2025-10-18T19:16:44.520862"
}
```

#### `POST /batch-analyze`
Analiza múltiples casos de prueba en una sola petición.

**Request Body:**
```json
[
  {
    "test_case_id": "TC-001",
    "test_case_content": "Verificar login con credenciales válidas",
    "project_key": "TEST",
    "priority": "High",
    "labels": ["login"]
  },
  {
    "test_case_id": "TC-002",
    "test_case_content": "Verificar logout del usuario",
    "project_key": "TEST",
    "priority": "Medium",
    "labels": ["logout"]
  }
]
```

#### `GET /analysis/{analysis_id}`
Obtiene el resultado de un análisis específico por ID.

## 🧪 Pruebas con Postman

### 1. Importar Colección

1. Abre Postman
2. Haz clic en "Import"
3. Selecciona el archivo `postman_collection.json`
4. Importa el archivo `postman_environment.json`

### 2. Configurar Variables

Las variables están preconfiguradas:
- `base_url`: http://localhost:8000
- `analysis_id`: ID de análisis de ejemplo
- `test_case_id`: ID de caso de prueba de ejemplo
- `project_key`: Clave del proyecto de ejemplo

### 3. Ejecutar Pruebas

1. **Información del Servicio**: Verifica que el servidor esté funcionando
2. **Estado de Salud**: Comprueba el estado de todos los componentes
3. **Analizar Caso de Prueba**: Prueba diferentes tipos de casos de prueba
4. **Análisis en Lote**: Prueba el procesamiento de múltiples casos

## 🔧 Configuración

### Variables de Entorno Requeridas

```env
# Servidor
PORT=8000
LOG_LEVEL=INFO

# Langfuse (Observabilidad)
LANGFUSE_PUBLIC_KEY=pk-lf-68cd9e76-1769-4ea8-99c6-06cd43f942ed
LANGFUSE_SECRET_KEY=sk-lf-fd683a67-6ff3-4216-aaed-1956a2798453
LANGFUSE_HOST=https://us.cloud.langfuse.com

# Google Gemini
GOOGLE_API_KEY=AIzaSyAWRoXr18XDdpA8tALdmqBlH9zBMUNuNFw
GEMINI_MODEL=gemini-2.0-flash

# Jira
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_TOKEN=ATCTT3xFfGN0c3dETJjiWzxKErcfV8-DXD8yrdGPvyo_YOxMR6i6ASScKoDGVCbFRBSMHGFRsJu0a1VlB4o7OK01kq1dCaQgabwfSohsjiGzJOaWHcQL8n1xslWYPBkqd1JgzkVM_oE5TkfxakmmZA_3uQpIiMewToOAsynN9x5qeP8FJPMy7nM=DA95D797
JIRA_ORG_ID=2ecbde5d-e040-4d64-a723-b53ef1ef34a2
```

## 📊 Tipos de Sugerencias

### Clarity (Claridad)
- Mejoras en legibilidad y comprensión
- Definición de datos de prueba específicos
- Detallado de pasos de prueba

### Coverage (Cobertura)
- Sugerencias para mejorar cobertura de pruebas
- Casos de error adicionales
- Casos límite (edge cases)

### Automation (Automatización)
- Optimizaciones para automatización
- Herramientas recomendadas
- Mejores prácticas de automatización

### Best Practice (Mejores Prácticas)
- Convenciones de nomenclatura
- Estructura de casos de prueba
- Mantenibilidad a largo plazo

## 🚨 Códigos de Error

- **400**: Datos de entrada inválidos
- **404**: Recurso no encontrado
- **500**: Error interno del servidor

## 📈 Monitoreo

### Langfuse
- Trazas de análisis en tiempo real
- Métricas de rendimiento
- Logs estructurados

### Logs
- Formato JSON estructurado
- Niveles: INFO, WARNING, ERROR
- Timestamps en formato ISO

## 🔗 Enlaces Útiles

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Estado de Salud**: http://localhost:8000/health
- **Colección Postman**: `postman_collection.json`
- **Variables Postman**: `postman_environment.json`
