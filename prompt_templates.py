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
