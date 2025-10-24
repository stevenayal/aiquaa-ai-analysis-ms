# Endpoint /analyze-jira-confluence

## Descripción

El endpoint `/analyze-jira-confluence` analiza issues de Jira y genera planes de prueba completos y estructurados para documentar en Confluence. Este endpoint combina la integración con Jira, análisis de IA y generación de contenido optimizado para Confluence.

## Características Principales

- 🔗 **Integración con Jira**: Obtiene datos completos del issue de Jira
- 🤖 **Análisis con IA**: Usa Google Gemini para análisis inteligente
- 📝 **Planes Estructurados**: Genera planes de prueba profesionales
- 🎨 **Formato Confluence**: Contenido optimizado con macros y elementos visuales
- 📊 **Métricas Detalladas**: Análisis de cobertura y potencial de automatización
- ⚡ **Múltiples Estrategias**: Soporte para diferentes enfoques de testing

## Uso del Endpoint

### URL
```
POST /analyze-jira-confluence
```

### Parámetros de Entrada

```json
{
  "jira_issue_id": "PROJ-123",
  "confluence_space_key": "QA",
  "test_plan_title": "Plan de Pruebas - Autenticación de Usuarios",
  "test_strategy": "comprehensive",
  "include_automation": true,
  "include_performance": false,
  "include_security": true
}
```

#### Parámetros Requeridos

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `jira_issue_id` | string | ID del issue de Jira a analizar | "PROJ-123" |
| `confluence_space_key` | string | Clave del espacio de Confluence | "QA" |
| `test_plan_title` | string | Título del plan de pruebas | "Plan de Pruebas - Autenticación" |

#### Parámetros Opcionales

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `test_strategy` | string | "comprehensive" | Estrategia de testing (basic, standard, comprehensive, agile) |
| `include_automation` | boolean | true | Incluir casos de automatización |
| `include_performance` | boolean | false | Incluir casos de rendimiento |
| `include_security` | boolean | true | Incluir casos de seguridad |

### Estrategias de Testing

| Estrategia | Descripción | Casos Generados |
|------------|-------------|-----------------|
| `basic` | Plan básico con casos esenciales | 5-10 casos |
| `standard` | Plan estándar con casos funcionales y de integración | 10-20 casos |
| `comprehensive` | Plan completo con todos los tipos de pruebas | 20-40 casos |
| `agile` | Plan ágil optimizado para metodologías ágiles | 15-30 casos |

## Respuesta del Endpoint

### Estructura de la Respuesta

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

### Componentes Principales

#### 1. Secciones del Plan de Pruebas (`test_plan_sections`)
- **Resumen Ejecutivo**: Objetivos y alcance del plan
- **Alcance y Criterios**: Definición del alcance de pruebas
- **Estrategia de Testing**: Enfoque y metodología
- **Plan de Ejecución**: Cronograma y fases
- **Casos de Prueba**: Lista estructurada de casos
- **Criterios de Aceptación**: Definición de criterios
- **Gestión de Riesgos**: Identificación y mitigación
- **Recursos y Cronograma**: Recursos necesarios

#### 2. Fases de Ejecución (`test_execution_phases`)
- **Fase 1**: Preparación y Setup
- **Fase 2**: Pruebas Funcionales
- **Fase 3**: Pruebas de Integración
- **Fase 4**: Pruebas de Aceptación

#### 3. Casos de Prueba (`test_cases`)
- Formato estándar: `CP - NNN - APLICACION - MODULO - DATO - CONDICION - RESULTADO`
- Pasos detallados y verificables
- Resultados esperados específicos
- Precondiciones completas
- Datos de prueba realistas
- Evaluación de automatización

#### 4. Contenido de Confluence
- **`confluence_content`**: Contenido completo con formato
- **`confluence_markup`**: Markup específico para crear la página
- Optimizado con macros de Confluence
- Tablas estructuradas y elementos visuales
- Enlaces y referencias cruzadas

## Ejemplos de Uso

### Ejemplo 1: Historia de Usuario
```bash
curl -X POST "http://localhost:8000/analyze-jira-confluence" \
  -H "Content-Type: application/json" \
  -d '{
    "jira_issue_id": "AUTH-001",
    "confluence_space_key": "QA",
    "test_plan_title": "Plan de Pruebas - Sistema de Autenticación",
    "test_strategy": "comprehensive",
    "include_automation": true,
    "include_security": true
  }'
```

### Ejemplo 2: Tarea de Integración
```bash
curl -X POST "http://localhost:8000/analyze-jira-confluence" \
  -H "Content-Type: application/json" \
  -d '{
    "jira_issue_id": "API-002",
    "confluence_space_key": "DEV",
    "test_plan_title": "Plan de Pruebas - Integración API de Pagos",
    "test_strategy": "agile",
    "include_automation": true,
    "include_performance": true
  }'
```

### Ejemplo 3: Bug de Rendimiento
```bash
curl -X POST "http://localhost:8000/analyze-jira-confluence" \
  -H "Content-Type: application/json" \
  -d '{
    "jira_issue_id": "PERF-003",
    "confluence_space_key": "QA",
    "test_plan_title": "Plan de Pruebas - Optimización de Rendimiento",
    "test_strategy": "standard",
    "include_performance": true
  }'
```

## Scripts de Prueba

### 1. Prueba Básica
```bash
python test_confluence_endpoint.py
```

### 2. Ejemplos de Uso
```bash
python ejemplo_uso_confluence_endpoint.py
```

## Códigos de Respuesta

| Código | Descripción |
|--------|-------------|
| 200 | Análisis completado exitosamente |
| 404 | Issue de Jira no encontrado |
| 422 | Datos de entrada inválidos |
| 500 | Error interno del servidor |

## Características Avanzadas

### 1. Análisis de Cobertura
- Cobertura funcional
- Cobertura de casos edge
- Cobertura de integración
- Cobertura de seguridad
- Cobertura de UI/UX
- Cobertura de accesibilidad

### 2. Potencial de Automatización
- Evaluación de casos automatizables
- Herramientas recomendadas
- Esfuerzo de implementación
- Consideraciones de mantenimiento

### 3. Formato Confluence
- Macros de información (info, warning, note)
- Tablas estructuradas para casos de prueba
- Enlaces a issues de Jira relacionados
- Elementos visuales apropiados
- Optimizado para colaboración

### 4. Gestión de Riesgos
- Identificación de riesgos
- Estrategias de mitigación
- Niveles de prioridad
- Impacto en el negocio

## Integración con Herramientas

### Jira
- Obtiene datos completos del issue
- Considera dependencias y relaciones
- Analiza criterios de aceptación
- Evalúa contexto del proyecto

### Confluence
- Genera contenido optimizado
- Utiliza macros y elementos visuales
- Estructura colaborativa
- Facilita revisión y actualización

### IA (Google Gemini)
- Análisis inteligente del contenido
- Generación de casos de prueba
- Evaluación de cobertura
- Optimización de estrategias

## Mejores Prácticas

### 1. Preparación
- Asegúrate de que el issue de Jira exista
- Verifica permisos en el espacio de Confluence
- Define claramente el alcance del plan

### 2. Configuración
- Selecciona la estrategia apropiada
- Habilita/deshabilita tipos de pruebas según necesidad
- Considera el contexto del proyecto

### 3. Uso del Contenido
- Revisa el contenido generado
- Adapta según necesidades específicas
- Colabora con el equipo para refinamiento

### 4. Seguimiento
- Monitorea la ejecución del plan
- Actualiza según cambios en el issue
- Evalúa la efectividad del plan

## Troubleshooting

### Problemas Comunes

1. **Issue de Jira no encontrado**
   - Verifica que el ID del issue sea correcto
   - Confirma que tienes permisos de acceso
   - Revisa la configuración de Jira

2. **Timeout en la respuesta**
   - El análisis puede tomar tiempo según la complejidad
   - Considera usar estrategias más simples para issues complejos

3. **Contenido de Confluence no se renderiza**
   - Verifica que el espacio de Confluence exista
   - Confirma permisos de escritura
   - Revisa la configuración de macros

### Logs y Debugging

- Revisa los logs del servidor para detalles
- Usa el endpoint `/health` para verificar estado
- Consulta las métricas de procesamiento

## Roadmap

### Próximas Características
- Integración directa con Confluence API
- Plantillas personalizables
- Análisis de dependencias entre issues
- Métricas de calidad del plan
- Integración con herramientas de CI/CD

### Mejoras Planificadas
- Soporte para múltiples issues
- Análisis de impacto en el negocio
- Generación de reportes ejecutivos
- Integración con herramientas de testing
- Automatización de la creación de páginas

## Soporte

Para soporte técnico o preguntas sobre el endpoint:
- Revisa la documentación de la API
- Consulta los logs del servidor
- Verifica la configuración de Jira y Confluence
- Contacta al equipo de desarrollo
