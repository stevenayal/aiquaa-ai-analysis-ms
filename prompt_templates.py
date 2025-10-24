"""
Prompt Templates Versionados
Plantillas de prompts para diferentes tipos de análisis QA
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()

class PromptTemplates:
    """Gestor de plantillas de prompts versionadas"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Inicializar plantillas de prompts"""
        return {
            "analysis": {
                "version": "1.0.0",
                "template": self._get_analysis_template(),
                "variables": ["test_case_content", "project_key", "priority", "labels"]
            },
            "improvement": {
                "version": "1.0.0", 
                "template": self._get_improvement_template(),
                "variables": ["test_case_content", "current_issues"]
            },
            "scenario_generation": {
                "version": "1.0.0",
                "template": self._get_scenario_template(),
                "variables": ["test_case_content", "test_type"]
            },
            "quality_assessment": {
                "version": "1.0.0",
                "template": self._get_quality_template(),
                "variables": ["test_case_content", "quality_criteria"]
            },
            # NUEVOS
            "modular_generation": {
                "version": "1.0.0",
                "template": self._get_modular_generation_template(),
                "variables": ["programa", "modulos", "condiciones", "variantes", "cantidad_max"]
            },
            "cp_briefs": {
                "version": "1.0.0",
                "template": self._get_cp_briefs_template(),
                "variables": ["programa", "modulos", "condiciones", "cantidad_max"]
            },
            "requirements_analysis": {
                "version": "1.0.0",
                "template": self._get_requirements_analysis_template(),
                "variables": ["requirement_content", "project_key", "priority", "test_types", "coverage_level"]
            },
            "jira_workitem_analysis": {
                "version": "1.0.0",
                "template": self._get_jira_workitem_analysis_template(),
                "variables": ["work_item_data", "requirement_content", "project_key", "test_types", "coverage_level"]
            },
            "istqb_test_generation": {
                "version": "1.0.0",
                "template": self._get_istqb_test_generation_template(),
                "variables": ["programa", "dominio", "modulos", "factores", "limites", "reglas", "tecnicas", "priorizacion", "cantidad_max", "salida_plan_ejecucion"]
            },
            "confluence_test_plan": {
                "version": "1.0.0",
                "template": self._get_confluence_test_plan_template(),
                "variables": ["jira_data", "test_plan_title", "test_strategy", "include_automation", "include_performance", "include_security", "confluence_space_key"]
            }
        }
    
    def get_analysis_prompt(
        self,
        test_case_content: str,
        project_key: str,
        priority: str = "Medium",
        labels: Optional[List[str]] = None
    ) -> str:
        """Obtener prompt para análisis de caso de prueba"""
        try:
            template_data = self.templates["analysis"]
            template = template_data["template"]
            
            # Preparar variables
            labels_str = ", ".join(labels) if labels else "N/A"
            
            # Reemplazar variables en el template
            prompt = template.format(
                test_case_content=test_case_content,
                project_key=project_key,
                priority=priority,
                labels=labels_str,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info("Analysis prompt generated", project_key=project_key, priority=priority)
            return prompt
            
        except Exception as e:
            logger.error("Error generating analysis prompt", error=str(e))
            return self._get_fallback_analysis_prompt(test_case_content)
    
    def get_improvement_prompt(
        self,
        test_case_content: str,
        current_issues: Optional[List[str]] = None
    ) -> str:
        """Obtener prompt para sugerencias de mejora"""
        try:
            template_data = self.templates["improvement"]
            template = template_data["template"]
            
            issues_str = "\n".join([f"- {issue}" for issue in current_issues]) if current_issues else "Ninguno identificado"
            
            prompt = template.format(
                test_case_content=test_case_content,
                current_issues=issues_str,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info("Improvement prompt generated")
            return prompt
            
        except Exception as e:
            logger.error("Error generating improvement prompt", error=str(e))
            return self._get_fallback_improvement_prompt(test_case_content)
    
    def get_scenario_generation_prompt(
        self,
        test_case_content: str,
        test_type: str = "functional"
    ) -> str:
        """Obtener prompt para generación de escenarios"""
        try:
            template_data = self.templates["scenario_generation"]
            template = template_data["template"]
            
            prompt = template.format(
                test_case_content=test_case_content,
                test_type=test_type,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info("Scenario generation prompt created", test_type=test_type)
            return prompt
            
        except Exception as e:
            logger.error("Error generating scenario prompt", error=str(e))
            return self._get_fallback_scenario_prompt(test_case_content)
    
    def get_quality_assessment_prompt(
        self,
        test_case_content: str,
        quality_criteria: Optional[List[str]] = None
    ) -> str:
        """Obtener prompt para evaluación de calidad"""
        try:
            template_data = self.templates["quality_assessment"]
            template = template_data["template"]
            
            criteria_str = "\n".join([f"- {criteria}" for criteria in quality_criteria]) if quality_criteria else self._get_default_quality_criteria()
            
            prompt = template.format(
                test_case_content=test_case_content,
                quality_criteria=criteria_str,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info("Quality assessment prompt generated")
            return prompt
            
        except Exception as e:
            logger.error("Error generating quality assessment prompt", error=str(e))
            return self._get_fallback_quality_prompt(test_case_content)
    
    def get_modular_generation_prompt(
        self,
        programa: str,
        modulos: List[str],
        condiciones: List[str],
        variantes: Optional[List[str]] = None,
        cantidad_max: int = 200
    ) -> str:
        """Método para CSV de CPs (CP - NNN - ...)"""
        try:
            template = self.templates["modular_generation"]["template"]
            prompt = template.format(
                programa=programa.upper().strip(),
                modulos=", ".join([m.upper().strip() for m in modulos]),
                condiciones=", ".join([c.upper().strip() for c in condiciones]),
                variantes=", ".join([v.upper().strip() for v in variantes]) if variantes else "N/A",
                cantidad_max=cantidad_max,
                timestamp=datetime.utcnow().isoformat()
            )
            logger.info("Modular generation prompt created",
                        programa=programa, cantidad_max=cantidad_max)
            return prompt
        except Exception as e:
            logger.error("Error generating modular generation prompt", error=str(e))
            return f"Genera CSV sin encabezado: CP - NNN - {programa.upper()} - MODULO - CONDICION - ESCENARIO "\
                   f"usando MODULOS={modulos} y CONDICIONES={condiciones}. Máx: {cantidad_max}."
    
    def get_cp_briefs_prompt(
        self,
        programa: str,
        modulos: List[str],
        condiciones: List[str],
        cantidad_max: int = 50
    ) -> str:
        """
        Genera prompt para devolver bloques en formato:
        1 - CP - NNN - PROGRAMA - MODULO - CONDICION - ESCENARIO
        2- Precondicion: ...
        3- Resultado Esperado: ...
        """
        try:
            template = self.templates["cp_briefs"]["template"]
            prompt = template.format(
                programa=programa.upper().strip(),
                modulos=", ".join([m.upper().strip() for m in modulos]),
                condiciones=", ".join([c.upper().strip() for c in condiciones]),
                cantidad_max=cantidad_max,
                timestamp=datetime.utcnow().isoformat()
            )
            logger.info("CP briefs prompt created", programa=programa, cantidad_max=cantidad_max)
            return prompt
        except Exception as e:
            logger.error("Error generating cp briefs prompt", error=str(e))
            # Fallback mínimo
            return (
                f"Genera {cantidad_max} bloques con el formato exacto:\n"
                f"1 - CP - NNN - {programa.upper()} - MODULO - CONDICION - ESCENARIO\n"
                "2- Precondicion: <texto breve y concreto>\n"
                "3- Resultado Esperado: <resultado verificable>\n"
                f"Usá MODULOS={modulos} y CONDICIONES={condiciones}. Solo los bloques, sin texto extra."
            )
    
    def get_requirements_analysis_prompt(
        self,
        requirement_content: str,
        project_key: str,
        priority: str = "Medium",
        test_types: Optional[List[str]] = None,
        coverage_level: str = "medium"
    ) -> str:
        """Obtener prompt para análisis de requerimientos y generación de casos de prueba"""
        try:
            template_data = self.templates["requirements_analysis"]
            template = template_data["template"]
            
            # Preparar variables
            test_types_str = ", ".join(test_types) if test_types else "functional, integration"
            
            # Reemplazar variables en el template
            prompt = template.format(
                requirement_content=requirement_content,
                project_key=project_key,
                priority=priority,
                test_types=test_types_str,
                coverage_level=coverage_level,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info("Requirements analysis prompt generated", 
                       project_key=project_key, priority=priority, coverage_level=coverage_level)
            return prompt
            
        except Exception as e:
            logger.error("Error generating requirements analysis prompt", error=str(e))
            return self._get_fallback_requirements_prompt(requirement_content)
    
    def _get_analysis_template(self) -> str:
        """Template mejorado para análisis de casos de prueba existentes"""
        return """
Eres un experto en QA y testing con más de 10 años de experiencia en análisis de casos de prueba y mejora continua de procesos de testing.
Analiza el siguiente caso de prueba y proporciona sugerencias de mejora basadas en las mejores prácticas de la industria.

CONTEXTO:
- Proyecto: {project_key}
- Prioridad: {priority}
- Etiquetas: {labels}
- Timestamp: {timestamp}

CASO DE PRUEBA A ANALIZAR:
{test_case_content}

METODOLOGÍA DE ANÁLISIS:
1. **EVALUACIÓN DE CALIDAD**:
   - Claridad y legibilidad del caso
   - Completitud de pasos y verificaciones
   - Especificidad de resultados esperados
   - Consistencia en nomenclatura y formato

2. **ANÁLISIS DE COBERTURA**:
   - Cobertura de casos positivos y negativos
   - Inclusión de casos edge y boundary values
   - Cobertura de integración y regresión
   - Consideración de aspectos de seguridad

3. **EVALUACIÓN DE MANTENIBILIDAD**:
   - Facilidad de mantenimiento y actualización
   - Reutilización de componentes
   - Documentación y comentarios
   - Estructura modular y organizada

4. **POTENCIAL DE AUTOMATIZACIÓN**:
   - Viabilidad técnica de automatización
   - Herramientas y frameworks recomendados
   - Estrategias de implementación
   - Consideraciones de mantenimiento

FORMATO DE RESPUESTA JSON:
{{
    "summary": "Resumen ejecutivo del análisis en 2-3 oraciones",
    "confidence_score": 0.85,
    "suggestions": [
        {{
            "type": "clarity|coverage|best_practice|automation|maintainability|security|performance",
            "title": "Título específico y accionable de la sugerencia",
            "description": "Descripción detallada de la mejora con ejemplos concretos",
            "priority": "critical|high|medium|low",
            "category": "improvement|bug_fix|enhancement|optimization|security|performance",
            "effort": "low|medium|high",
            "impact": "low|medium|high",
            "implementation_guidance": "Pasos específicos para implementar la mejora",
            "expected_benefit": "Beneficio esperado de la mejora",
            "related_standards": ["ISO 25010", "ISTQB", "IEEE 829"]
        }}
    ],
    "improved_test_cases": [
        {{
            "test_case_id": "CP-001-APLICACION-MODULO-DATO-CONDICION-RESULTADO",
            "title": "CP - 001 - Aplicacion - Modulo - Dato - Condicion - Resultado",
            "preconditions": "Precondicion: [Descripción específica de las precondiciones necesarias]",
            "expected_result": "Resultado Esperado: [Descripción específica del resultado esperado]",
            "description": "Descripción detallada del caso de prueba mejorado"
        }}
    ],
    "quality_metrics": {{
        "clarity_score": 0.85,
        "completeness_score": 0.90,
        "maintainability_score": 0.75,
        "automation_readiness": 0.80,
        "coverage_score": 0.70,
        "security_consideration": 0.65
    }},
    "categories": ["clarity", "coverage", "automation", "maintainability"],
    "overall_quality_score": 0.75,
    "quality_grade": "A|B|C|D|F",
    "strengths": [
        "Fortaleza identificada 1",
        "Fortaleza identificada 2"
    ],
    "weaknesses": [
        "Debilidad identificada 1",
        "Debilidad identificada 2"
    ],
    "recommendations": [
        "Recomendación específica y accionable 1",
        "Recomendación específica y accionable 2"
    ],
    "compliance_check": {{
        "standards_met": ["ISO 25010", "ISTQB Foundation"],
        "compliance_score": 0.85,
        "non_compliant_areas": ["Área 1", "Área 2"],
        "improvement_areas": ["Área de mejora 1", "Área de mejora 2"]
    }},
    "automation_assessment": {{
        "feasibility": "high|medium|low",
        "recommended_tools": ["Selenium", "Playwright", "Cypress"],
        "implementation_effort": "low|medium|high",
        "maintenance_considerations": "Consideraciones específicas de mantenimiento"
    }}
}}

CRITERIOS DE EVALUACIÓN:
- **Claridad**: El caso es fácil de entender y seguir
- **Completitud**: Incluye todos los pasos y verificaciones necesarias
- **Mantenibilidad**: Fácil de actualizar y mantener
- **Automatización**: Preparado para automatización
- **Cobertura**: Cubre diferentes escenarios y casos edge
- **Seguridad**: Considera aspectos de seguridad
- **Rendimiento**: Evalúa impactos en rendimiento
- **Estándares**: Cumple con estándares de la industria

BUENAS PRÁCTICAS APLICADAS:
- Análisis basado en estándares ISO 25010 e ISTQB
- Evaluación de viabilidad de automatización
- Consideración de aspectos de seguridad y rendimiento
- Recomendaciones específicas y accionables
- Métricas de calidad cuantificables
- Evaluación de cumplimiento de estándares

Responde SOLO con el JSON válido, sin texto adicional.
"""
    
    def _get_improvement_template(self) -> str:
        """Template para sugerencias de mejora"""
        return """
Eres un consultor de QA senior. Analiza el caso de prueba y proporciona mejoras específicas.

CASO DE PRUEBA:
{test_case_content}

PROBLEMAS IDENTIFICADOS:
{current_issues}

INSTRUCCIONES:
Proporciona mejoras específicas y accionables en formato JSON. Considera:

1. Mejoras de claridad y legibilidad
2. Cobertura de casos de prueba adicionales
3. Optimización para automatización
4. Mejores prácticas de testing
5. Mantenibilidad a largo plazo

FORMATO DE RESPUESTA JSON:
{{
    "improvements": [
        {{
            "category": "clarity|coverage|automation|maintainability|performance",
            "title": "Título de la mejora",
            "description": "Descripción detallada",
            "priority": "high|medium|low",
            "effort": "low|medium|high",
            "impact": "low|medium|high",
            "implementation_steps": [
                "Paso 1: Descripción específica",
                "Paso 2: Descripción específica"
            ],
            "expected_benefit": "Beneficio esperado de la mejora"
        }}
    ],
    "priority_order": ["high", "medium", "low"],
    "estimated_effort": "low|medium|high",
    "expected_impact": "low|medium|high"
}}

Responde SOLO con el JSON válido.
"""
    
    def _get_scenario_template(self) -> str:
        """Template para generación de escenarios"""
        return """
Eres un especialista en testing. Genera escenarios de prueba detallados basados en el caso de prueba.

CASO DE PRUEBA:
{test_case_content}

TIPO DE TEST: {test_type}

INSTRUCCIONES:
Genera escenarios de prueba específicos que cubran diferentes aspectos:

1. CASO FELIZ (Happy Path)
2. CASOS DE ERROR
3. CASOS LÍMITE (Edge Cases)
4. CASOS DE INTEGRACIÓN
5. CASOS DE RENDIMIENTO (si aplica)

FORMATO DE RESPUESTA JSON:
{{
    "scenarios": [
        {{
            "name": "Nombre descriptivo del escenario",
            "description": "Descripción detallada del escenario",
            "type": "happy_path|error_case|edge_case|integration|performance",
            "priority": "high|medium|low",
            "steps": [
                "Paso 1: Acción específica",
                "Paso 2: Acción específica",
                "Paso 3: Verificación"
            ],
            "test_data": {{
                "input": "Datos de entrada específicos",
                "expected_output": "Resultado esperado",
                "preconditions": "Condiciones previas"
            }},
            "assertions": [
                "Verificación 1",
                "Verificación 2"
            ],
            "automation_potential": "high|medium|low",
            "estimated_duration": "5-10 minutes"
        }}
    ],
    "coverage_analysis": {{
        "functional_coverage": "85%",
        "edge_case_coverage": "70%",
        "integration_coverage": "60%"
    }},
    "recommendations": [
        "Recomendación para mejorar cobertura",
        "Sugerencia de automatización"
    ]
}}

Responde SOLO con el JSON válido.
"""
    
    def _get_quality_template(self) -> str:
        """Template para evaluación de calidad"""
        return """
Eres un auditor de calidad de software. Evalúa la calidad del caso de prueba.

CASO DE PRUEBA:
{test_case_content}

CRITERIOS DE CALIDAD:
{quality_criteria}

INSTRUCCIONES:
Evalúa el caso de prueba contra los criterios de calidad y proporciona una puntuación detallada.

FORMATO DE RESPUESTA JSON:
{{
    "quality_scores": {{
        "clarity": 0.85,
        "completeness": 0.90,
        "maintainability": 0.75,
        "automation_readiness": 0.80,
        "coverage": 0.70
    }},
    "overall_score": 0.80,
    "grade": "A|B|C|D|F",
    "strengths": [
        "Fortaleza 1",
        "Fortaleza 2"
    ],
    "weaknesses": [
        "Debilidad 1",
        "Debilidad 2"
    ],
    "improvement_areas": [
        "Área de mejora 1",
        "Área de mejora 2"
    ],
    "compliance": {{
        "standards": "ISO 25010",
        "compliance_score": 0.85,
        "non_compliant_items": []
    }},
    "recommendations": [
        "Recomendación específica 1",
        "Recomendación específica 2"
    ]
}}

Responde SOLO con el JSON válido.
"""
    
    def _get_modular_generation_template(self) -> str:
        """Template para generación modular de casos de prueba"""
        return """
Eres un generador estricto de CASOS DE PRUEBA por DISEÑO MODULAR.

METADATOS:
- PROGRAMA: {programa}
- MODULOS: {modulos}
- CONDICIONES: {condiciones}
- VARIANTES/EDICIONES: {variantes}
- MAX_FILAS: {cantidad_max}
- TIMESTAMP: {timestamp}

OBJETIVO:
Producir exclusivamente líneas CSV (sin encabezado) con el patrón EXACTO:
CP - NNN - PROGRAMA - MODULO - CONDICION - ESCENARIO

REGLAS:
1) NNN inicia en 001, sin saltos.
2) PROGRAMA = {programa}.
3) MODULO ∈ MODULOS.
4) CONDICION ∈ CONDICIONES (átoma).
5) ESCENARIO: MAYÚSCULAS, verbo + resultado (≤12 palabras).
6) Sin texto adicional.
7) Cobertura mínima por módulo: ≥1 caso feliz y ≥1 caso error.
8) Si hay fallas remotas (p.ej., TIMEOUT/SIN_CONEXION), al menos 1 caso con RETRY o MARCADO PENDIENTE.
9) Si VARIANTES ≠ N/A, duplicar solo cuando cambie el comportamiento.
10) Priorizar alto riesgo en los primeros 30.
11) Máximo {cantidad_max} filas.

SALIDA: SOLO el CSV.
""".strip()
    
    def _get_cp_briefs_template(self) -> str:
        """Template para fichas de caso de prueba"""
        return """
Eres un generador de fichas de caso de prueba. Para cada caso, entrega EXACTAMENTE tres líneas:

1 - CP - NNN - PROGRAMA - MODULO - CONDICION - ESCENARIO
2- Precondicion: <precondición concreta, verificable, breve>
3- Resultado Esperado: <resultado observable y medible>

PARÁMETROS:
- PROGRAMA: {programa}
- MODULOS: {modulos}
- CONDICIONES: {condiciones}
- MAX_CASOS: {cantidad_max}
- TIMESTAMP: {timestamp}

REGLAS:
- NNN desde 001, correlativo sin saltos.
- MODULO debe ser uno de MODULOS.
- CONDICION debe ser una de CONDICIONES.
- ESCENARIO en MAYÚSCULAS, verbo + resultado (≤12 palabras).
- Precondición: estado del sistema/datos previos/flags/roles necesarios.
- Resultado esperado: incluir estado final + efectos (persistencia, logs, eventos, códigos).
- Cobertura: por cada MÓDULO, al menos 1 caso feliz y 1 de error.
- No incluir texto extra, encabezados ni viñetas entre casos.
- Generar hasta MAX_CASOS.

EJEMPLO DE FORMA (NO lo repitas si no aplica):
1 - CP - 001 - {programa} - AUTORIZACION - INPUT_VALIDO - AUTORIZA Y REGISTRA OPERACION
2- Precondicion: Usuario activo; datos completos; firma válida.
3- Resultado Esperado: Operación autorizada; ID transacción generado; registro persistido y auditado.

Ahora genera los casos.
""".strip()
    
    def _get_default_quality_criteria(self) -> str:
        """Criterios de calidad por defecto"""
        return """
- Claridad: El caso de prueba es fácil de entender
- Completitud: Incluye todos los pasos necesarios
- Mantenibilidad: Fácil de actualizar y mantener
- Automatización: Preparado para automatización
- Cobertura: Cubre diferentes escenarios
- Datos de prueba: Incluye datos de prueba apropiados
- Naming: Sigue convenciones de nomenclatura
- Documentación: Bien documentado
"""
    
    def _get_fallback_analysis_prompt(self, test_case_content: str) -> str:
        """Prompt de fallback para análisis"""
        return f"""
Analiza este caso de prueba y proporciona sugerencias de mejora:

{test_case_content}

Proporciona sugerencias en formato JSON con campos: suggestions, confidence_score, summary.
"""
    
    def _get_fallback_improvement_prompt(self, test_case_content: str) -> str:
        """Prompt de fallback para mejoras"""
        return f"""
Sugiere mejoras para este caso de prueba:

{test_case_content}

Proporciona mejoras en formato JSON con campos: improvements, priority_order.
"""
    
    def _get_fallback_scenario_prompt(self, test_case_content: str) -> str:
        """Prompt de fallback para escenarios"""
        return f"""
Genera escenarios de prueba para:

{test_case_content}

Proporciona escenarios en formato JSON con campos: scenarios, coverage_analysis.
"""
    
    def _get_fallback_quality_prompt(self, test_case_content: str) -> str:
        """Prompt de fallback para calidad"""
        return f"""
Evalúa la calidad de este caso de prueba:

{test_case_content}

Proporciona evaluación en formato JSON con campos: quality_scores, overall_score, recommendations.
"""
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Obtener información de una plantilla"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """Listar todas las plantillas disponibles"""
        return list(self.templates.keys())
    
    def get_version(self) -> str:
        """Obtener versión actual de las plantillas"""
        return self.version
    
    def _get_requirements_analysis_template(self) -> str:
        """Template mejorado para análisis de requerimientos y generación de casos de prueba"""
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

2. **DISEÑO DE CASOS DE PRUEBA**:
   - Aplica técnicas de partición de equivalencia
   - Considera valores límite y casos edge
   - Incluye casos de integración y regresión
   - Evalúa aspectos de seguridad y rendimiento

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
            "test_case_id": "CP-001-{project_key}-MODULO-DATO-CONDICION-RESULTADO",
            "title": "CP - 001 - Aplicacion - Modulo - Dato - Condicion - Resultado",
            "description": "Descripción detallada que explique el propósito y alcance del caso",
            "test_type": "functional|integration|ui|api|security|performance|usability|accessibility",
            "priority": "critical|high|medium|low",
            "steps": [
                "Paso 1: Acción específica y verificable",
                "Paso 2: Acción específica y verificable",
                "Paso N: Verificación del resultado"
            ],
            "expected_result": "Resultado Esperado: [Descripción específica del resultado esperado]",
            "preconditions": [
                "Precondicion: [Descripción específica de las precondiciones necesarias]"
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

ESTRUCTURA OBLIGATORIA DE CASOS DE PRUEBA:
- **test_case_id**: Formato "CP-001-APLICACION-MODULO-DATO-CONDICION-RESULTADO"
- **title**: Formato "CP - 001 - Aplicacion - Modulo - Dato - Condicion - Resultado"
- **expected_result**: Formato "Resultado Esperado: [descripción específica]"
- **preconditions**: Formato "Precondicion: [descripción específica]"
- **Aplicacion**: Nombre de la aplicación o sistema
- **Modulo**: Módulo o componente específico
- **Dato**: Tipo de dato o entrada específica
- **Condicion**: Condición específica a probar
- **Resultado**: Resultado esperado específico

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
    
    def _get_fallback_requirements_prompt(self, requirement_content: str) -> str:
        """Prompt de fallback para análisis de requerimientos"""
        return f"""
Analiza el siguiente requerimiento y genera casos de prueba:

{requirement_content}

Genera casos de prueba en formato JSON con:
- test_case_id
- title
- description
- test_type
- priority
- steps
- expected_result
- preconditions
- test_data
- automation_potential
- estimated_duration

Incluye también coverage_analysis y confidence_score.
        """
    
    def get_jira_workitem_analysis_prompt(
        self,
        work_item_data: Dict[str, Any],
        requirement_content: str,
        project_key: str,
        test_types: Optional[List[str]] = None,
        coverage_level: str = "medium"
    ) -> str:
        """Obtener prompt para análisis de work item de Jira y generación de casos de prueba"""
        try:
            template_data = self.templates["jira_workitem_analysis"]
            template = template_data["template"]
            
            # Preparar variables
            test_types_str = ", ".join(test_types) if test_types else "functional, integration"
            
            # Reemplazar variables en el template
            prompt = template.format(
                work_item_data=work_item_data,
                requirement_content=requirement_content,
                project_key=project_key,
                test_types=test_types_str,
                coverage_level=coverage_level,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info("Jira work item analysis prompt generated", 
                       project_key=project_key, 
                       work_item_id=work_item_data.get("key", ""),
                       coverage_level=coverage_level)
            return prompt
            
        except Exception as e:
            logger.error("Error generating Jira work item analysis prompt", error=str(e))
            return self._get_fallback_jira_workitem_prompt(work_item_data, requirement_content)
    
    def _get_jira_workitem_analysis_template(self) -> str:
        """Template mejorado para análisis de work item de Jira y generación de casos de prueba"""
        return """
Eres un experto en QA y testing con especialización en análisis de work items de Jira y generación de casos de prueba basados en historias de usuario y requerimientos.
Analiza el siguiente work item de Jira y genera casos de prueba estructurados aplicando las mejores prácticas de testing ágil.

DATOS DEL WORK ITEM:
{work_item_data}

CONTENIDO DEL REQUERIMIENTO:
{requirement_content}

CONTEXTO:
- Proyecto: {project_key}
- Tipos de prueba: {test_types}
- Nivel de cobertura: {coverage_level}
- Timestamp: {timestamp}

METODOLOGÍA DE ANÁLISIS PARA JIRA:
1. **ANÁLISIS DEL WORK ITEM**:
   - Identifica el tipo de issue (Story, Task, Bug, Epic)
   - Extrae criterios de aceptación explícitos e implícitos
   - Analiza la descripción y campos personalizados
   - Considera la prioridad y el estado actual
   - Identifica dependencias y relaciones con otros issues

2. **DISEÑO DE CASOS DE PRUEBA ÁGILES**:
   - Aplica técnicas de testing basadas en comportamiento (BDD)
   - Considera el contexto del usuario y el valor de negocio
   - Incluye casos de aceptación y criterios de "Definition of Done"
   - Evalúa aspectos de usabilidad y experiencia de usuario
   - Considera integración con otros sistemas y APIs

3. **COBERTURA COMPLETA**:
   - Casos positivos (happy path) basados en criterios de aceptación
   - Casos negativos (validaciones y manejo de errores)
   - Casos límite (boundary values y edge cases)
   - Casos de integración (flujos end-to-end)
   - Casos de regresión (impacto en funcionalidades existentes)
   - Casos de seguridad (autenticación, autorización, validación de entrada)

FORMATO DE RESPUESTA JSON:
{{
    "test_cases": [
        {{
            "test_case_id": "CP-001-{project_key}-MODULO-DATO-CONDICION-RESULTADO",
            "title": "CP - 001 - Aplicacion - Modulo - Dato - Condicion - Resultado",
            "description": "Descripción detallada que explique el propósito y alcance del caso",
            "test_type": "functional|integration|ui|api|security|performance|usability|accessibility|regression",
            "priority": "critical|high|medium|low",
            "steps": [
                "Paso 1: Acción específica y verificable",
                "Paso 2: Acción específica y verificable",
                "Paso N: Verificación del resultado"
            ],
            "expected_result": "Resultado Esperado: [Descripción específica del resultado esperado]",
            "preconditions": [
                "Precondicion: [Descripción específica de las precondiciones necesarias]"
            ],
            "test_data": {{
                "input_data": "Datos de entrada específicos",
                "environment": "Configuración del entorno",
                "user_roles": "Roles de usuario necesarios",
                "jira_context": "Contexto específico del work item"
            }},
            "automation_potential": "high|medium|low",
            "estimated_duration": "X-Y minutes",
            "risk_level": "high|medium|low",
            "business_impact": "critical|high|medium|low",
            "acceptance_criteria": [
                "Criterio de aceptación 1",
                "Criterio de aceptación 2"
            ],
            "definition_of_done": [
                "Criterio de Definition of Done 1",
                "Criterio de Definition of Done 2"
            ]
        }}
    ],
    "coverage_analysis": {{
        "functional_coverage": "X%",
        "edge_case_coverage": "X%",
        "integration_coverage": "X%",
        "security_coverage": "X%",
        "ui_coverage": "X%",
        "usability_coverage": "X%",
        "accessibility_coverage": "X%",
        "jira_integration_coverage": "X%",
        "regression_coverage": "X%"
    }},
    "confidence_score": 0.85,
    "jira_analysis": {{
        "issue_type": "Story|Task|Bug|Epic",
        "priority_level": "Highest|High|Medium|Low|Lowest",
        "complexity": "low|medium|high",
        "business_value": "high|medium|low",
        "technical_risk": "high|medium|low",
        "dependencies": ["Dependencia 1", "Dependencia 2"],
        "related_issues": ["Issue relacionado 1", "Issue relacionado 2"]
    }},
    "test_strategy": {{
        "approach": "Descripción del enfoque de testing utilizado",
        "techniques_applied": ["BDD", "Partición de equivalencia", "Valores límite", "Casos de uso"],
        "risks_identified": ["Riesgo 1", "Riesgo 2"],
        "mitigation_strategies": ["Estrategia 1", "Estrategia 2"],
        "testing_phases": ["Unit", "Integration", "System", "Acceptance"]
    }}
}}

REGLAS ESPECÍFICAS PARA JIRA:
- Genera entre 5-12 casos de prueba según la complejidad del work item
- Cada caso debe ser independiente, ejecutable y mantenible
- Incluye datos de prueba realistas y específicos del contexto
- Prioriza casos críticos y de alto valor de negocio
- Asegúrate de que los pasos sean claros, específicos y verificables
- Incluye casos de error, validación y recuperación
- Considera aspectos de usabilidad y accesibilidad
- Evalúa el impacto en el negocio y el nivel de riesgo
- Incluye criterios de aceptación y Definition of Done
- Considera dependencias con otros work items

ESTRUCTURA OBLIGATORIA DE CASOS DE PRUEBA:
- **test_case_id**: Formato "CP-001-APLICACION-MODULO-DATO-CONDICION-RESULTADO"
- **title**: Formato "CP - 001 - Aplicacion - Modulo - Dato - Condicion - Resultado"
- **expected_result**: Formato "Resultado Esperado: [descripción específica]"
- **preconditions**: Formato "Precondicion: [descripción específica]"
- **Aplicacion**: Nombre de la aplicación o sistema
- **Modulo**: Módulo o componente específico
- **Dato**: Tipo de dato o entrada específica
- **Condicion**: Condición específica a probar
- **Resultado**: Resultado esperado específico

BUENAS PRÁCTICAS APLICADAS:
- Análisis basado en metodologías ágiles (Scrum, Kanban)
- Consideración del contexto de usuario y valor de negocio
- Aplicación de técnicas BDD (Behavior-Driven Development)
- Evaluación de viabilidad de automatización
- Consideración de aspectos de seguridad y rendimiento
- Recomendaciones específicas y accionables
- Métricas de calidad cuantificables
- Evaluación de cumplimiento de estándares ágiles

Genera la respuesta JSON ahora:
        """
    
    def _get_fallback_jira_workitem_prompt(self, work_item_data: Dict[str, Any], requirement_content: str) -> str:
        """Prompt de fallback para análisis de work item de Jira"""
        return f"""
Analiza el siguiente work item de Jira y genera casos de prueba:

WORK ITEM: {work_item_data.get('key', 'N/A')} - {work_item_data.get('summary', 'N/A')}
DESCRIPCIÓN: {requirement_content}

Genera casos de prueba en formato JSON con:
- test_case_id
- title
- description
- test_type
- priority
- steps
- expected_result
- preconditions
- test_data
- automation_potential
- estimated_duration

Incluye también coverage_analysis y confidence_score.
        """
    
    def get_istqb_test_generation_prompt(
        self,
        programa: str,
        dominio: str,
        modulos: List[str],
        factores: Dict[str, List[str]],
        limites: Dict[str, Any],
        reglas: List[str],
        tecnicas: Dict[str, bool],
        priorizacion: str = "Riesgo",
        cantidad_max: int = 150,
        salida_plan_ejecucion: Optional[Dict[str, Any]] = None
    ) -> str:
        """Obtener prompt para generación de casos de prueba con técnicas ISTQB"""
        try:
            template_data = self.templates["istqb_test_generation"]
            template = template_data["template"]
            
            # Preparar variables
            modulos_str = ", ".join([m.upper().strip() for m in modulos])
            factores_str = self._format_factores(factores)
            limites_str = self._format_limites(limites)
            reglas_str = "\n".join([f"- {regla}" for regla in reglas])
            tecnicas_str = self._format_tecnicas(tecnicas)
            salida_plan_str = self._format_salida_plan(salida_plan_ejecucion)
            
            # Reemplazar variables en el template
            prompt = template.format(
                programa=programa.upper().strip(),
                dominio=dominio,
                modulos=modulos_str,
                factores=factores_str,
                limites=limites_str,
                reglas=reglas_str,
                tecnicas=tecnicas_str,
                priorizacion=priorizacion,
                cantidad_max=cantidad_max,
                salida_plan_ejecucion=salida_plan_str,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info("ISTQB test generation prompt created", 
                       programa=programa, cantidad_max=cantidad_max)
            return prompt
            
        except Exception as e:
            logger.error("Error generating ISTQB test generation prompt", error=str(e))
            return self._get_fallback_istqb_prompt(programa, modulos, cantidad_max)
    
    def _format_factores(self, factores: Dict[str, List[str]]) -> str:
        """Formatear factores para el prompt"""
        formatted = []
        for factor, valores in factores.items():
            valores_str = ", ".join([f'"{v}"' for v in valores])
            formatted.append(f'"{factor}": [{valores_str}]')
        return "{\n    " + ",\n    ".join(formatted) + "\n}"
    
    def _format_limites(self, limites: Dict[str, Any]) -> str:
        """Formatear límites para el prompt"""
        formatted = []
        for limite, valor in limites.items():
            if isinstance(valor, dict):
                if "min" in valor and "max" in valor:
                    formatted.append(f'"{limite}": {{"min": {valor["min"]}, "max": {valor["max"]}}}')
                else:
                    formatted.append(f'"{limite}": {valor}')
            else:
                formatted.append(f'"{limite}": {valor}')
        return "{\n    " + ",\n    ".join(formatted) + "\n}"
    
    def _format_tecnicas(self, tecnicas: Dict[str, bool]) -> str:
        """Formatear técnicas para el prompt"""
        formatted = []
        for tecnica, activa in tecnicas.items():
            formatted.append(f'"{tecnica}": {str(activa).lower()}')
        return "{\n    " + ",\n    ".join(formatted) + "\n}"
    
    def _format_salida_plan(self, salida_plan: Optional[Dict[str, Any]]) -> str:
        """Formatear configuración de salida del plan"""
        if not salida_plan:
            return '{"incluir": false, "formato": "cursor_playwright_mcp"}'
        
        incluir = salida_plan.get("incluir", False)
        formato = salida_plan.get("formato", "cursor_playwright_mcp")
        return f'{{"incluir": {str(incluir).lower()}, "formato": "{formato}"}}'
    
    def _get_istqb_test_generation_template(self) -> str:
        """Template para generación de casos de prueba con técnicas ISTQB"""
        return """
Eres un Agente QA experto que genera artefactos de prueba aplicando técnicas de diseño ISTQB Foundation Level.

ROL: Agente QA que genera artefactos de prueba aplicando técnicas de diseño, con nombres de casos en el formato:
CP - NNN - PROGRAMA - MODULO - CONDICION - ESCENARIO.

ENTRADA (JSON de configuración):
{{
  "programa": "{programa}",
  "dominio": "{dominio}",
  "modulos": [{modulos}],
  "factores": {factores},
  "limites": {limites},
  "reglas": [
{reglas}
  ],
  "tecnicas": {tecnicas},
  "priorizacion": "{priorizacion}",
  "cantidad_max": {cantidad_max},
  "salida_plan_ejecucion": {salida_plan_ejecucion}
}}

REGLAS GLOBALES:
- CP Name: CP - NNN - {{PROGRAMA}} - {{MODULO}} - {{CONDICION}} - {{ESCENARIO}}; NNN desde 001, sin saltos.
- CONDICION: atómica y tomada de factores/eventos (p.ej. FACTOR_3_TIMEOUT, FACTOR_1_VALOR1).
- ESCENARIO: MAYÚSCULAS, verbo + resultado (≤12 palabras).
- Cobertura mínima por módulo: ≥1 caso feliz y ≥1 de error.
- Riesgo primero: priorizar alto impacto/uso en los primeros 30 CP.
- Sin duplicados semánticos.
- Todo en MAYÚSCULAS y sin texto extra salvo lo especificado.

QUÉ GENERAR (controlado por tecnicas):

Sección A — CSV (obligatorio): líneas CP - NNN - … hasta cantidad_max.

Sección B — FICHAS (obligatorio): por cada CP, exactamente 3 líneas:
1 - CP - NNN - PROGRAMA - MODULO - CONDICION - ESCENARIO
2- Precondicion: <estado/datos/roles/flags>
3- Resultado Esperado: <resultado observable/medible, efectos y auditoría>

Sección C — ARTEFACTOS TÉCNICOS (incluir solo los marcados true):
- equivalencias: particiones válidas/ inválidas por cada factor.
- valores_limite: casos min-1,min,min+1,max-1,max,max+1 para límites numéricos/longitudes.
- tabla_decision: matriz compacta Condiciones→Acciones alineada a reglas.
- transicion_estados: estados y transiciones principales del requerimiento.
- arbol_clasificacion: clases/atributos y restricciones entre factores.
- pairwise: combinaciones mínimas que cubren todas las parejas entre factores + CP asociado.
- casos_uso: flujo principal y alternos relevantes del dominio.
- error_guessing: lista de hipótesis de fallos del dominio.
- checklist: verificación genérica (mensajes claros, logs, auditoría, accesibilidad, rate-limit/quotas, idempotencia, seguridad, internacionalización, performance básica).

Sección D — Plan de Ejecución (opcional por salida_plan_ejecucion.incluir):
Si formato="cursor_playwright_mcp", entregar JSON por CP con:
steps[] (action, target/selector, value/opciones), asserts[] (assertion, target, args), artefactos (screenshot/trace), timeout_sec, tags.

No incluir secretos; enmascarar con {{secrets.*}}.

FORMATO DE SALIDA (estricto):
Entregar solo las secciones en este orden exacto:
A) CSV → B) FICHAS → C) ARTEFACTOS TÉCNICOS → D) PLAN (si aplica).

No agregar prólogos, epílogos ni comentarios fuera de las secciones.

GUÍA DE MAPEO VARIABLE→CONTENIDO:
- PROGRAMA ← programa.
- MODULO ← un elemento de modulos.
- CONDICION ← combinación atomizada de factores/eventos (<FACTOR>_<VALOR>).
- ESCENARIO ← derivado de reglas/acciones (p.ej., PROCESA Y PERSISTE, RECHAZA POR REGLA R2, REINTENTA Y MARCA PENDIENTE).
- Precondición ← requisitos de datos/estado/flags/config necesarios para ejecutar el CP.
- Resultado esperado ← estado final + efectos colaterales (persistencia, eventos, logs, códigos, auditoría).

TIMESTAMP: {timestamp}

Genera ahora los casos de prueba aplicando las técnicas ISTQB especificadas.
""".strip()
    
    def _get_fallback_istqb_prompt(self, programa: str, modulos: List[str], cantidad_max: int) -> str:
        """Prompt de fallback para generación ISTQB"""
        modulos_str = ", ".join([m.upper().strip() for m in modulos])
        return f"""
Genera {cantidad_max} casos de prueba con formato:
CP - NNN - {programa.upper()} - MODULO - CONDICION - ESCENARIO

Usando módulos: {modulos_str}

Aplica técnicas ISTQB básicas:
- Partición de equivalencia
- Valores límite
- Casos positivos y negativos
- Cobertura por módulo

Formato de salida:
A) CSV con casos
B) Fichas detalladas
C) Artefactos técnicos básicos
        """
    
    def get_confluence_test_plan_prompt(
        self,
        jira_data: Dict[str, Any],
        test_plan_title: str,
        test_strategy: str = "comprehensive",
        include_automation: bool = True,
        include_performance: bool = False,
        include_security: bool = True,
        confluence_space_key: str = "QA"
    ) -> str:
        """Obtener prompt para análisis de Jira y diseño de plan de pruebas para Confluence"""
        try:
            template_data = self.templates["confluence_test_plan"]
            template = template_data["template"]
            
            # Convertir jira_data a string para el template
            jira_data_str = json.dumps(jira_data, indent=2, ensure_ascii=False)
            
            # Reemplazar variables usando replace para evitar conflictos con llaves JSON
            prompt = template.replace('{jira_data}', jira_data_str)
            prompt = prompt.replace('{test_plan_title}', test_plan_title)
            prompt = prompt.replace('{test_strategy}', test_strategy)
            prompt = prompt.replace('{include_automation}', str(include_automation).lower())
            prompt = prompt.replace('{include_performance}', str(include_performance).lower())
            prompt = prompt.replace('{include_security}', str(include_security).lower())
            prompt = prompt.replace('{confluence_space_key}', confluence_space_key)
            prompt = prompt.replace('{timestamp}', datetime.utcnow().isoformat())
            
            logger.info("Confluence test plan prompt generated", 
                       test_plan_title=test_plan_title, 
                       test_strategy=test_strategy,
                       confluence_space_key=confluence_space_key)
            return prompt
            
        except Exception as e:
            logger.error("Error generating Confluence test plan prompt", error=str(e))
            return self._get_fallback_confluence_prompt(jira_data, test_plan_title)
    
    def _get_confluence_test_plan_template(self) -> str:
        """Template para análisis de Jira y diseño de plan de pruebas para Confluence"""
        return """
Eres un experto en QA y testing con especialización en análisis de issues de Jira y diseño de planes de prueba estructurados para Confluence.
Analiza el siguiente issue de Jira y diseña un plan de pruebas completo y profesional para documentar en Confluence.

DATOS DEL ISSUE DE JIRA:
{jira_data}

CONFIGURACIÓN DEL PLAN:
- Título del Plan: {test_plan_title}
- Estrategia de Testing: {test_strategy}
- Espacio de Confluence: {confluence_space_key}
- Incluir Automatización: {include_automation}
- Incluir Rendimiento: {include_performance}
- Incluir Seguridad: {include_security}
- Timestamp: {timestamp}

METODOLOGÍA DE DISEÑO DEL PLAN:

1. **ANÁLISIS DEL ISSUE DE JIRA**:
   - Identifica el tipo de issue (Story, Task, Bug, Epic)
   - Extrae criterios de aceptación explícitos e implícitos
   - Analiza la descripción y campos personalizados
   - Considera la prioridad, estado y dependencias
   - Identifica stakeholders y responsables

2. **DISEÑO DE ESTRATEGIA DE TESTING**:
   - Define el enfoque de testing según la estrategia solicitada
   - Identifica tipos de pruebas necesarios (funcionales, no funcionales)
   - Establece criterios de entrada y salida
   - Define niveles de testing (unit, integration, system, acceptance)
   - Considera aspectos de automatización, rendimiento y seguridad

3. **ESTRUCTURA DEL PLAN DE PRUEBAS**:
   - Resumen ejecutivo y objetivos
   - Alcance y criterios de cobertura
   - Estrategia de testing detallada
   - Plan de ejecución por fases
   - Casos de prueba estructurados
   - Criterios de aceptación y Definition of Done
   - Gestión de riesgos y mitigaciones
   - Recursos y cronograma

4. **FORMATO CONFLUENCE**:
   - Utiliza macros de Confluence para estructura
   - Incluye tablas, listas y elementos visuales
   - Aplica formato profesional y legible
   - Incluye enlaces y referencias cruzadas
   - Optimiza para colaboración y revisión

FORMATO DE RESPUESTA JSON:
{{
    "test_plan_sections": [
        {{
            "section_id": "overview",
            "title": "Resumen Ejecutivo",
            "content": "Contenido en formato Confluence con macros",
            "order": 1
        }},
        {{
            "section_id": "scope",
            "title": "Alcance y Criterios de Cobertura",
            "content": "Contenido detallado del alcance",
            "order": 2
        }},
        {{
            "section_id": "strategy",
            "title": "Estrategia de Testing",
            "content": "Estrategia detallada con enfoques",
            "order": 3
        }},
        {{
            "section_id": "execution",
            "title": "Plan de Ejecución",
            "content": "Fases y cronograma de ejecución",
            "order": 4
        }},
        {{
            "section_id": "test_cases",
            "title": "Casos de Prueba",
            "content": "Lista estructurada de casos de prueba",
            "order": 5
        }},
        {{
            "section_id": "acceptance",
            "title": "Criterios de Aceptación",
            "content": "Criterios y Definition of Done",
            "order": 6
        }},
        {{
            "section_id": "risks",
            "title": "Gestión de Riesgos",
            "content": "Riesgos identificados y mitigaciones",
            "order": 7
        }},
        {{
            "section_id": "resources",
            "title": "Recursos y Cronograma",
            "content": "Recursos necesarios y timeline",
            "order": 8
        }}
    ],
    "test_execution_phases": [
        {{
            "phase_name": "Fase 1: Preparación y Setup",
            "duration": "1-2 días",
            "test_cases_count": 5,
            "responsible": "Equipo de QA",
            "dependencies": ["Entorno de testing configurado"]
        }},
        {{
            "phase_name": "Fase 2: Pruebas Funcionales",
            "duration": "3-5 días",
            "test_cases_count": 15,
            "responsible": "Equipo de QA",
            "dependencies": ["Fase 1 completada"]
        }},
        {{
            "phase_name": "Fase 3: Pruebas de Integración",
            "duration": "2-3 días",
            "test_cases_count": 8,
            "responsible": "Equipo de QA + Desarrollo",
            "dependencies": ["Fase 2 completada"]
        }},
        {{
            "phase_name": "Fase 4: Pruebas de Aceptación",
            "duration": "1-2 días",
            "test_cases_count": 5,
            "responsible": "Product Owner + Stakeholders",
            "dependencies": ["Fase 3 completada"]
        }}
    ],
    "test_cases": [
        {{
            "test_case_id": "CP-001-{confluence_space_key}-MODULO-DATO-CONDICION-RESULTADO",
            "title": "CP - 001 - Aplicacion - Modulo - Dato - Condicion - Resultado",
            "description": "Descripción detallada del caso de prueba",
            "test_type": "functional|integration|ui|api|security|performance|usability|accessibility|regression",
            "priority": "critical|high|medium|low",
            "steps": [
                "Paso 1: Acción específica y verificable",
                "Paso 2: Acción específica y verificable",
                "Paso N: Verificación del resultado"
            ],
            "expected_result": "Resultado Esperado: [Descripción específica del resultado esperado]",
            "preconditions": [
                "Precondicion: [Descripción específica de las precondiciones necesarias]"
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
    "confluence_content": "Contenido completo del plan en formato Confluence con macros y formato",
    "confluence_markup": "Markup específico de Confluence para crear la página",
    "total_test_cases": 25,
    "estimated_duration": "1-2 semanas",
    "risk_level": "medium",
    "confidence_score": 0.85,
    "coverage_analysis": {{
        "functional_coverage": "90%",
        "edge_case_coverage": "75%",
        "integration_coverage": "80%",
        "security_coverage": "85%",
        "ui_coverage": "70%",
        "usability_coverage": "65%",
        "accessibility_coverage": "60%",
        "automation_coverage": "70%"
    }},
    "automation_potential": {{
        "high_automation": 15,
        "medium_automation": 8,
        "low_automation": 2,
        "automation_percentage": "70%",
        "recommended_tools": ["Selenium", "Playwright", "Cypress", "Jest"],
        "implementation_effort": "medium"
    }},
    "jira_analysis": {{
        "issue_type": "Story|Task|Bug|Epic",
        "priority_level": "Highest|High|Medium|Low|Lowest",
        "complexity": "low|medium|high",
        "business_value": "high|medium|low",
        "technical_risk": "high|medium|low",
        "dependencies": ["Dependencia 1", "Dependencia 2"],
        "stakeholders": ["Stakeholder 1", "Stakeholder 2"]
    }}
}}

REGLAS ESPECÍFICAS PARA CONFLUENCE:

1. **FORMATO CONFLUENCE**:
   - Utiliza macros de Confluence (info, warning, note, panel)
   - Aplica tablas estructuradas para casos de prueba
   - Incluye enlaces a issues de Jira relacionados
   - Usa elementos visuales (iconos, colores) apropiadamente
   - Optimiza para lectura en pantalla y impresión

2. **ESTRUCTURA DEL PLAN**:
   - Resumen ejecutivo claro y conciso
   - Alcance bien definido con criterios de entrada/salida
   - Estrategia de testing detallada y justificada
   - Plan de ejecución realista con dependencias
   - Casos de prueba estructurados y ejecutables
   - Criterios de aceptación medibles
   - Gestión de riesgos proactiva

3. **CASOS DE PRUEBA**:
   - Formato estándar: CP - NNN - APLICACION - MODULO - DATO - CONDICION - RESULTADO
   - Pasos claros, específicos y verificables
   - Resultados esperados medibles
   - Precondiciones completas
   - Datos de prueba realistas
   - Evaluación de automatización

4. **COLABORACIÓN**:
   - Incluye secciones para comentarios y feedback
   - Define roles y responsabilidades claramente
   - Establece criterios de aprobación
   - Facilita la revisión y actualización

5. **MÉTRICAS Y ANÁLISIS**:
   - Cobertura de pruebas cuantificada
   - Análisis de riesgo detallado
   - Potencial de automatización evaluado
   - Estimaciones realistas de tiempo y recursos

BUENAS PRÁCTICAS APLICADAS:
- Análisis basado en metodologías ágiles (Scrum, Kanban)
- Consideración del contexto de usuario y valor de negocio
- Aplicación de técnicas BDD (Behavior-Driven Development)
- Evaluación de viabilidad de automatización
- Consideración de aspectos de seguridad y rendimiento
- Formato profesional optimizado para Confluence
- Estructura colaborativa y mantenible

Genera la respuesta JSON ahora:
        """
    
    def _get_fallback_confluence_prompt(self, jira_data: Dict[str, Any], test_plan_title: str) -> str:
        """Prompt de fallback para análisis de Confluence"""
        return f"""
Analiza el siguiente issue de Jira y diseña un plan de pruebas para Confluence:

ISSUE: {jira_data.get('key', 'N/A')} - {jira_data.get('summary', 'N/A')}
DESCRIPCIÓN: {jira_data.get('description', 'N/A')}

TÍTULO DEL PLAN: {test_plan_title}

Genera un plan de pruebas en formato JSON con:
- test_plan_sections (secciones del plan)
- test_execution_phases (fases de ejecución)
- test_cases (casos de prueba)
- confluence_content (contenido para Confluence)
- confluence_markup (markup de Confluence)

Incluye también coverage_analysis, automation_potential y jira_analysis.
        """
