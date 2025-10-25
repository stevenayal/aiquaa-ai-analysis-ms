# Railway Deployment Fix - AIQUAA AI Analysis MS

## 🔧 Problema Identificado

El deployment en Railway estaba fallando con:
```
Attempt #1-7 failed with service unavailable
1/1 replicas never became healthy!
Healthcheck failed!
```

## 🛠️ Solución Implementada

### 1. **Dockerfile - Puerto Dinámico**

**Antes:**
```dockerfile
CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Después:**
```dockerfile
CMD ["/app/start.sh"]
```

**Cambios:**
- ✅ Usa script de inicio (`start.sh`) que soporta `$PORT` de Railway
- ✅ PYTHONPATH configurado a `/app`
- ✅ Healthcheck Docker deshabilitado (Railway usa su propio healthcheck)
- ✅ Comando en formato array para mejor manejo de señales

### 2. **Script de Inicio (`start.sh`)**

Nuevo archivo que:
- ✅ Verifica versión de Python
- ✅ Valida dependencias críticas (FastAPI, Pydantic, Uvicorn)
- ✅ Verifica que la app puede importarse
- ✅ Usa variable `$PORT` de Railway con fallback a 8000
- ✅ Warning si `GOOGLE_API_KEY` no está configurada
- ✅ Logs mejorados para debugging

### 3. **railway.json - Timeout Aumentado**

**Antes:**
```json
{
  "healthcheckTimeout": 100
}
```

**Después:**
```json
{
  "healthcheckTimeout": 300
}
```

**Razón:** La primera carga de dependencias (Google AI, Langfuse) puede tomar más tiempo.

### 4. **.dockerignore - Build Optimizado**

Nuevo archivo que excluye:
- ✅ Archivos de desarrollo (`test_*.py`, `scripts/`)
- ✅ Archivos legacy no necesarios
- ✅ Logs, data, venv
- ✅ Documentación excepto README
- ✅ Archivos IDE y Git

**Beneficio:** Build más rápido y imagen Docker más pequeña.

### 5. **Procfile & runtime.txt**

Archivos de soporte para Railway:

**Procfile:**
```
web: python -m uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT
```

**runtime.txt:**
```
python-3.11.9
```

## 📋 Checklist de Deployment

### Antes de Deploy:

- [x] Dockerfile actualizado con puerto dinámico
- [x] Script `start.sh` creado y ejecutable
- [x] `.dockerignore` creado
- [x] `railway.json` con timeout aumentado
- [x] Variables de entorno configuradas en Railway:
  - [ ] `GOOGLE_API_KEY` (REQUERIDA)
  - [ ] `GEMINI_MODEL=gemini-pro`
  - [ ] `ENVIRONMENT=production`
  - [ ] `DEBUG=false`
  - [ ] `LOG_LEVEL=INFO`
  - [ ] `LANGFUSE_PUBLIC_KEY` (Opcional)
  - [ ] `LANGFUSE_SECRET_KEY` (Opcional)
  - [ ] `JIRA_BASE_URL` (Opcional)
  - [ ] `JIRA_EMAIL` (Opcional)
  - [ ] `JIRA_TOKEN` (Opcional)

### Después de Deploy:

```bash
# 1. Verificar health check
curl https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/api/v1/salud

# Respuesta esperada:
{
  "status": "healthy",
  "timestamp": "2024-10-25T03:00:00Z",
  "version": "v1",
  "services": {
    "llm": "healthy",
    "jira": "not_configured",
    "langfuse": "not_configured"
  }
}

# 2. Verificar redirección a Swagger
curl -I https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/
# Debe retornar: Location: /docs

# 3. Acceder a Swagger UI
# https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/docs

# 4. Verificar OpenAPI Schema
curl https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/openapi.json

# 5. Ver logs en Railway
railway logs --follow
```

## 🐛 Troubleshooting

### Si el healthcheck sigue fallando:

**1. Verificar logs de Railway:**
```bash
railway logs
```

Buscar:
- ✅ "Starting AIQUAA AI Analysis MS..."
- ✅ "FastAPI: X.X.X"
- ✅ "App imported successfully"
- ✅ "Application startup complete"

**2. Verificar variables de entorno:**
```bash
railway variables
```

Debe mostrar `GOOGLE_API_KEY` configurada.

**3. Verificar que el servicio escucha en el puerto correcto:**
```bash
railway logs | grep "Uvicorn running"
```

Debe mostrar: `Uvicorn running on http://0.0.0.0:XXXX`

**4. Si falla la importación de `apps.api.main`:**

Verificar que todos los `__init__.py` existen:
```bash
find apps core domain infrastructure schemas -name "__init__.py"
```

**5. Si falla con "Module not found":**

Verificar que `PYTHONPATH=/app` está configurado en el Dockerfile.

### Errores Comunes:

| Error | Causa | Solución |
|-------|-------|----------|
| `service unavailable` | App no inicia o crashea | Ver logs con `railway logs` |
| `Module 'apps' not found` | PYTHONPATH incorrecto | Verificar Dockerfile tiene `ENV PYTHONPATH=/app` |
| `Google API key not configured` | Variable de entorno faltante | Configurar `GOOGLE_API_KEY` en Railway |
| `Port already in use` | Conflicto de puertos | Railway maneja esto automáticamente |

## 🎯 Comando de Deploy

```bash
# Push a GitHub (Railway auto-deploys)
git push origin main

# O deploy manual con Railway CLI
railway up

# Ver status
railway status

# Ver logs en tiempo real
railway logs --follow
```

## ✅ Verificación Final

Una vez deployado, verificar los siguientes endpoints:

```bash
BASE_URL="https://aiquaa-ai-analysis-ms-v2-production.up.railway.app"

# 1. Root (debe redirigir a /docs)
curl -L $BASE_URL/

# 2. Health check (debe retornar JSON)
curl $BASE_URL/api/v1/salud | jq

# 3. Swagger UI (debe retornar HTML)
curl -s $BASE_URL/docs | grep "Swagger UI"

# 4. ReDoc (debe retornar HTML)
curl -s $BASE_URL/redoc | grep "ReDoc"

# 5. OpenAPI Schema (debe retornar JSON válido)
curl $BASE_URL/openapi.json | jq .info
```

## 📊 Métricas Esperadas

Después del deploy exitoso:

- **Build Time**: ~10-30 segundos
- **Start Time**: ~5-10 segundos
- **Health Check**: Debe pasar en primer intento
- **Memory Usage**: ~150-300 MB
- **Response Time (/salud)**: <200ms

---

**Última actualización**: 2025-10-25
**Status**: ✅ Fixes implementados, listo para redeploy
