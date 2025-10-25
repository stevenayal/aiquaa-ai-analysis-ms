# Railway Quick Fix - App Minimal para Debug

## 🚨 Problema Actual

La app completa no inicia en Railway (502 Bad Gateway). Necesitamos identificar el problema.

## ✅ Solución: Deploy App Minimal

### Paso 1: Cambiar a Dockerfile Minimal

En Railway Dashboard:
1. Ve a **Settings** → **Deploy**
2. En **Dockerfile Path**, cambiar de:
   ```
   Dockerfile
   ```
   a:
   ```
   Dockerfile.minimal
   ```
3. Click en **Save**

### Paso 2: Trigger Redeploy

Hacer commit y push:

```bash
git add -A
git commit -m "debug: Add minimal app for Railway troubleshooting"
git push origin feat/layered-architecture-openapi
```

O en Railway Dashboard:
- **Deployments** → **"..."** → **Redeploy**

### Paso 3: Verificar Minimal App

Una vez deployado:

```bash
# Health check
curl https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/api/v1/salud

# Debe retornar:
{
  "status": "healthy",
  "message": "Minimal app running successfully"
}

# Debug info
curl https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/debug

# Swagger (redirección desde /)
curl -L https://aiquaa-ai-analysis-ms-v2-production.up.railway.app/
```

## 🔍 ¿Qué hace la App Minimal?

**Dockerfile.minimal**:
- ✅ Solo instala FastAPI, Uvicorn, Pydantic (dependencias mínimas)
- ✅ Solo copia `apps/` (no toda la aplicación)
- ✅ Build en ~10 segundos

**main_minimal.py**:
- ✅ FastAPI simple sin dependencias complejas
- ✅ Redirección `/` → `/docs` ✅
- ✅ Health check en `/api/v1/salud`
- ✅ Debug endpoint en `/debug`

**start-minimal.sh**:
- ✅ Logs de diagnóstico
- ✅ Verifica Python e imports
- ✅ Inicia Uvicorn con puerto dinámico

## 📊 Diagnóstico con App Minimal

### Si la App Minimal FUNCIONA ✅

**Problema**: La app completa tiene un error en imports o inicialización.

**Solución**: Revisar logs de build completo para encontrar el error específico.

**Pasos siguientes**:
1. Verificar que todos los `__init__.py` existen
2. Revisar imports en `apps/api/main.py`
3. Verificar que `infrastructure/`, `domain/`, `core/` se copian correctamente
4. Agregar dependencias una por una

### Si la App Minimal NO FUNCIONA ❌

**Problema**: Configuración de Railway incorrecta.

**Revisar**:
- [ ] ¿El puerto está correcto en los logs? (`Uvicorn running on http://0.0.0.0:XXXX`)
- [ ] ¿El healthcheck path es `/api/v1/salud`?
- [ ] ¿Hay suficiente memoria? (mínimo 512MB)
- [ ] ¿La variable `PORT` se está pasando correctamente?

## 🔄 Volver a la App Completa

Una vez que la app minimal funcione:

1. **Cambiar Dockerfile Path de vuelta**:
   ```
   Dockerfile
   ```

2. **Asegurar que tenemos las variables de entorno**:
   ```bash
   GOOGLE_API_KEY=tu-api-key-aqui
   GEMINI_MODEL=gemini-pro
   ENVIRONMENT=production
   DEBUG=false
   ```

3. **Redeploy**

4. **Verificar logs** para ver dónde falla la inicialización completa

## 📝 Comparación

| Característica | App Minimal | App Completa |
|----------------|-------------|--------------|
| **Dependencias** | FastAPI, Uvicorn, Pydantic | +15 librerías más |
| **Build Time** | ~10 segundos | ~30 segundos |
| **Startup Time** | <2 segundos | ~5-10 segundos |
| **Funcionalidad** | Solo health + docs | Análisis IA completo |
| **Tamaño Imagen** | ~200MB | ~500MB |

## 🎯 Objetivo

1. ✅ Probar que Railway puede ejecutar una app FastAPI básica
2. ✅ Verificar que el puerto dinámico funciona
3. ✅ Confirmar que la redirección `/` → `/docs` funciona
4. ✅ Obtener logs de debug para identificar el problema real

## 🚀 Comando Rápido

```bash
# Todo en uno:
cd "Z:\Proyectos\ia-analisis"

git add apps/api/main_minimal.py Dockerfile.minimal start-minimal.sh railway-minimal.json RAILWAY_QUICK_FIX.md

git commit -m "debug: Add minimal Railway test app

- Minimal FastAPI app with only health check and docs redirect
- Dockerfile.minimal with minimal dependencies
- Debug endpoint to inspect Railway environment
- Troubleshooting guide for Railway deployment"

git push origin feat/layered-architecture-openapi
```

Luego en Railway:
1. Settings → Deploy → Dockerfile Path → `Dockerfile.minimal`
2. Save
3. Redeploy

---

**Nota**: Una vez identificado el problema con la app minimal, podemos volver a `Dockerfile` y arreglar el issue específico.
