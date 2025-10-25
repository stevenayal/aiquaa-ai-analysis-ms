"""Confluence service - business logic for test plan generation."""

import time
from datetime import datetime
from typing import Dict, Any

import structlog

from core.constants import AnalysisStatus
from infrastructure.ai import LLMWrapper, PromptTemplates
from infrastructure.http import TrackerClient

logger = structlog.get_logger(__name__)


class ConfluenceService:
    """Service for Confluence test plan generation."""

    def __init__(
        self,
        llm_wrapper: LLMWrapper,
        prompt_templates: PromptTemplates,
        jira_client: TrackerClient
    ):
        """Initialize Confluence service."""
        self.llm = llm_wrapper
        self.prompts = prompt_templates
        self.jira = jira_client

    async def generate_test_plan(
        self,
        jira_issue_id: str,
        confluence_space_key: str,
        test_plan_title: str
    ) -> Dict[str, Any]:
        """Generate test plan from Jira issue."""
        start_time = time.time()

        try:
            # Get Jira issue details
            work_item_data = await self.jira.get_work_item_details(jira_issue_id)

            if not work_item_data:
                raise ValueError(f"Jira issue {jira_issue_id} not found")

            # Build content
            content = f"Title: {work_item_data.get('summary', '')}\n"
            content += f"Description: {work_item_data.get('description', '')}"

            # Generate analysis ID
            analysis_id = f"confluence_{jira_issue_id}_{int(time.time())}"

            # Get Confluence prompt
            prompt = self.prompts.get_confluence_test_plan_prompt(
                jira_content=content,
                test_plan_title=test_plan_title or f"Test Plan - {work_item_data.get('summary', '')}"
            )

            # Generate test plan
            result = await self.llm.analyze_requirements(
                prompt=prompt,
                requirement_id=jira_issue_id,
                analysis_id=analysis_id
            )

            processing_time = time.time() - start_time

            return {
                "id_issue_jira": jira_issue_id,
                "id_analisis": analysis_id,
                "titulo_plan": test_plan_title or f"Test Plan - {work_item_data.get('summary', '')}",
                "estado": AnalysisStatus.COMPLETED,
                "casos_prueba": result.get("test_cases", []),
                "secciones_plan": result.get("sections", []),
                "fases_ejecucion": result.get("phases", []),
                "puntuacion_confianza": result.get("confidence_score", 0.8),
                "tiempo_procesamiento": processing_time,
                "fecha_creacion": datetime.utcnow()
            }

        except Exception as e:
            logger.error("Test plan generation failed", error=str(e), jira_issue_id=jira_issue_id)
            processing_time = time.time() - start_time

            return {
                "id_issue_jira": jira_issue_id,
                "id_analisis": f"confluence_error_{int(time.time())}",
                "titulo_plan": test_plan_title or "Error",
                "estado": AnalysisStatus.FAILED,
                "casos_prueba": [],
                "secciones_plan": [],
                "fases_ejecucion": [],
                "puntuacion_confianza": 0.0,
                "tiempo_procesamiento": processing_time,
                "fecha_creacion": datetime.utcnow(),
                "error": str(e)
            }
