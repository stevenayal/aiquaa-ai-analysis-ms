# Railway Troubleshooting Guide - AIQUAA AI Analysis MS

## 🔴 Error 502 Bad Gateway

**Síntomas:**
```
{"status":"error","code":502,"message":"Application failed to respond"}
```

### Diagnóstico Paso a Paso

#### 1. **Verificar que el deployment está activo**

En Railway dashboard:
- Ir a tu proyecto
- Verificar que el deployment esté en estado **"Active"** (verde)
- Si está en "Building" o "Failed", esperar o revisar logs de build

#### 2. **Verificar logs de Railway**

```bash
railway logs --tail 100
```

**Buscar errores comunes:**

```bash
# ❌ Error: GOOGLE_API_KEY not set
# Solución: Configurar variable en Railway dashboard

# ❌ Error: ModuleNotFoundError: No module named 'apps'
# Solución: Verificar PYTHONPATH=/app en Dockerfile

# ❌ Error: ImportError: cannot import name 'X'
# Solución: Verificar que todos los __init__.py existen

# ❌ Error: Port already in use
# Solución: Railway maneja esto automáticamente, reiniciar deployment
```

#### 3. **Verificar Variables de Entorno**

En Railway dashboard → Variables:

**MÍNIMAS REQUERIDAS para que la app inicie:**
```bash
✅ PORT (Railway lo asigna automáticamente)
✅ PYTHONPATH=/app (debe estar en Dockerfile)
```

**REQUERIDAS para funcionalidad completa:**
```bash
✅ GOOGLE_API_KEY=tu-api-key-aqui
✅ GEMINI_MODEL=gemini-pro
✅ ENVIRONMENT=production
✅ DEBUG=false
```

**Verificar en Railway CLI:**
```bash
railway variables
```

#### 4. **Verificar que la app puede iniciar localmente**

```bash
# Construir imagen Docker localmente
docker build -t aiquaa-test .

# Ejecutar con las mismas variables que Railway
docker run -p 8000:8000 \
  -e PORT=8000 \
  -e GOOGLE_API_KEY=tu-api-key \
  -e ENVIRONMENT=production \
  aiquaa-test

# Verificar que responde
curl http://localhost:8000/api/v1/salud
```

## 🔧 Soluciones Rápidas

### Solución 1: Redeploy Forzado

```bash
# Trigger redeploy manual
railway up --detach

# O en dashboard: "Deployments" → "..." → "Redeploy"
```

### Solución 2: Verificar Start Command

En Railway dashboard → Settings → Deploy:

**Start Command debe ser VACÍO** (Railway usa el CMD del Dockerfile)

Si tiene algo, borrarlo y hacer redeploy.

### Solución 3: Verificar Build

En Railway logs buscar:
```
✅ Build time: X seconds
✅ Starting AIQUAA AI Analysis MS...
✅ FastAPI: 0.109.0
✅ Pydantic: 2.5.3
✅ Uvicorn: 0.27.0
✅ App imported successfully
✅ Application startup complete
```

Si alguno falla, ese es el problema.

### Solución 4: Aumentar Memoria

Si la app crashea por memoria:

Railway dashboard → Settings → Resources:
- Aumentar Memory a 1GB o 2GB

### Solución 5: Verificar Healthcheck Path

Railway dashboard → Settings → Deploy:
- Healthcheck Path: `/api/v1/salud`
- Healthcheck Timeout: `300`

## 📋 Checklist de Verificación

Antes de contactar soporte, verificar:

- [ ] ✅ Build completado exitosamente
- [ ] ✅ Deployment en estado "Active"
- [ ] ✅ Variables de entorno configuradas
- [ ] ✅ GOOGLE_API_KEY presente y válida
- [ ] ✅ Logs no muestran errores críticos
- [ ] ✅ Puerto correcto (Railway asigna automáticamente)
- [ ] ✅ Start command vacío (usa Dockerfile CMD)
- [ ] ✅ Healthcheck path correcto

## 🧪 Test de Conectividad

```bash
BASE_URL="https://aiquaa-ai-analysis-ms-v2-production.up.railway.app"

# 1. Verificar que Railway responde (aunque sea con error)
curl -I $BASE_URL
# Debe retornar headers, no timeout

# 2. Verificar health endpoint
curl $BASE_URL/api/v1/salud
# Debe retornar JSON con status

# 3. Verificar Swagger
curl -I $BASE_URL/docs
# Debe retornar 200 OK

# 4. Verificar redirección
curl -I $BASE_URL/
# Debe retornar 307 con Location: /docs
```

## 🔍 Debugging Avanzado

### Habilitar Debug Logs

En Railway variables:
```bash
LOG_LEVEL=DEBUG
DEBUG=true
```

Redeploy y verificar logs:
```bash
railway logs --follow
```

### Verificar Importaciones

Crear endpoint de debug temporal en `main.py`:

```python
@app.get("/debug/info")
async def debug_info():
    """Debug endpoint - REMOVE IN PRODUCTION"""
    import sys
    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "path": sys.path,
        "env": {
            "GOOGLE_API_KEY": "***" if os.getenv("GOOGLE_API_KEY") else "NOT_SET",
            "PORT": os.getenv("PORT"),
            "PYTHONPATH": os.getenv("PYTHONPATH")
        }
    }
```

Acceder a: `https://your-app.railway.app/debug/info`

### Ejecutar Shell en Railway

```bash
railway run bash

# Dentro del contenedor:
python --version
python -c "from apps.api.main import app; print('OK')"
python -c "import fastapi; print(fastapi.__version__)"
```

## 📞 Contactar Soporte

Si después de todos estos pasos sigue fallando:

**Información a incluir:**

1. **Logs de Railway** (últimas 100 líneas):
```bash
railway logs --tail 100 > railway-logs.txt
```

2. **Variables de entorno** (ocultar secretos):
```bash
railway variables > variables.txt
# EDITAR Y REMOVER SECRETOS antes de compartir
```

3. **Build logs**:
- Railway dashboard → Deployments → Click en el deployment → "View Logs"

4. **Descripción del error**:
- Qué endpoint estás intentando acceder
- Qué error exacto recibes
- Qué pasos ya intentaste

**Canales de soporte:**
- Railway Discord: https://discord.gg/railway
- Railway Docs: https://docs.railway.app/
- AIQUAA Support: support@aiquaa.com

---

## ✅ Última Verificación

Si todo lo demás falla, verificar que el código local funciona:

```bash
# 1. Limpiar todo
rm -rf __pycache__ **/__pycache__

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Exportar variables
export GOOGLE_API_KEY=tu-api-key
export GEMINI_MODEL=gemini-pro

# 4. Ejecutar localmente
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000

# 5. Verificar
curl http://localhost:8000/api/v1/salud
```

Si funciona local pero no en Railway, el problema está en la configuración de Railway.

---

**Última actualización**: 2025-10-25
**Autor**: AIQUAA Team
