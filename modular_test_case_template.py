"""
Plantilla para generación de test cases con estructura modular.
Formato: CP001 - NOMBRE DE APLICACION - MODULO - CONDICION Y RESULTADO
"""

from typing import Dict, List, Any
import re

class ModularTestCaseTemplate:
    """Generador de test cases con estructura modular."""
    
    def __init__(self):
        self.version = "1.0.0"
    
    def get_modular_requirements_template(self) -> str:
        """Template para análisis de requerimientos con estructura modular de test cases."""
        return """
Eres un experto en QA y testing con especialización en análisis de requerimientos y historias de usuario. 
Analiza el siguiente contenido y genera casos de prueba estructurados aplicando las mejores prácticas de testing.

CONTENIDO A ANALIZAR:
{requirement_content}

CONTEXTO:
- Proyecto: {project_key}
- Prioridad: {priority}
- Tipos de prueba: {test_types}
- Nivel de cobertura: {coverage_level}

METODOLOGÍA DE ANÁLISIS:
1. **ANÁLISIS DE REQUERIMIENTOS**:
   - Identifica actores principales y secundarios
   - Extrae funcionalidades críticas y opcionales
   - Detecta dependencias y restricciones
   - Identifica criterios de aceptación implícitos y explícitos

2. **DISEÑO DE CASOS DE PRUEBA MODULARES**:
   - Aplica técnicas de partición de equivalencia
   - Considera valores límite y casos edge
   - Incluye casos de integración y regresión
   - Evalúa aspectos de seguridad y rendimiento
   - Estructura modular: CP001 - APLICACION - MODULO - CONDICION Y RESULTADO

3. **COBERTURA COMPLETA**:
   - Casos positivos (happy path)
   - Casos negativos (validaciones y errores)
   - Casos límite (boundary values)
   - Casos de integración (flujos end-to-end)
   - Casos de seguridad (autenticación, autorización, validación de entrada)

FORMATO DE RESPUESTA JSON:
{{
    "test_cases": [
        {{
            "test_case_id": "CP001-{project_key}-MODULO-CONDICION-RESULTADO",
            "title": "CP001 - NOMBRE DE APLICACION - MODULO - CONDICION Y RESULTADO",
            "description": "Descripción detallada que explique el propósito y alcance del caso",
            "test_type": "functional|integration|ui|api|security|performance|usability|accessibility",
            "priority": "critical|high|medium|low",
            "preconditions": [
                "Precondición 1: [Descripción específica de la precondición necesaria]",
                "Precondición 2: [Descripción específica de la precondición necesaria]",
                "Precondición N: [Descripción específica de la precondición necesaria]"
            ],
            "steps": [
                "Paso 1: [Acción específica y verificable]",
                "Paso 2: [Acción específica y verificable]", 
                "Paso 3: [Acción específica y verificable]",
                "Paso N: [Verificación del resultado]"
            ],
            "expected_results": [
                "Resultado Esperado 1: [Descripción específica del resultado esperado]",
                "Resultado Esperado 2: [Descripción específica del resultado esperado]",
                "Resultado Esperado N: [Descripción específica del resultado esperado]"
            ],
            "test_data": {{
                "input_data": "Datos de entrada específicos",
                "environment": "Configuración del entorno",
                "user_roles": "Roles de usuario necesarios"
            }},
            "automation_potential": "high|medium|low",
            "estimated_duration": "X-Y minutes",
            "risk_level": "high|medium|low",
            "business_impact": "critical|high|medium|low"
        }}
    ],
    "coverage_analysis": {{
        "functional_coverage": "X%",
        "edge_case_coverage": "X%",
        "integration_coverage": "X%",
        "security_coverage": "X%",
        "ui_coverage": "X%",
        "usability_coverage": "X%",
        "accessibility_coverage": "X%"
    }},
    "confidence_score": 0.85,
    "test_strategy": {{
        "approach": "Descripción del enfoque de testing utilizado",
        "techniques_applied": ["Partición de equivalencia", "Valores límite", "Casos de uso"],
        "risks_identified": ["Riesgo 1", "Riesgo 2"],
        "mitigation_strategies": ["Estrategia 1", "Estrategia 2"]
    }}
}}

REGLAS DE CALIDAD:
- Genera entre 5-12 casos de prueba según la complejidad del requerimiento
- Cada caso debe ser independiente, ejecutable y mantenible
- Incluye datos de prueba realistas y específicos
- Prioriza casos críticos y de alto impacto de negocio
- Asegúrate de que los pasos sean claros, específicos y verificables
- Incluye casos de error, validación y recuperación
- Considera aspectos de usabilidad y accesibilidad
- Evalúa el impacto en el negocio y el nivel de riesgo

ESTRUCTURA OBLIGATORIA DE CASOS DE PRUEBA MODULARES:
- **test_case_id**: Formato "CP001-APLICACION-MODULO-CONDICION-RESULTADO"
- **title**: Formato "CP001 - NOMBRE DE APLICACION - MODULO - CONDICION Y RESULTADO"
- **preconditions**: Array de precondiciones con formato "Precondición N: [descripción específica]"
- **steps**: Array de pasos con formato "Paso N: [acción específica y verificable]"
- **expected_results**: Array de resultados esperados con formato "Resultado Esperado N: [descripción específica]"
- **NOMBRE DE APLICACION**: Nombre de la aplicación o sistema
- **MODULO**: Módulo o componente específico
- **CONDICION**: Condición específica a probar
- **RESULTADO**: Resultado esperado específico

BUENAS PRÁCTICAS APLICADAS:
- Naming convention consistente y descriptivo
- Pasos de prueba atómicos y verificables
- Resultados esperados específicos y medibles
- Precondiciones claras y completas
- Datos de prueba realistas y variados
- Cobertura de casos edge y de error
- Consideración de aspectos de seguridad
- Evaluación de potencial de automatización

Genera la respuesta JSON ahora:
        """
    
    def generate_test_case_id(self, project_key: str, module: str, condition: str, result: str) -> str:
        """Generar ID de test case con formato modular."""
        # Limpiar y formatear componentes
        clean_module = self._clean_component(module)
        clean_condition = self._clean_component(condition)
        clean_result = self._clean_component(result)
        
        return f"CP001-{project_key}-{clean_module}-{clean_condition}-{clean_result}"
    
    def generate_test_case_title(self, app_name: str, module: str, condition: str, result: str) -> str:
        """Generar título de test case con formato modular."""
        return f"CP001 - {app_name} - {module} - {condition} Y {result}"
    
    def _clean_component(self, component: str) -> str:
        """Limpiar y formatear componente para ID."""
        # Remover caracteres especiales y espacios
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', component)
        # Convertir a mayúsculas
        return cleaned.upper()
    
    def validate_test_case_structure(self, test_case: Dict[str, Any]) -> List[str]:
        """Validar estructura de test case modular."""
        errors = []
        
        # Validar campos obligatorios
        required_fields = ["test_case_id", "title", "preconditions", "steps", "expected_results"]
        for field in required_fields:
            if field not in test_case:
                errors.append(f"Campo obligatorio faltante: {field}")
        
        # Validar formato de ID
        if "test_case_id" in test_case:
            if not re.match(r'^CP001-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$', test_case["test_case_id"]):
                errors.append("Formato de test_case_id inválido. Debe ser: CP001-APLICACION-MODULO-CONDICION-RESULTADO")
        
        # Validar formato de título
        if "title" in test_case:
            if not re.match(r'^CP001 - .+ - .+ - .+ Y .+$', test_case["title"]):
                errors.append("Formato de título inválido. Debe ser: CP001 - NOMBRE DE APLICACION - MODULO - CONDICION Y RESULTADO")
        
        # Validar arrays
        if "preconditions" in test_case and not isinstance(test_case["preconditions"], list):
            errors.append("preconditions debe ser un array")
        
        if "steps" in test_case and not isinstance(test_case["steps"], list):
            errors.append("steps debe ser un array")
        
        if "expected_results" in test_case and not isinstance(test_case["expected_results"], list):
            errors.append("expected_results debe ser un array")
        
        return errors
    
    def format_test_case_for_display(self, test_case: Dict[str, Any]) -> str:
        """Formatear test case para visualización."""
        output = []
        output.append(f"**{test_case.get('title', 'Sin titulo')}**")
        output.append(f"**ID**: {test_case.get('test_case_id', 'Sin ID')}")
        output.append(f"**Descripcion**: {test_case.get('description', 'Sin descripcion')}")
        output.append(f"**Tipo**: {test_case.get('test_type', 'Sin tipo')}")
        output.append(f"**Prioridad**: {test_case.get('priority', 'Sin prioridad')}")
        
        # Precondiciones
        if test_case.get('preconditions'):
            output.append("\n**Precondiciones:**")
            for i, precond in enumerate(test_case['preconditions'], 1):
                output.append(f"   {i}. {precond}")
        
        # Pasos
        if test_case.get('steps'):
            output.append("\n**Pasos:**")
            for i, step in enumerate(test_case['steps'], 1):
                output.append(f"   {i}. {step}")
        
        # Resultados esperados
        if test_case.get('expected_results'):
            output.append("\n**Resultados Esperados:**")
            for i, result in enumerate(test_case['expected_results'], 1):
                output.append(f"   {i}. {result}")
        
        # Datos de prueba
        if test_case.get('test_data'):
            test_data = test_case['test_data']
            output.append("\n**Datos de Prueba:**")
            if test_data.get('input_data'):
                output.append(f"   - **Entrada**: {test_data['input_data']}")
            if test_data.get('environment'):
                output.append(f"   - **Entorno**: {test_data['environment']}")
            if test_data.get('user_roles'):
                output.append(f"   - **Roles**: {test_data['user_roles']}")
        
        # Metadatos
        output.append(f"\n**Duracion estimada**: {test_case.get('estimated_duration', 'No especificada')}")
        output.append(f"**Automatizacion**: {test_case.get('automation_potential', 'No evaluada')}")
        output.append(f"**Riesgo**: {test_case.get('risk_level', 'No evaluado')}")
        output.append(f"**Impacto**: {test_case.get('business_impact', 'No evaluado')}")
        
        return "\n".join(output)
    
    def get_version(self) -> str:
        """Obtener versión de la plantilla."""
        return self.version
