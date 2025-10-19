# Despliegue en Railway

## Configuración de Variables de Entorno

Para que la API funcione correctamente en Railway, necesitas configurar las siguientes variables de entorno:

### Variables Requeridas

1. **GOOGLE_API_KEY** (REQUERIDO)
   - Obtén tu API key de Google AI Studio
   - Sin esta variable, la API no funcionará
   - Ejemplo: `AIzaSyAWRoXr18XDdpA8tALdmqBlH9zBMUNuNFw`

2. **GEMINI_MODEL** (OPCIONAL)
   - Modelo de Gemini a utilizar
   - Por defecto: `gemini-1.5-flash`
   - Opciones: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-pro`

### Variables Opcionales

3. **LANGFUSE_PUBLIC_KEY** (opcional)
   - Para observabilidad y monitoreo
   - Obtén de tu cuenta de Langfuse
   - Ejemplo: `pk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

4. **LANGFUSE_SECRET_KEY** (opcional)
   - Para observabilidad y monitoreo
   - Obtén de tu cuenta de Langfuse
   - Ejemplo: `sk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

5. **LANGFUSE_HOST** (opcional)
   - URL del host de Langfuse
   - Por defecto: `https://us.cloud.langfuse.com`

6. **JIRA_BASE_URL** (opcional)
   - URL base de tu instancia de Jira
   - Ejemplo: `https://your-domain.atlassian.net`

7. **JIRA_TOKEN** (opcional)
   - Token de autenticación de Jira
   - Obtén de tu perfil de Jira
   - Ejemplo: `ATCTT3xFfGN0c3dETJjiWzxKErcfV8-DXD8yrdGPvyo_YOxMR6i6ASScKoDGVCbFRBSMHGFRsJu0a1VlB4o7OK01kq1dCaQgabwfSohsjiGzJOaWHcQL8n1xslWYPBkqd1JgzkVM_oE5TkfxakmmZA_3uQpIiMewToOAsynN9x5qeP8FJPMy7nM=DA95D797`

8. **JIRA_ORG_ID** (opcional)
   - ID de organización de Jira
   - Ejemplo: `2ecbde5d-e040-4d64-a723-b53ef1ef34a2`

## Cómo Configurar en Railway

1. Ve a tu proyecto en Railway
2. Selecciona la pestaña "Variables"
3. Agrega las variables de entorno necesarias
4. Reinicia el servicio

## Verificación

Una vez desplegado, puedes verificar la configuración:

```bash
curl https://ia-analisis-production.up.railway.app/config
```

## Endpoints Disponibles

- **Documentación**: https://ia-analisis-production.up.railway.app/docs
- **Health Check**: https://ia-analisis-production.up.railway.app/health
- **Config Check**: https://ia-analisis-production.up.railway.app/config

## Solución de Problemas

### Error 500: "Model not configured"
- Verifica que `GOOGLE_API_KEY` esté configurada
- Verifica que la API key sea válida

### Error 503: "AI model not configured"
- Mismo problema que el error 500
- La API key no está configurada o es inválida

### Error de conexión a Langfuse
- Verifica las credenciales de Langfuse
- El servicio funcionará sin Langfuse, pero sin observabilidad
