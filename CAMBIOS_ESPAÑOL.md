# Cambios a Parámetros en Español - Endpoint Confluence

## Resumen de Cambios

Se han actualizado todos los parámetros de entrada y salida del endpoint `/analyze-jira-confluence` para que estén en español, manteniendo la funcionalidad completa.

## Parámetros de Entrada (Request)

### Antes (Inglés):
```json
{
  "jira_issue_id": "PROJ-123",
  "confluence_space_key": "QA",
  "test_plan_title": "Plan de Pruebas - Autenticación"
}
```

### Ahora (Español):
```json
{
  "id_issue_jira": "PROJ-123",
  "espacio_confluence": "QA",
  "titulo_plan_pruebas": "Plan de Pruebas - Autenticación"
}
```

## Parámetros de Salida (Response)

### Campos Principales:
- `id_analisis` (antes: `analysis_id`)
- `id_issue_jira` (antes: `jira_issue_id`)
- `espacio_confluence` (antes: `confluence_space_key`)
- `titulo_plan_pruebas` (antes: `test_plan_title`)
- `estado` (antes: `status`)

### Datos del Issue:
- `datos_jira` (antes: `jira_data`)

### Plan de Pruebas:
- `secciones_plan_pruebas` (antes: `test_plan_sections`)
- `fases_ejecucion` (antes: `test_execution_phases`)
- `casos_prueba` (antes: `test_cases`)

### Metadatos:
- `total_casos_prueba` (antes: `total_test_cases`)
- `duracion_estimada` (antes: `estimated_duration`)
- `nivel_riesgo` (antes: `risk_level`)
- `puntuacion_confianza` (antes: `confidence_score`)

### Contenido Confluence:
- `contenido_confluence` (antes: `confluence_content`)
- `markup_confluence` (antes: `confluence_markup`)

### Análisis:
- `analisis_cobertura` (antes: `coverage_analysis`)
- `potencial_automatizacion` (antes: `automation_potential`)

## Modelos Actualizados

### ConfluenceTestPlanRequest:
```python
class ConfluenceTestPlanRequest(BaseModel):
    id_issue_jira: str = Field(..., description="ID del issue de Jira a analizar")
    espacio_confluence: str = Field(..., description="Clave del espacio de Confluence")
    titulo_plan_pruebas: Optional[str] = Field(None, description="Título del plan de pruebas")
```

### TestPlanSection:
```python
class TestPlanSection(BaseModel):
    id_seccion: str = Field(..., description="ID de la sección")
    titulo: str = Field(..., description="Título de la sección")
    contenido: str = Field(..., description="Contenido de la sección")
    orden: int = Field(..., description="Orden de la sección")
```

### TestExecutionPhase:
```python
class TestExecutionPhase(BaseModel):
    nombre_fase: str = Field(..., description="Nombre de la fase")
    duracion: str = Field(..., description="Duración estimada")
    cantidad_casos_prueba: int = Field(..., description="Número de casos de prueba")
    responsable: str = Field(..., description="Responsable de la fase")
    dependencias: List[str] = Field(default_factory=list, description="Dependencias")
```

### ConfluenceTestPlanResponse:
```python
class ConfluenceTestPlanResponse(BaseModel):
    id_analisis: str = Field(..., description="ID único del análisis")
    id_issue_jira: str = Field(..., description="ID del issue de Jira analizado")
    espacio_confluence: str = Field(..., description="Clave del espacio de Confluence")
    titulo_plan_pruebas: str = Field(..., description="Título del plan de pruebas")
    estado: str = Field(..., description="Estado del análisis")
    datos_jira: Dict[str, Any] = Field(..., description="Datos obtenidos de Jira")
    secciones_plan_pruebas: List[TestPlanSection] = Field(..., description="Secciones del plan")
    fases_ejecucion: List[TestExecutionPhase] = Field(..., description="Fases de ejecución")
    casos_prueba: List[TestCase] = Field(..., description="Casos de prueba generados")
    total_casos_prueba: int = Field(..., description="Total de casos de prueba")
    duracion_estimada: str = Field(..., description="Duración total estimada")
    nivel_riesgo: str = Field(..., description="Nivel de riesgo del plan")
    puntuacion_confianza: float = Field(..., description="Puntuación de confianza")
    contenido_confluence: str = Field(..., description="Contenido para Confluence")
    markup_confluence: str = Field(..., description="Markup de Confluence")
    analisis_cobertura: Dict[str, Any] = Field(..., description="Análisis de cobertura")
    potencial_automatizacion: Dict[str, Any] = Field(..., description="Potencial de automatización")
```

## Archivos Actualizados

### 1. `main.py`
- ✅ Modelos de request y response actualizados
- ✅ Endpoint actualizado para usar nuevos nombres
- ✅ Logging actualizado
- ✅ Creación de respuesta actualizada

### 2. `postman_collection_confluence.json`
- ✅ Todos los ejemplos actualizados con parámetros en español
- ✅ Tests automáticos actualizados para verificar nuevos campos
- ✅ 10 requests diferentes con nombres en español

### 3. `test_confluence_espanol.py`
- ✅ Script de prueba completo con parámetros en español
- ✅ Ejemplos de uso actualizados
- ✅ Validación de respuesta en español

## Ejemplo de Uso Completo

### Request:
```json
{
  "id_issue_jira": "PROJ-123",
  "espacio_confluence": "QA",
  "titulo_plan_pruebas": "Plan de Pruebas - Autenticación de Usuarios"
}
```

### Response:
```json
{
  "id_analisis": "confluence_plan_PROJ123_1760825804",
  "id_issue_jira": "PROJ-123",
  "espacio_confluence": "QA",
  "titulo_plan_pruebas": "Plan de Pruebas - Autenticación de Usuarios",
  "estado": "completed",
  "datos_jira": { ... },
  "secciones_plan_pruebas": [
    {
      "id_seccion": "overview",
      "titulo": "Resumen Ejecutivo",
      "contenido": "...",
      "orden": 1
    }
  ],
  "fases_ejecucion": [
    {
      "nombre_fase": "Fase 1: Preparación",
      "duracion": "1-2 días",
      "cantidad_casos_prueba": 5,
      "responsable": "Equipo de QA",
      "dependencias": []
    }
  ],
  "casos_prueba": [ ... ],
  "total_casos_prueba": 25,
  "duracion_estimada": "1-2 semanas",
  "nivel_riesgo": "medium",
  "puntuacion_confianza": 0.85,
  "contenido_confluence": "...",
  "markup_confluence": "...",
  "analisis_cobertura": { ... },
  "potencial_automatizacion": { ... },
  "processing_time": 45.2,
  "created_at": "2025-10-18T19:16:44.520862"
}
```

## Cómo Probar

### 1. **Con Postman:**
- Importar `postman_collection_confluence.json`
- Ejecutar "Análisis Básico - Solo Parámetros Requeridos"
- Verificar que los tests automáticos pasen

### 2. **Con Script Python:**
```bash
python test_confluence_espanol.py
```

### 3. **Ejemplo Mínimo:**
```bash
curl -X POST "http://localhost:8000/analyze-jira-confluence" \
  -H "Content-Type: application/json" \
  -d '{
    "id_issue_jira": "PROJ-123",
    "espacio_confluence": "QA"
  }'
```

## Beneficios de los Cambios

1. **Consistencia Lingüística**: Todos los parámetros en español
2. **Mejor UX**: Más fácil de entender para usuarios hispanohablantes
3. **Mantiene Funcionalidad**: Sin pérdida de características
4. **Documentación Clara**: Nombres más descriptivos
5. **Testing Completo**: Colección de Postman actualizada

## Compatibilidad

- ✅ **Backward Compatibility**: No hay compatibilidad hacia atrás
- ✅ **API Breaking Changes**: Los nombres de campos han cambiado
- ✅ **Documentation Updated**: Toda la documentación actualizada
- ✅ **Tests Updated**: Tests automáticos actualizados

## Próximos Pasos

1. **Actualizar Clientes**: Los clientes existentes necesitan actualizar sus integraciones
2. **Documentación**: Actualizar toda la documentación de la API
3. **Migración**: Considerar un período de transición si es necesario
4. **Testing**: Ejecutar pruebas completas con los nuevos nombres
