# Solución al Error 502 en Railway

## Problema Identificado
El error 502 se debía a una configuración incorrecta del puerto y el comando de inicio en Railway.

## Cambios Realizados

### 1. Archivo `app_simple.py` (Nuevo)
- Versión ultra simplificada de FastAPI
- Solo endpoints `/` y `/health`
- Configuración de puerto dinámico usando `PORT` environment variable
- Sin dependencias externas complejas

### 2. Archivo `Dockerfile` (Actualizado)
```dockerfile
# Exponer puerto
EXPOSE 8080

# Comando por defecto
CMD ["python", "app_simple.py"]
```

### 3. Archivo `railway.json` (Actualizado)
```json
{
  "deploy": {
    "startCommand": "python app_simple.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

## Verificación Local
✅ El servicio funciona correctamente en `http://localhost:8080`
✅ El endpoint `/health` responde con `{"status":"healthy","message":"Service is running"}`
✅ La redirección automática de `/` a `/docs` funciona (Status 307)
✅ Swagger UI es accesible en `/docs`

## Próximos Pasos
1. Hacer commit y push de los cambios
2. Railway debería detectar automáticamente los cambios y redesplegar
3. Verificar que el health check pase
4. Probar acceso a Swagger UI en `https://ia-analisis-production.up.railway.app/docs`
5. Verificar que `https://ia-analisis-production.up.railway.app/` redirija automáticamente a Swagger

## Estructura de Archivos
```
├── app_simple.py          # Versión ultra simple (ACTUAL)
├── app.py                 # Versión anterior
├── main.py                # Versión completa original
├── Dockerfile             # Configurado para app_simple.py
├── railway.json           # Configurado para app_simple.py
└── requirements.txt       # Dependencias mínimas
```

## Comandos de Verificación
```bash
# Local
python app_simple.py
curl http://localhost:8080/health

# Railway (después del despliegue)
curl https://ia-analisis-production.up.railway.app/health
curl -I https://ia-analisis-production.up.railway.app/  # Verificar redirección
curl https://ia-analisis-production.up.railway.app/docs
```
