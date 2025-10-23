# Análisis Estático de Requisitos ISTQB

## Descripción

El endpoint `/analysis/requirements/istqb-check` implementa un análisis estático de requisitos siguiendo los estándares **ISTQB Foundation Level v4.0**. Este endpoint evalúa la calidad de requerimientos escritos en lenguaje natural, detectando ambigüedades, malas prácticas y riesgos.

## Características Principales

### 🎯 Criterios de Evaluación
- **Claridad**: No ambiguo, términos específicos
- **Completitud**: Entradas, salidas, reglas, restricciones, NFR
- **Consistencia**: Sin contradicciones internas/externas
- **Factibilidad**: Técnica y operativamente viable
- **Testabilidad**: Criterios de aceptación medibles

### 🔍 Heurísticas de Ambigüedad Detectadas
- Términos vagos: rápido, fácil, robusto, óptimo
- Cuantificadores difusos: algunos, varios, suficiente
- Rangos abiertos: <, >, alrededor de, aproximadamente
- Pronombres sin antecedente: esto, eso, ellos
- Voz pasiva sin responsable: se realizará, será procesado
- Deixis temporal/espacial: pronto, en breve, más adelante

### ⚡ Validaciones Automáticas
- Longitud mínima del requerimiento (30 caracteres)
- Detección de términos vagos
- Verificación de métricas en requerimientos de rendimiento
- Análisis de completitud básica

## Endpoint

```
POST /analysis/requirements/istqb-check
```

### Headers Sugeridos
```
Content-Type: application/json
X-Model: gpt-4
X-Analysis-Version: istqb-v1
Content-Language: es-PY
```

### Estructura de Entrada

```json
{
  "requirement_id": "REQ-123",
  "requirement_text": "Texto completo del requerimiento (mínimo 30 caracteres)",
  "context": {
    "product": "Sistema de Autenticación",
    "module": "Login",
    "stakeholders": ["PO", "QA", "Dev"],
    "constraints": ["PCI DSS", "LGPD", "SLA 200ms p95"],
    "dependencies": ["API Clientes v2"]
  },
  "glossary": {
    "NroDoc": "Número de documento nacional",
    "ClienteVIP": "Cliente con score >= 800"
  },
  "acceptance_template": "Dado/Cuando/Entonces",
  "non_functional_expectations": ["p95<=300ms", "TLS1.3", "a11y WCAG AA"]
}
```

### Estructura de Salida

```json
{
  "requirement_id": "REQ-123",
  "quality_score": {
    "overall": 85,
    "clarity": 90,
    "completeness": 80,
    "consistency": 85,
    "feasibility": 90,
    "testability": 75
  },
  "issues": [
    {
      "id": "ISS-001",
      "type": "Ambiguity",
      "heuristic": "VagueTerm",
      "excerpt": "término vago: 'rápido'",
      "explanation": "El término 'rápido' es ambiguo según ISTQB - debe ser cuantificado",
      "impact_area": ["Value", "Testability"],
      "risk": {
        "severity": "Medium",
        "likelihood": "High",
        "rpn": 12
      },
      "fix_suggestion": "Especificar tiempo máximo de respuesta: 'p95 ≤ 300ms'",
      "proposed_rewrite": "El sistema debe responder en p95 ≤ 300ms"
    }
  ],
  "coverage": {
    "inputs_defined": true,
    "outputs_defined": true,
    "business_rules": ["BR-001", "BR-002"],
    "error_handling_defined": true,
    "roles_responsibilities_defined": false,
    "data_contracts_defined": true,
    "nfr_defined": ["performance", "security"]
  },
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "format": "GWT",
      "criterion": "Dado un usuario válido Cuando ingresa credenciales correctas Entonces debe autenticarse exitosamente",
      "measurable": true,
      "test_oracle": "Verificar redirección al dashboard y token de sesión válido",
      "example_data": {
        "input": "usuario: test@example.com, password: Test123!",
        "expected": "Redirección a /dashboard, token JWT válido"
      }
    }
  ],
  "traceability": {
    "glossary_terms_used": ["Credenciales", "Autenticación"],
    "external_refs_needed": ["PCI DSS", "LGPD"],
    "dependencies_touched": ["API Clientes v2"]
  },
  "summary": "Requerimiento con buena estructura pero necesita especificación de métricas de rendimiento y manejo de errores más detallado. Prioridad: Media.",
  "proposed_clean_version": "El sistema debe permitir autenticación de usuarios con credenciales válidas, respondiendo en p95 ≤ 300ms, con manejo de errores específico y validación contra base de datos LDAP.",
  "analysis_id": "istqb_REQ-123_1640995200",
  "processing_time": 8.5,
  "created_at": "2025-01-18T10:00:00Z"
}
```

## Códigos de Respuesta

| Código | Descripción |
|--------|-------------|
| 200 | Análisis completado exitosamente |
| 400 | JSON inválido o requirement_text vacío |
| 422 | Texto ilegible (idioma no soportado) |
| 500 | Error interno del analizador |

## Tipos de Issues Detectados

### Ambiguity
- **VagueTerm**: Términos vagos (rápido, fácil, óptimo)
- **FuzzyQuantifier**: Cuantificadores difusos (algunos, varios)
- **OpenRange**: Rangos abiertos (<, >, alrededor de)
- **PronounWithoutAntecedent**: Pronombres sin antecedente
- **PassiveVoice**: Voz pasiva sin responsable
- **TemporalDeixis**: Deixis temporal/espacial

### Omission
- **MissingInputOutput**: Falta definición de entradas/salidas
- **MissingErrorHandling**: Falta manejo de errores
- **UndefinedRole**: Roles no definidos

### Inconsistency
- **RuleConflict**: Conflictos entre reglas

### NFRGap
- **MissingInputOutput**: Falta especificación de NFRs

### DataSpecGap
- **MissingInputOutput**: Falta especificación de datos

### ResponsibilityGap
- **UndefinedRole**: Responsabilidades no definidas

## Niveles de Riesgo

### Severidad
- **Low**: Impacto mínimo
- **Medium**: Impacto moderado
- **High**: Impacto alto
- **Critical**: Impacto crítico

### Probabilidad
- **Low**: Baja probabilidad
- **Medium**: Probabilidad media
- **High**: Alta probabilidad

### RPN (Risk Priority Number)
- **1-9**: Riesgo bajo
- **10-18**: Riesgo medio
- **19-27**: Riesgo alto

## Ejemplos de Uso

### Ejemplo 1: Requerimiento Típico
```python
import requests

payload = {
    "requirement_id": "REQ-AUTH-001",
    "requirement_text": "El sistema debe permitir autenticación de usuarios con credenciales válidas, validando contra la base de datos y mostrando mensajes de error apropiados.",
    "context": {
        "product": "Sistema de Autenticación",
        "module": "Login",
        "stakeholders": ["PO", "QA", "Dev"],
        "constraints": ["PCI DSS", "LGPD"],
        "dependencies": ["API Usuarios v2"]
    },
    "glossary": {
        "Credenciales": "Usuario y contraseña",
        "Autenticación": "Verificación de identidad"
    },
    "acceptance_template": "Dado/Cuando/Entonces",
    "non_functional_expectations": ["p95<=300ms", "TLS1.3"]
}

response = requests.post(
    "http://localhost:8000/analysis/requirements/istqb-check",
    json=payload,
    headers={
        "Content-Type": "application/json",
        "X-Model": "gpt-4",
        "X-Analysis-Version": "istqb-v1",
        "Content-Language": "es-PY"
    }
)

resultado = response.json()
print(f"Puntuación: {resultado['quality_score']['overall']}/100")
print(f"Issues: {len(resultado['issues'])}")
```

### Ejemplo 2: Requerimiento Problemático
```python
payload = {
    "requirement_id": "REQ-BAD-001",
    "requirement_text": "El sistema debe ser rápido y fácil de usar.",
    "context": {
        "product": "Sistema de Pruebas",
        "module": "Interfaz",
        "stakeholders": ["PO"],
        "constraints": [],
        "dependencies": []
    },
    "glossary": {},
    "acceptance_template": "Dado/Cuando/Entonces",
    "non_functional_expectations": []
}

# Este requerimiento generará múltiples issues:
# - Términos vagos: "rápido", "fácil"
# - Falta de especificaciones
# - Sin criterios de aceptación
```

## Mejores Prácticas

### ✅ Requerimientos Buenos
- Términos específicos y cuantificables
- Entradas y salidas claramente definidas
- Manejo de errores especificado
- Criterios de aceptación SMART
- Roles y responsabilidades definidos
- NFRs con métricas específicas

### ❌ Requerimientos Problemáticos
- Términos vagos (rápido, fácil, óptimo)
- Falta de especificaciones técnicas
- Sin manejo de errores
- Criterios de aceptación no medibles
- Roles no definidos
- NFRs sin métricas

## Integración con Herramientas

### Jira
```python
# Crear issue en Jira basado en issues detectados
for issue in resultado['issues']:
    if issue['risk']['severity'] in ['High', 'Critical']:
        jira_issue = {
            "summary": f"[ISTQB] {issue['type']}: {issue['excerpt']}",
            "description": f"{issue['explanation']}\n\nSugerencia: {issue['fix_suggestion']}",
            "priority": issue['risk']['severity'],
            "labels": ["istqb", "requirement-quality"]
        }
        # Crear issue en Jira
```

### Confluence
```python
# Generar reporte de calidad
reporte = {
    "requirement_id": resultado['requirement_id'],
    "quality_score": resultado['quality_score']['overall'],
    "issues_count": len(resultado['issues']),
    "critical_issues": [i for i in resultado['issues'] if i['risk']['severity'] == 'Critical'],
    "recommendations": [i['fix_suggestion'] for i in resultado['issues']]
}
# Guardar en Confluence
```

## Monitoreo y Observabilidad

El endpoint está integrado con Langfuse para observabilidad completa:
- Tracking de análisis
- Métricas de calidad
- Tiempo de procesamiento
- Patrones de issues detectados

## Limitaciones

- Requiere texto en español para mejor análisis
- Dependiente de la calidad del modelo de IA
- Análisis basado en heurísticas predefinidas
- No reemplaza revisión humana experta

## Roadmap

- [ ] Soporte para múltiples idiomas
- [ ] Integración con herramientas de gestión de requisitos
- [ ] Análisis de dependencias entre requisitos
- [ ] Métricas de tendencia de calidad
- [ ] Exportación a formatos estándar (ReqIF, etc.)