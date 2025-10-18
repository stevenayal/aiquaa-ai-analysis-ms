"""
Prompt Templates Versionados
Plantillas de prompts para diferentes tipos de análisis QA
"""

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
        """Template para análisis de casos de prueba"""
        return """
Eres un experto en QA y testing. Analiza el siguiente caso de prueba y proporciona sugerencias de mejora.

CONTEXTO:
- Proyecto: {project_key}
- Prioridad: {priority}
- Etiquetas: {labels}
- Timestamp: {timestamp}

CASO DE PRUEBA:
{test_case_content}

INSTRUCCIONES:
Analiza el caso de prueba y proporciona sugerencias estructuradas en formato JSON. Enfócate en:

1. CLARIDAD Y COMPLETITUD
   - ¿Está claro el objetivo del test?
   - ¿Faltan pasos o información?
   - ¿Son específicos los resultados esperados?

2. COBERTURA DE TESTING
   - ¿Cubre casos edge?
   - ¿Incluye casos de error?
   - ¿Prueba integración adecuadamente?

3. MEJORES PRÁCTICAS
   - ¿Sigue convenciones de naming?
   - ¿Es mantenible y reutilizable?
   - ¿Tiene datos de prueba apropiados?

4. AUTOMATIZACIÓN
   - ¿Se puede automatizar fácilmente?
   - ¿Qué herramientas recomiendas?

FORMATO DE RESPUESTA JSON:
{{
    "summary": "Resumen del análisis en 2-3 oraciones",
    "confidence_score": 0.85,
    "suggestions": [
        {{
            "type": "clarity|coverage|best_practice|automation",
            "title": "Título de la sugerencia",
            "description": "Descripción detallada de la mejora",
            "priority": "high|medium|low",
            "category": "improvement|bug_fix|enhancement",
            "effort": "low|medium|high",
            "impact": "low|medium|high"
        }}
    ],
    "categories": ["clarity", "coverage", "automation"],
    "overall_quality_score": 0.75,
    "recommendations": [
        "Recomendación específica 1",
        "Recomendación específica 2"
    ]
}}

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
        """Template para análisis de requerimientos y generación de casos de prueba"""
        return """
Eres un experto en QA y testing. Analiza el siguiente requerimiento y genera casos de prueba estructurados.

REQUERIMIENTO:
{requirement_content}

CONTEXTO:
- Proyecto: {project_key}
- Prioridad: {priority}
- Tipos de prueba: {test_types}
- Nivel de cobertura: {coverage_level}

INSTRUCCIONES:
1. Analiza el requerimiento y identifica todos los escenarios de prueba necesarios
2. Genera casos de prueba para cada tipo especificado: {test_types}
3. Asegúrate de cubrir casos positivos, negativos y edge cases
4. Incluye precondiciones, pasos detallados y resultados esperados
5. Evalúa el potencial de automatización de cada caso
6. Proporciona un análisis de cobertura

FORMATO DE RESPUESTA JSON:
{{
    "test_cases": [
        {{
            "test_case_id": "TC-{project_key}-001",
            "title": "Título descriptivo del caso de prueba",
            "description": "Descripción detallada del caso de prueba",
            "test_type": "functional|integration|ui|api|security|performance",
            "priority": "high|medium|low",
            "steps": [
                "Paso 1: Descripción detallada",
                "Paso 2: Descripción detallada",
                "Paso N: Descripción detallada"
            ],
            "expected_result": "Resultado esperado específico y verificable",
            "preconditions": [
                "Precondición 1",
                "Precondición 2"
            ],
            "test_data": {{
                "campo1": "valor1",
                "campo2": "valor2"
            }},
            "automation_potential": "high|medium|low",
            "estimated_duration": "X-Y minutes"
        }}
    ],
    "coverage_analysis": {{
        "functional_coverage": "X%",
        "edge_case_coverage": "X%",
        "integration_coverage": "X%",
        "security_coverage": "X%",
        "ui_coverage": "X%"
    }},
    "confidence_score": 0.85
}}

REGLAS:
- Genera entre 3-8 casos de prueba según la complejidad
- Cada caso debe ser independiente y ejecutable
- Incluye datos de prueba específicos cuando sea relevante
- Prioriza casos de alta prioridad primero
- Asegúrate de que los pasos sean claros y verificables
- Incluye casos de error y validación cuando aplique

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
        """Template para análisis de work item de Jira y generación de casos de prueba"""
        return """
Eres un experto en QA y testing. Analiza el siguiente work item de Jira y genera casos de prueba estructurados.

DATOS DEL WORK ITEM:
{work_item_data}

CONTENIDO DEL REQUERIMIENTO:
{requirement_content}

CONTEXTO:
- Proyecto: {project_key}
- Tipos de prueba: {test_types}
- Nivel de cobertura: {coverage_level}
- Timestamp: {timestamp}

INSTRUCCIONES:
1. Analiza el work item de Jira y extrae todos los escenarios de prueba necesarios
2. Considera el tipo de issue, prioridad y estado del work item
3. Genera casos de prueba para cada tipo especificado: {test_types}
4. Asegúrate de cubrir casos positivos, negativos y edge cases
5. Incluye precondiciones, pasos detallados y resultados esperados
6. Evalúa el potencial de automatización de cada caso
7. Proporciona un análisis de cobertura específico para el contexto de Jira

FORMATO DE RESPUESTA JSON:
{{
    "test_cases": [
        {{
            "test_case_id": "TC-{project_key}-001",
            "title": "Título descriptivo del caso de prueba",
            "description": "Descripción detallada del caso de prueba",
            "test_type": "functional|integration|ui|api|security|performance",
            "priority": "high|medium|low",
            "steps": [
                "Paso 1: Descripción detallada",
                "Paso 2: Descripción detallada",
                "Paso N: Descripción detallada"
            ],
            "expected_result": "Resultado esperado específico y verificable",
            "preconditions": [
                "Precondición 1",
                "Precondición 2"
            ],
            "test_data": {{
                "campo1": "valor1",
                "campo2": "valor2"
            }},
            "automation_potential": "high|medium|low",
            "estimated_duration": "X-Y minutes"
        }}
    ],
    "coverage_analysis": {{
        "functional_coverage": "X%",
        "edge_case_coverage": "X%",
        "integration_coverage": "X%",
        "security_coverage": "X%",
        "ui_coverage": "X%",
        "jira_integration_coverage": "X%"
    }},
    "confidence_score": 0.85
}}

REGLAS ESPECÍFICAS PARA JIRA:
- Genera entre 3-8 casos de prueba según la complejidad del work item
- Cada caso debe ser independiente y ejecutable
- Incluye datos de prueba específicos cuando sea relevante
- Prioriza casos de alta prioridad primero
- Asegúrate de que los pasos sean claros y verificables
- Incluye casos de error y validación cuando aplique
- Considera el contexto del proyecto y tipo de issue
- Incluye casos específicos para integración con Jira si aplica

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
