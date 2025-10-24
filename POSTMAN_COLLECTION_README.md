# Colección de Postman - Endpoint Confluence

## Descripción

Esta colección de Postman contiene todas las pruebas necesarias para el endpoint `/analyze-jira-confluence` con parámetros simplificados. Incluye ejemplos de uso, pruebas de validación y tests automáticos.

## Archivos Incluidos

- `postman_collection_confluence.json` - Colección principal de Postman
- `postman_environment_confluence.json` - Variables de entorno
- `test_confluence_simplified.py` - Script de prueba simplificado

## Configuración

### 1. Importar en Postman

1. Abre Postman
2. Haz clic en "Import"
3. Selecciona los archivos:
   - `postman_collection_confluence.json`
   - `postman_environment_confluence.json`

### 2. Configurar Variables de Entorno

Las variables principales son:

| Variable | Valor por Defecto | Descripción |
|----------|-------------------|-------------|
| `base_url` | `http://localhost:8000` | URL del servidor |
| `jira_issue_id` | `PROJ-123` | ID del issue de Jira |
| `confluence_space_key` | `QA` | Espacio de Confluence |
| `test_plan_title` | `Plan de Pruebas - Autenticación de Usuarios` | Título del plan |

### 3. Configurar el Servidor

Asegúrate de que el servidor esté ejecutándose:

```bash
# Desarrollo local
python main.py

# O con uvicorn directamente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Requests Incluidos

### 1. Health Check
- **Método**: GET
- **URL**: `{{base_url}}/health`
- **Descripción**: Verificar el estado del servidor

### 2. Análisis Básico - Solo Parámetros Requeridos
```json
{
  "jira_issue_id": "{{jira_issue_id}}",
  "confluence_space_key": "{{confluence_space_key}}"
}
```

### 3. Análisis Completo - Con Título Personalizado
```json
{
  "jira_issue_id": "{{jira_issue_id}}",
  "confluence_space_key": "{{confluence_space_key}}",
  "test_plan_title": "Plan de Pruebas - Autenticación de Usuarios"
}
```

### 4. Ejemplos de Uso

#### Historia de Usuario
```json
{
  "jira_issue_id": "AUTH-001",
  "confluence_space_key": "QA",
  "test_plan_title": "Plan de Pruebas - Sistema de Autenticación"
}
```

#### Tarea de Integración
```json
{
  "jira_issue_id": "API-002",
  "confluence_space_key": "DEV",
  "test_plan_title": "Plan de Pruebas - Integración API de Pagos"
}
```

#### Bug de Rendimiento
```json
{
  "jira_issue_id": "PERF-003",
  "confluence_space_key": "QA",
  "test_plan_title": "Plan de Pruebas - Optimización de Rendimiento"
}
```

#### Epic Complejo
```json
{
  "jira_issue_id": "EPIC-001",
  "confluence_space_key": "PRODUCT",
  "test_plan_title": "Plan de Pruebas - Nueva Funcionalidad de E-commerce"
}
```

### 5. Pruebas de Error

#### Issue No Encontrado
```json
{
  "jira_issue_id": "INVALID-999",
  "confluence_space_key": "QA"
}
```

#### Parámetros Inválidos
```json
{
  "jira_issue_id": "",
  "confluence_space_key": "QA"
}
```

## Tests Automáticos

La colección incluye tests automáticos que verifican:

### Tests Básicos
- ✅ Status code es 200
- ✅ Tiempo de respuesta menor a 120 segundos
- ✅ Respuesta contiene campos requeridos

### Tests de Contenido
- ✅ `analysis_id` presente
- ✅ `jira_issue_id` presente
- ✅ `confluence_space_key` presente
- ✅ `status` presente

### Tests de Estructura
- ✅ `test_plan_sections` es un array no vacío
- ✅ `test_cases` es un array no vacío
- ✅ `confluence_content` es un string no vacío
- ✅ `coverage_analysis` es un objeto
- ✅ `automation_potential` es un objeto

### Tests de Calidad
- ✅ `confidence_score` está entre 0 y 1
- ✅ `processing_time` es un número positivo

## Uso de la Colección

### 1. Ejecutar Todas las Pruebas

1. Selecciona la colección "Análisis QA - Confluence Endpoint"
2. Haz clic en "Run collection"
3. Selecciona el entorno "Confluence QA Analysis Environment"
4. Haz clic en "Run Análisis QA - Confluence Endpoint"

### 2. Ejecutar Pruebas Individuales

1. Selecciona el request que quieres probar
2. Ajusta las variables si es necesario
3. Haz clic en "Send"

### 3. Personalizar Variables

1. Ve a "Environments"
2. Selecciona "Confluence QA Analysis Environment"
3. Modifica las variables según tus necesidades

## Ejemplos de Respuesta

### Respuesta Exitosa
```json
{
  "jira_issue_id": "PROJ-123",
  "confluence_space_key": "QA",
  "test_plan_title": "Plan de Pruebas - Autenticación de Usuarios",
  "analysis_id": "confluence_plan_PROJ123_1760825804",
  "status": "completed",
  "jira_data": { ... },
  "test_plan_sections": [ ... ],
  "test_execution_phases": [ ... ],
  "test_cases": [ ... ],
  "total_test_cases": 25,
  "estimated_duration": "1-2 semanas",
  "risk_level": "medium",
  "confidence_score": 0.85,
  "confluence_content": "...",
  "confluence_markup": "...",
  "coverage_analysis": { ... },
  "automation_potential": { ... },
  "processing_time": 45.2,
  "created_at": "2025-10-18T19:16:44.520862"
}
```

### Respuesta de Error
```json
{
  "detail": "Issue de Jira INVALID-999 not found"
}
```

## Troubleshooting

### Problemas Comunes

1. **Error de Conexión**
   - Verifica que el servidor esté ejecutándose
   - Confirma la URL en las variables de entorno

2. **Timeout en las Respuestas**
   - El análisis puede tomar tiempo según la complejidad
   - Aumenta el timeout en Postman si es necesario

3. **Issue No Encontrado**
   - Verifica que el issue de Jira exista
   - Confirma la configuración de Jira

4. **Tests Fallando**
   - Revisa que el servidor esté funcionando correctamente
   - Verifica la configuración de Jira y Confluence

### Logs y Debugging

- Revisa la consola de Postman para errores
- Usa el request "Health Check" para verificar el estado
- Consulta los logs del servidor para detalles

## Configuración Avanzada

### Variables de Entorno Adicionales

Puedes agregar más variables según tus necesidades:

```json
{
  "key": "custom_jira_issue",
  "value": "CUSTOM-001",
  "type": "default",
  "enabled": true
}
```

### Tests Personalizados

Puedes agregar tests personalizados en la sección "Tests" de cada request:

```javascript
pm.test("Custom test", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.custom_field).to.exist;
});
```

### Pre-request Scripts

Puedes agregar scripts que se ejecuten antes de cada request:

```javascript
// Generar timestamp único
pm.environment.set("timestamp", new Date().getTime());
```

## Integración con CI/CD

### Newman (CLI de Postman)

```bash
# Instalar Newman
npm install -g newman

# Ejecutar colección
newman run postman_collection_confluence.json -e postman_environment_confluence.json

# Con reporte HTML
newman run postman_collection_confluence.json -e postman_environment_confluence.json --reporters html --reporter-html-export report.html
```

### GitHub Actions

```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Newman
        run: |
          npm install -g newman
          newman run postman_collection_confluence.json -e postman_environment_confluence.json
```

## Mejores Prácticas

### 1. Organización
- Usa nombres descriptivos para los requests
- Agrupa requests relacionados en folders
- Documenta cada request con descripciones claras

### 2. Variables
- Usa variables para valores que cambian frecuentemente
- Mantén valores sensibles en variables de entorno
- Documenta el propósito de cada variable

### 3. Tests
- Escribe tests que verifiquen la funcionalidad crítica
- Incluye tests de validación de datos
- Prueba casos de error y edge cases

### 4. Mantenimiento
- Actualiza la colección cuando cambie la API
- Revisa y actualiza los tests regularmente
- Documenta cambios importantes

## Soporte

Para soporte técnico o preguntas sobre la colección:
- Revisa la documentación de la API
- Consulta los logs del servidor
- Verifica la configuración de Jira y Confluence
- Contacta al equipo de desarrollo
