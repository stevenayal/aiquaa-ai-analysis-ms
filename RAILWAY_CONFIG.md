# Configuración para Railway

## ✅ **Configuración Implementada**

### 🔧 **Configuración de FastAPI:**

1. **Servidores Configurados:**
   - Producción: `https://ia-analisis-production.up.railway.app`
   - Desarrollo: `http://localhost:8000`

2. **CORS Configurado:**
   - Orígenes permitidos: Railway, localhost, 127.0.0.1
   - Métodos: Todos (*)
   - Headers: Todos (*)
   - Credenciales: Habilitadas

3. **TrustedHostMiddleware:**
   - Hosts permitidos: `ia-analisis-production.up.railway.app`, `*.railway.app`
   - Localhost y 127.0.0.1 para desarrollo

4. **Endpoint Raíz:**
   - Redirige automáticamente a `/docs` (Swagger UI)

### 🚀 **Configuración del Servidor:**

1. **Puerto:** Usa la variable de entorno `PORT` (Railway la proporciona automáticamente)
2. **Host:** `0.0.0.0` (necesario para Railway)
3. **Reload:** Deshabilitado en producción (`RAILWAY_ENVIRONMENT=production`)
4. **Log Level:** Configurable via `LOG_LEVEL`

### 📋 **Variables de Entorno Requeridas en Railway:**

```bash
# Configuración básica
PORT=8000
LOG_LEVEL=info
RAILWAY_ENVIRONMENT=production

# Langfuse
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# Jira
JIRA_URL=your_jira_url
JIRA_USERNAME=your_jira_username
JIRA_API_TOKEN=your_jira_api_token

# Google Gemini
GOOGLE_API_KEY=your_google_api_key
```

### 🔗 **URLs de la API:**

- **Documentación Swagger:** `https://ia-analisis-production.up.railway.app/docs`
- **Documentación ReDoc:** `https://ia-analisis-production.up.railway.app/redoc`
- **OpenAPI JSON:** `https://ia-analisis-production.up.railway.app/openapi.json`
- **Health Check:** `https://ia-analisis-production.up.railway.app/health`

### 🎯 **Endpoints Disponibles:**

1. **`GET /`** - Redirige a la documentación
2. **`GET /health`** - Verificación de salud del servicio
3. **`POST /analyze`** - Análisis unificado de contenido
4. **`POST /analyze-jira`** - Análisis de work items de Jira
5. **`POST /generate-advanced-tests`** - Generación de casos avanzados

### 🛠️ **Configuración de Railway:**

1. **railway.json** creado con:
   - Builder: NIXPACKS
   - Start Command: `python main.py`
   - Health Check: `/health`
   - Timeout: 100 segundos
   - Restart Policy: ON_FAILURE

### ✅ **Verificación de Funcionamiento:**

1. **Swagger UI:** Debe funcionar correctamente en `https://ia-analisis-production.up.railway.app/docs`
2. **Try it out:** Debe usar la URL base de Railway automáticamente
3. **CORS:** Debe permitir requests desde el navegador
4. **Health Check:** Debe responder correctamente

### 🔍 **Troubleshooting:**

1. **Si Swagger no carga:** Verificar que la URL base esté configurada correctamente
2. **Si CORS falla:** Verificar que los orígenes estén en la lista de permitidos
3. **Si el servidor no inicia:** Verificar las variables de entorno en Railway
4. **Si los endpoints no responden:** Verificar el health check en Railway

### 📊 **Monitoreo:**

- **Logs:** Disponibles en el dashboard de Railway
- **Métricas:** CPU, memoria, red en tiempo real
- **Health Check:** Automático cada 30 segundos
- **Restart:** Automático en caso de fallo
