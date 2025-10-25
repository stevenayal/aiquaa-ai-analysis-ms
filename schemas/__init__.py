"""Pydantic schemas for API requests and responses."""

from .common import ErrorResponse, HealthResponse, LLMDiagnosticResponse
from .analysis import (
    AnalysisRequest,
    AnalysisResponse,
    TestCase,
    CoverageAnalysis,
    AdvancedTestRequest,
    AdvancedTestResponse,
)
from .jira import JiraAnalysisRequest, JiraAnalysisResponse, JiraWorkItemData
from .confluence import (
    ConfluenceTestPlanRequest,
    ConfluenceTestPlanResponse,
    TestPlanSection,
    ExecutionPhase,
)

__all__ = [
    # Common
    "ErrorResponse",
    "HealthResponse",
    "LLMDiagnosticResponse",
    # Analysis
    "AnalysisRequest",
    "AnalysisResponse",
    "TestCase",
    "CoverageAnalysis",
    "AdvancedTestRequest",
    "AdvancedTestResponse",
    # Jira
    "JiraAnalysisRequest",
    "JiraAnalysisResponse",
    "JiraWorkItemData",
    # Confluence
    "ConfluenceTestPlanRequest",
    "ConfluenceTestPlanResponse",
    "TestPlanSection",
    "ExecutionPhase",
]
