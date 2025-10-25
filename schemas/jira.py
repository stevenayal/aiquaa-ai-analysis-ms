"""Jira integration schemas."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

from core.constants import AnalysisLevel, AnalysisStatus
from .analysis import TestCase, CoverageAnalysis


class JiraWorkItemData(BaseModel):
    """Jira work item data."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "key": "PROJ-123",
                "summary": "Implement user authentication",
                "description": "As a user, I want to log in securely...",
                "issue_type": "Story",
                "priority": "High",
                "status": "In Progress",
                "acceptance_criteria": [
                    "User can log in with email and password",
                    "Invalid credentials show error message"
                ],
                "labels": ["authentication", "security"],
                "assignee": "john.doe@example.com"
            }
        }
    )

    key: str = Field(..., description="Jira issue key")
    summary: str = Field(..., description="Issue summary")
    description: Optional[str] = Field(default=None, description="Issue description")
    issue_type: str = Field(..., description="Issue type (Story, Bug, Task, etc.)")
    priority: Optional[str] = Field(default=None, description="Priority level")
    status: str = Field(..., description="Current status")
    acceptance_criteria: Optional[List[str]] = Field(default=None, description="Acceptance criteria")
    labels: Optional[List[str]] = Field(default=None, description="Issue labels")
    assignee: Optional[str] = Field(default=None, description="Assignee email")
    reporter: Optional[str] = Field(default=None, description="Reporter email")
    created: Optional[datetime] = Field(default=None, description="Creation date")
    updated: Optional[datetime] = Field(default=None, description="Last update date")


class JiraAnalysisRequest(BaseModel):
    """Request for Jira work item analysis.

    Supports both English and Spanish parameter names.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "work_item_id": "PROJ-123",
                    "analysis_level": "comprehensive"
                },
                {
                    "id_work_item": "PROJ-456",
                    "nivel_analisis": "detailed"
                }
            ]
        }
    )

    # English parameters
    work_item_id: Optional[str] = Field(default=None, description="Jira work item ID")
    analysis_level: Optional[AnalysisLevel] = Field(
        default=AnalysisLevel.DETAILED,
        description="Analysis depth"
    )

    # Spanish parameters
    id_work_item: Optional[str] = Field(default=None, description="ID del work item de Jira")
    nivel_analisis: Optional[str] = Field(default=None, description="Nivel de análisis")

    @field_validator("work_item_id", "id_work_item")
    @classmethod
    def validate_work_item_id(cls, v, info):
        """Ensure at least one work item ID is provided."""
        if not v and not info.data.get("work_item_id") and not info.data.get("id_work_item"):
            raise ValueError("Either 'work_item_id' or 'id_work_item' must be provided")
        return v

    def get_work_item_id(self) -> str:
        """Get work item ID regardless of parameter name."""
        return self.work_item_id or self.id_work_item or ""

    def get_analysis_level(self) -> AnalysisLevel:
        """Get analysis level regardless of parameter name."""
        if self.nivel_analisis:
            return AnalysisLevel(self.nivel_analisis)
        return self.analysis_level or AnalysisLevel.DETAILED


class JiraAnalysisResponse(BaseModel):
    """Response from Jira work item analysis."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_work_item": "PROJ-123",
                "datos_jira": {
                    "key": "PROJ-123",
                    "summary": "Implement user authentication",
                    "description": "As a user, I want to log in securely...",
                    "issue_type": "Story",
                    "priority": "High",
                    "status": "In Progress",
                    "acceptance_criteria": [
                        "User can log in with email and password",
                        "Invalid credentials show error message"
                    ]
                },
                "id_analisis": "jira_analysis_PROJ123_1729768200",
                "estado": "completed",
                "casos_prueba": [
                    {
                        "id": "TC-PROJ-123-001",
                        "title": "Verify successful login with valid credentials",
                        "description": "Test that user can log in with valid email and password",
                        "steps": [
                            "Navigate to login page",
                            "Enter valid email",
                            "Enter valid password",
                            "Click login button"
                        ],
                        "expected_result": "User is logged in and redirected to dashboard",
                        "priority": "high",
                        "category": "functional"
                    }
                ],
                "analisis_cobertura": {
                    "functional_coverage": 90.0,
                    "edge_case_coverage": 75.0,
                    "negative_test_coverage": 80.0,
                    "missing_scenarios": ["Session timeout"],
                    "recommendations": ["Add tests for concurrent sessions"]
                },
                "puntuacion_confianza": 0.88,
                "tiempo_procesamiento": 14.3,
                "fecha_creacion": "2024-10-24T10:30:00Z"
            }
        }
    )

    id_work_item: str = Field(..., description="Jira work item ID")
    datos_jira: JiraWorkItemData = Field(..., description="Jira work item data")
    id_analisis: str = Field(..., description="Analysis ID")
    estado: AnalysisStatus = Field(..., description="Analysis status")
    casos_prueba: List[TestCase] = Field(default_factory=list, description="Generated test cases")
    analisis_cobertura: Optional[CoverageAnalysis] = Field(default=None, description="Coverage analysis")
    puntuacion_confianza: float = Field(..., description="Confidence score", ge=0.0, le=1.0)
    tiempo_procesamiento: float = Field(..., description="Processing time in seconds")
    fecha_creacion: datetime = Field(..., description="Creation timestamp")
