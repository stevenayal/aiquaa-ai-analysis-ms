"""FastAPI dependencies for dependency injection."""

from functools import lru_cache

from infrastructure.ai import LLMWrapper, PromptTemplates
from infrastructure.http import TrackerClient
from infrastructure.sanitizer import PIISanitizer
from domain.services import AnalysisService, JiraService, ConfluenceService


# Infrastructure dependencies (singletons)

@lru_cache
def get_llm_wrapper() -> LLMWrapper:
    """Get LLM wrapper instance."""
    return LLMWrapper()


@lru_cache
def get_prompt_templates() -> PromptTemplates:
    """Get prompt templates instance."""
    return PromptTemplates()


@lru_cache
def get_sanitizer() -> PIISanitizer:
    """Get PII sanitizer instance."""
    return PIISanitizer()


@lru_cache
def get_tracker_client() -> TrackerClient:
    """Get Jira tracker client instance."""
    return TrackerClient()


# Service dependencies

@lru_cache
def get_analysis_service() -> AnalysisService:
    """Get analysis service instance."""
    return AnalysisService(
        llm_wrapper=get_llm_wrapper(),
        prompt_templates=get_prompt_templates(),
        sanitizer=get_sanitizer()
    )


@lru_cache
def get_jira_service() -> JiraService:
    """Get Jira service instance."""
    return JiraService(
        llm_wrapper=get_llm_wrapper(),
        prompt_templates=get_prompt_templates(),
        jira_client=get_tracker_client()
    )


@lru_cache
def get_confluence_service() -> ConfluenceService:
    """Get Confluence service instance."""
    return ConfluenceService(
        llm_wrapper=get_llm_wrapper(),
        prompt_templates=get_prompt_templates(),
        jira_client=get_tracker_client()
    )
