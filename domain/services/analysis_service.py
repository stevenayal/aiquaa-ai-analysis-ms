"""Analysis service - business logic for content analysis."""

import time
from datetime import datetime
from typing import Dict, Any, List

import structlog

from core.constants import ContentType, AnalysisLevel, AnalysisStatus
from infrastructure.ai import LLMWrapper, PromptTemplates
from infrastructure.sanitizer import PIISanitizer

logger = structlog.get_logger(__name__)


class AnalysisService:
    """Service for analyzing content and generating test cases."""

    def __init__(
        self,
        llm_wrapper: LLMWrapper,
        prompt_templates: PromptTemplates,
        sanitizer: PIISanitizer
    ):
        """Initialize analysis service.

        Args:
            llm_wrapper: LLM wrapper instance
            prompt_templates: Prompt templates instance
            sanitizer: PII sanitizer instance
        """
        self.llm = llm_wrapper
        self.prompts = prompt_templates
        self.sanitizer = sanitizer

    async def analyze_content(
        self,
        content: str,
        content_type: ContentType,
        analysis_level: AnalysisLevel,
        sanitize_pii: bool = True
    ) -> Dict[str, Any]:
        """Analyze content and generate test cases.

        Args:
            content: Content to analyze
            content_type: Type of content
            analysis_level: Level of analysis
            sanitize_pii: Whether to sanitize PII

        Returns:
            Analysis result with test cases
        """
        start_time = time.time()

        try:
            # Sanitize content if enabled
            sanitized_content = content
            if sanitize_pii:
                sanitized_content = self.sanitizer.sanitize(content)

            # Generate analysis ID
            analysis_id = f"analysis_{content_type}_{int(time.time())}"

            # Get appropriate prompt
            prompt = self.prompts.get_requirements_analysis_prompt(
                requirement=sanitized_content,
                requirement_type=content_type,
                detail_level=analysis_level
            )

            # Perform analysis
            result = await self.llm.analyze_requirements(
                prompt=prompt,
                requirement_id=content_type,
                analysis_id=analysis_id
            )

            # Calculate processing time
            processing_time = time.time() - start_time

            # Build response
            return {
                "id_contenido": analysis_id,
                "tipo_contenido": content_type,
                "estado": AnalysisStatus.COMPLETED,
                "casos_prueba": result.get("test_cases", []),
                "sugerencias": result.get("suggestions", []),
                "analisis_cobertura": result.get("coverage_analysis", {}),
                "puntuacion_confianza": result.get("confidence_score", 0.8),
                "tiempo_procesamiento": processing_time,
                "fecha_creacion": datetime.utcnow()
            }

        except Exception as e:
            logger.error("Analysis failed", error=str(e))
            processing_time = time.time() - start_time

            return {
                "id_contenido": f"analysis_error_{int(time.time())}",
                "tipo_contenido": content_type,
                "estado": AnalysisStatus.FAILED,
                "casos_prueba": [],
                "sugerencias": [],
                "analisis_cobertura": {},
                "puntuacion_confianza": 0.0,
                "tiempo_procesamiento": processing_time,
                "fecha_creacion": datetime.utcnow(),
                "error": str(e)
            }

    async def generate_advanced_tests(
        self,
        requirement: str,
        strategies: List[str],
        include_istqb_format: bool = True,
        include_execution_plan: bool = False
    ) -> Dict[str, Any]:
        """Generate advanced test cases with ISTQB techniques.

        Args:
            requirement: Requirement to analyze
            strategies: Test design strategies to apply
            include_istqb_format: Include ISTQB formatted tests
            include_execution_plan: Include execution plan

        Returns:
            Advanced test generation result
        """
        start_time = time.time()

        try:
            generation_id = f"istqb_analysis_{int(time.time())}"

            # Get ISTQB prompt
            prompt = self.prompts.get_istqb_test_generation_prompt(
                requirement=requirement,
                programa="ADVANCED",
                strategies=strategies,
                include_execution_plan=include_execution_plan
            )

            # Generate tests
            result = await self.llm.generate_istqb_test_cases(
                prompt=prompt,
                programa="ADVANCED",
                generation_id=generation_id
            )

            processing_time = time.time() - start_time

            return {
                "id_analisis": generation_id,
                "estado": AnalysisStatus.COMPLETED,
                "csv_cases": result.get("csv_cases", []),
                "fichas": result.get("fichas", []),
                "artefactos_tecnicos": result.get("artefactos_tecnicos", {}),
                "plan_ejecucion": result.get("plan_ejecucion") if include_execution_plan else None,
                "tiempo_procesamiento": processing_time,
                "fecha_creacion": datetime.utcnow()
            }

        except Exception as e:
            logger.error("Advanced test generation failed", error=str(e))
            processing_time = time.time() - start_time

            return {
                "id_analisis": f"istqb_error_{int(time.time())}",
                "estado": AnalysisStatus.FAILED,
                "csv_cases": [],
                "fichas": [],
                "artefactos_tecnicos": {},
                "plan_ejecucion": None,
                "tiempo_procesamiento": processing_time,
                "fecha_creacion": datetime.utcnow(),
                "error": str(e)
            }
