# 🚀 API de Análisis QA - Endpoints en Español

## 📋 Endpoints Disponibles

### 1. **`POST /analizar`** - Análisis de Contenido
**Descripción**: Analiza cualquier tipo de contenido y genera casos de prueba usando IA

**Parámetros de Entrada**:
```json
{
  "id_contenido": "TC-001",
  "contenido": "Verificar que el usuario pueda iniciar sesión...",
  "tipo_contenido": "test_case",
  "nivel_analisis": "high"
}
```

**Parámetros de Salida**:
```json
{
  "id_contenido": "TC-001",
  "id_analisis": "analysis_TC001_1760825804",
  "estado": "completed",
  "casos_prueba": [...],
  "sugerencias": [...],
  "analisis_cobertura": {...},
  "puntuacion_confianza": 0.85,
  "tiempo_procesamiento": 8.81,
  "fecha_creacion": "2025-10-18T19:16:44.520862"
}
```

### 2. **`POST /analizar-jira`** - Análisis de Work Items de Jira
**Descripción**: Obtiene un work item de Jira y genera casos de prueba estructurados

**Parámetros de Entrada**:
```json
{
  "id_work_item": "AUTH-123",
  "nivel_analisis": "high"
}
```

**Parámetros de Salida**:
```json
{
  "id_work_item": "AUTH-123",
  "datos_jira": {...},
  "id_analisis": "jira_analysis_AUTH123_1760825804",
  "estado": "completed",
  "casos_prueba": [...],
  "analisis_cobertura": {...},
  "puntuacion_confianza": 0.85,
  "tiempo_procesamiento": 15.5,
  "fecha_creacion": "2025-10-18T19:16:44.520862"
}
```

### 3. **`POST /generar-pruebas-avanzadas`** - Generación Avanzada
**Descripción**: Genera casos de prueba aplicando técnicas de diseño avanzadas

**Parámetros de Entrada**:
```json
{
  "requerimiento": "El sistema debe permitir a los usuarios autenticarse...",
  "aplicacion": "SISTEMA_AUTH"
}
```

**Parámetros de Salida**:
```json
{
  "aplicacion": "SISTEMA_AUTH",
  "id_generacion": "advanced_SISTEMA_AUTH_1760825804",
  "estado": "completed",
  "casos_prueba": [...],
  "analisis_cobertura": {...},
  "puntuacion_confianza": 0.85,
  "tiempo_procesamiento": 25.3,
  "fecha_creacion": "2025-10-18T19:16:44.520862"
}
```

### 4. **`POST /analisis/requisitos/verificacion-istqb`** - Análisis ISTQB
**Descripción**: Evalúa la calidad de un requerimiento siguiendo estándares ISTQB

**Parámetros de Entrada**:
```json
{
  "requirement_id": "REQ-001",
  "requirement_text": "El sistema debe permitir a los usuarios iniciar sesión...",
  "context": {
    "producto": "Sistema de Autenticación",
    "modulo": "Login",
    "stakeholders": ["PO", "QA", "Dev"],
    "restricciones": ["PCI DSS", "LGPD"],
    "dependencias": ["API Clientes v2"]
  },
  "glossary": {...},
  "acceptance_template": "Dado [condición] cuando [acción] entonces [resultado]",
  "non_functional_expectations": ["Rendimiento", "Seguridad", "Usabilidad"]
}
```

**Parámetros de Salida**:
```json
{
  "id_requerimiento": "REQ-001",
  "puntuacion_calidad": {...},
  "issues": [...],
  "cobertura": {...},
  "criterios_aceptacion": [...],
  "trazabilidad": {...},
  "resumen": "...",
  "version_limpia_propuesta": "...",
  "id_analisis": "istqb_REQ001_1760825804",
  "tiempo_procesamiento": 12.5,
  "fecha_creacion": "2025-10-18T19:16:44.520862"
}
```

### 5. **`POST /analizar-jira-confluence`** - Análisis Jira-Confluence
**Descripción**: Analiza un issue de Jira y genera un plan de pruebas para Confluence

**Parámetros de Entrada**:
```json
{
  "id_issue_jira": "PROJ-123",
  "espacio_confluence": "QA",
  "titulo_plan_pruebas": "Plan de Pruebas - Autenticación"
}
```

**Parámetros de Salida**:
```json
{
  "id_issue_jira": "PROJ-123",
  "espacio_confluence": "QA",
  "titulo_plan_pruebas": "Plan de Pruebas - Autenticación",
  "id_analisis": "confluence_plan_PROJ123_1760825804",
  "estado": "completed",
  "datos_jira": {...},
  "secciones_plan_pruebas": [...],
  "fases_ejecucion": [...],
  "casos_prueba": [...],
  "total_casos_prueba": 25,
  "duracion_estimada": "1-2 semanas",
  "nivel_riesgo": "medium",
  "puntuacion_confianza": 0.85,
  "contenido_confluence": "...",
  "markup_confluence": "...",
  "analisis_cobertura": {...},
  "potencial_automatizacion": {...},
  "processing_time": 45.2,
  "created_at": "2025-10-18T19:16:44.520862"
}
```

### 6. **`GET /salud`** - Health Check
**Descripción**: Verifica el estado de salud del servicio

**Parámetros de Salida**:
```json
{
  "estado": "healthy",
  "timestamp": "2025-10-18T19:16:44.520862",
  "version": "1.0.0",
  "componentes": {
    "langfuse": "healthy",
    "jira": "healthy",
    "llm": "healthy"
  }
}
```

## 🔄 Migración de Endpoints

### Endpoints Anteriores → Nuevos Endpoints

| Endpoint Anterior | Nuevo Endpoint | Descripción |
|-------------------|----------------|-------------|
| `/analyze` | `/analizar` | Análisis de contenido |
| `/analyze-jira` | `/analizar-jira` | Análisis de Jira |
| `/generate-advanced-tests` | `/generar-pruebas-avanzadas` | Generación avanzada |
| `/analysis/requirements/istqb-check` | `/analisis/requisitos/verificacion-istqb` | Análisis ISTQB |
| `/analyze-jira-confluence` | `/analizar-jira-confluence` | Análisis Jira-Confluence |
| `/health` | `/salud` | Health check |

## 🧪 Ejemplos de Uso

### Ejemplo 1: Análisis de Caso de Prueba
```bash
curl -X POST "http://localhost:8000/analizar" \
  -H "Content-Type: application/json" \
  -d '{
    "id_contenido": "TC-001",
    "contenido": "Verificar que el usuario pueda iniciar sesión con credenciales válidas",
    "tipo_contenido": "test_case",
    "nivel_analisis": "high"
  }'
```

### Ejemplo 2: Análisis de Jira
```bash
curl -X POST "http://localhost:8000/analizar-jira" \
  -H "Content-Type: application/json" \
  -d '{
    "id_work_item": "AUTH-123",
    "nivel_analisis": "high"
  }'
```

### Ejemplo 3: Generación Avanzada
```bash
curl -X POST "http://localhost:8000/generar-pruebas-avanzadas" \
  -H "Content-Type: application/json" \
  -d '{
    "requerimiento": "El sistema debe permitir a los usuarios autenticarse usando email y contraseña",
    "aplicacion": "SISTEMA_AUTH"
  }'
```

### Ejemplo 4: Health Check
```bash
curl -X GET "http://localhost:8000/salud"
```

## 📊 Swagger UI

La documentación interactiva está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Beneficios de los Endpoints en Español

1. **Consistencia Lingüística**: Todos los endpoints en español
2. **Mejor UX**: Más intuitivo para desarrolladores hispanohablantes
3. **Mantiene Funcionalidad**: Sin pérdida de características
4. **Documentación Clara**: Nombres más descriptivos
5. **Testing Completo**: Validación automática de respuestas

## 🔧 Configuración

### Variables de Entorno
```bash
GOOGLE_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-pro
JIRA_URL=https://tu-empresa.atlassian.net
JIRA_EMAIL=tu-email@empresa.com
JIRA_TOKEN=tu_token_aqui
```

### Instalación
```bash
pip install -r requirements.txt
python main.py
```

## 📝 Notas Importantes

- **Breaking Changes**: Los endpoints han cambiado de inglés a español
- **Compatibilidad**: No hay compatibilidad hacia atrás
- **Migración**: Los clientes existentes necesitan actualizar sus integraciones
- **Testing**: Ejecutar pruebas completas con los nuevos endpoints
