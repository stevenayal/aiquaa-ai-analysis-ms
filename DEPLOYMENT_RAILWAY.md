# Deployment en Railway - AIQUAA AI Analysis MS

## 🚀 Servidor de Producción

**URL**: https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/

**Características**:
- ✅ Redirección automática de `/` a `/docs` (Swagger UI)
- ✅ Health checks automáticos en `/api/v1/salud`
- ✅ Reinicio automático en caso de falla
- ✅ Variables de entorno seguras
- ✅ SSL/TLS habilitado por defecto

## 📋 Configuración Railway

### 1. Variables de Entorno Requeridas

Configure las siguientes variables en el dashboard de Railway:

```bash
# === REQUERIDAS ===

# Google Gemini AI
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-pro

# Aplicación
APP_NAME=AIQUAA AI Analysis MS
APP_VERSION=v1
ENVIRONMENT=production
DEBUG=false

# Servidor
HOST=0.0.0.0
PORT=${PORT}  # Railway proporciona esto automáticamente

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# === OPCIONALES ===

# Langfuse (Observabilidad)
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true

# Jira Integration
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_TOKEN=your-jira-api-token
JIRA_TIMEOUT=30

# Feature Flags
USE_SPANISH_PARAMS=false
ENABLE_PII_SANITIZATION=true
ENABLE_RATE_LIMITING=true

# Seguridad
SECRET_KEY=your-super-secret-key-change-in-production
ALLOWED_API_KEYS=key1,key2,key3

# CORS (Railway domain)
CORS_ORIGINS=https://aiquaa-ai-analysis-ms-v2-production.up.railway.app,https://aiquaa.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### 2. Configuración del Proyecto

Railway detecta automáticamente el `Dockerfile` y `railway.json`.

**railway.json** ya está configurado con:
- Builder: Dockerfile
- Start Command: `python -m uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`
- Health Check: `/api/v1/salud`
- Restart Policy: ON_FAILURE con 10 reintentos máximos

### 3. Despliegue

#### Opción A: Deploy desde GitHub (Recomendado)

1. Conectar repositorio GitHub a Railway
2. Railway detectará cambios automáticamente
3. Cada push a `main` despliega automáticamente

#### Opción B: Deploy desde Railway CLI

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Vincular proyecto
railway link

# Deploy
railway up
```

## 🔍 Verificación del Despliegue

### 1. Verificar Health Check

```bash
curl https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/api/v1/salud
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2024-10-24T10:30:00Z",
  "version": "v1",
  "services": {
    "llm": "healthy",
    "jira": "healthy",
    "langfuse": "healthy"
  }
}
```

### 2. Verificar Redirección a Swagger

```bash
# Acceder a la raíz
curl -L https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/

# Debe redirigir a /docs
```

### 3. Verificar OpenAPI Schema

```bash
curl https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/openapi.json
```

### 4. Probar Endpoint de Análisis

```bash
curl -X POST "https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/api/v1/analizar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "content": "As a user, I want to reset my password",
    "content_type": "user_story",
    "analysis_level": "detailed"
  }'
```

## 📊 Monitoreo

### Logs en Railway

```bash
# Ver logs en tiempo real
railway logs

# Ver logs con filtro
railway logs --filter error
```

### Métricas Disponibles

Railway proporciona automáticamente:
- ✅ CPU usage
- ✅ Memory usage
- ✅ Network traffic
- ✅ Request rate
- ✅ Response times

Accede a las métricas en: https://railway.app/project/[your-project-id]/metrics

## 🔒 Seguridad en Producción

### 1. Variables Secretas

**Nunca commits**:
- `GOOGLE_API_KEY`
- `LANGFUSE_SECRET_KEY`
- `JIRA_TOKEN`
- `SECRET_KEY`
- `ALLOWED_API_KEYS`

Usar Railway Secrets Management para todas las credenciales.

### 2. HTTPS/SSL

Railway proporciona SSL automáticamente para todos los subdominios `*.up.railway.app`.

### 3. Rate Limiting

Configurado por defecto a 60 requests/minuto. Ajustar según necesidad:

```bash
RATE_LIMIT_PER_MINUTE=120
```

### 4. PII Sanitization

Habilitado por defecto en producción:

```bash
ENABLE_PII_SANITIZATION=true
```

## 🐛 Troubleshooting

### Problema: "Application failed to start"

**Solución**:
1. Verificar logs: `railway logs`
2. Verificar variables de entorno (especialmente `GOOGLE_API_KEY`)
3. Verificar que `PORT` no esté hardcodeado

### Problema: "Health check failing"

**Solución**:
1. Verificar que `/api/v1/salud` retorna 200
2. Aumentar `healthcheckTimeout` en `railway.json`
3. Verificar conectividad con servicios externos (Gemini, Jira)

### Problema: "502 Bad Gateway"

**Solución**:
1. Verificar que la app escucha en `0.0.0.0:$PORT`
2. Verificar logs de startup
3. Verificar que el Dockerfile es correcto

### Problema: "CORS errors"

**Solución**:
Actualizar `CORS_ORIGINS` con el dominio de Railway:

```bash
CORS_ORIGINS=https://aiquaa-ai-analysis-ms-v2-production.up.railway.app
```

## 🔄 CI/CD Pipeline

### GitHub Actions con Railway

El workflow `.github/workflows/openapi-validation.yml` ya está configurado para:

1. ✅ Validar OpenAPI schema
2. ✅ Run linting
3. ✅ Run tests
4. ✅ Deploy automático a Railway (en push a `main`)

Railway se integra automáticamente con GitHub cuando vinculas el repositorio.

## 📈 Escalado

### Escalado Vertical

Railway permite escalar recursos:
- **Memory**: 512MB - 32GB
- **CPU**: 1 vCPU - 32 vCPUs

Configurar en Railway dashboard.

### Escalado Horizontal

Para múltiples instancias, considerar:
1. Redis para rate limiting compartido
2. Session storage compartido
3. Load balancing (Railway Pro)

## 🌐 Custom Domain (Opcional)

### Configurar dominio personalizado

1. Ir a Railway project settings
2. Agregar custom domain: `api.aiquaa.com`
3. Configurar DNS:
   ```
   Type: CNAME
   Name: api
   Value: aiquaa-ai-analysis-ms-v2-production.up.railway.app
   ```
4. Actualizar `servers` en `apps/api/main.py`

## 📞 Soporte

- **Railway Docs**: https://docs.railway.app/
- **Railway Discord**: https://discord.gg/railway
- **AIQUAA Support**: support@aiquaa.com

---

**Última actualización**: 2024-10-24
**Versión**: v1
