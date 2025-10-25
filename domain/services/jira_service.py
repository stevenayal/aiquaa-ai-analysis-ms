"""Jira service - business logic for Jira integration."""

import time
from datetime import datetime
from typing import Dict, Any

import structlog

from core.constants import AnalysisLevel, AnalysisStatus
from infrastructure.ai import LLMWrapper, PromptTemplates
from infrastructure.http import TrackerClient

logger = structlog.get_logger(__name__)


class JiraService:
    """Service for Jira work item analysis."""

    def __init__(
        self,
        llm_wrapper: LLMWrapper,
        prompt_templates: PromptTemplates,
        jira_client: TrackerClient
    ):
        """Initialize Jira service."""
        self.llm = llm_wrapper
        self.prompts = prompt_templates
        self.jira = jira_client

    async def analyze_work_item(
        self,
        work_item_id: str,
        analysis_level: AnalysisLevel
    ) -> Dict[str, Any]:
        """Analyze Jira work item and generate test cases."""
        start_time = time.time()

        try:
            # Get work item details from Jira
            work_item_data = await self.jira.get_work_item_details(work_item_id)

            if not work_item_data:
                raise ValueError(f"Work item {work_item_id} not found")

            # Build content from work item
            content = self._build_work_item_content(work_item_data)

            # Generate analysis ID
            analysis_id = f"jira_analysis_{work_item_id}_{int(time.time())}"

            # Get Jira-specific prompt
            prompt = self.prompts.get_jira_workitem_analysis_prompt(
                work_item_content=content,
                work_item_type=work_item_data.get("issue_type", "Story"),
                detail_level=analysis_level
            )

            # Perform analysis
            result = await self.llm.analyze_jira_workitem(
                prompt=prompt,
                work_item_id=work_item_id,
                analysis_id=analysis_id
            )

            processing_time = time.time() - start_time

            return {
                "id_work_item": work_item_id,
                "datos_jira": work_item_data,
                "id_analisis": analysis_id,
                "estado": AnalysisStatus.COMPLETED,
                "casos_prueba": result.get("test_cases", []),
                "analisis_cobertura": result.get("coverage_analysis", {}),
                "puntuacion_confianza": result.get("confidence_score", 0.8),
                "tiempo_procesamiento": processing_time,
                "fecha_creacion": datetime.utcnow()
            }

        except Exception as e:
            logger.error("Jira analysis failed", error=str(e), work_item_id=work_item_id)
            processing_time = time.time() - start_time

            return {
                "id_work_item": work_item_id,
                "id_analisis": f"jira_error_{int(time.time())}",
                "estado": AnalysisStatus.FAILED,
                "casos_prueba": [],
                "analisis_cobertura": {},
                "puntuacion_confianza": 0.0,
                "tiempo_procesamiento": processing_time,
                "fecha_creacion": datetime.utcnow(),
                "error": str(e)
            }

    def _build_work_item_content(self, work_item_data: Dict[str, Any]) -> str:
        """Build content string from work item data."""
        parts = [
            f"Title: {work_item_data.get('summary', '')}",
            f"Type: {work_item_data.get('issue_type', '')}",
            f"Priority: {work_item_data.get('priority', '')}",
            f"\nDescription:\n{work_item_data.get('description', '')}"
        ]

        if work_item_data.get('acceptance_criteria'):
            criteria = work_item_data['acceptance_criteria']
            if isinstance(criteria, list):
                parts.append(f"\nAcceptance Criteria:\n" + "\n".join(f"- {c}" for c in criteria))

        return "\n".join(parts)
