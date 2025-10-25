"""Confluence integration schemas."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

from core.constants import AnalysisStatus
from .analysis import TestCase


class TestPlanSection(BaseModel):
    """Test plan section."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "1. Introduction",
                "content": "This test plan covers the authentication feature...",
                "subsections": [
                    {
                        "title": "1.1 Purpose",
                        "content": "The purpose of this test plan is to..."
                    }
                ]
            }
        }
    )

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    subsections: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Subsections"
    )


class ExecutionPhase(BaseModel):
    """Test execution phase."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phase_number": 1,
                "name": "Smoke Testing",
                "description": "Initial smoke tests to verify basic functionality",
                "test_cases": ["TC-001", "TC-002"],
                "estimated_duration": "2 hours",
                "dependencies": []
            }
        }
    )

    phase_number: int = Field(..., description="Phase number")
    name: str = Field(..., description="Phase name")
    description: str = Field(..., description="Phase description")
    test_cases: List[str] = Field(..., description="Test case IDs in this phase")
    estimated_duration: Optional[str] = Field(default=None, description="Estimated duration")
    dependencies: Optional[List[str]] = Field(default=None, description="Dependencies on other phases")


class ConfluenceTestPlanRequest(BaseModel):
    """Request for Confluence test plan generation.

    Supports both English and Spanish parameter names.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "jira_issue_id": "PROJ-123",
                    "confluence_space_key": "QA",
                    "test_plan_title": "Test Plan - User Authentication Feature"
                },
                {
                    "id_issue_jira": "PROJ-456",
                    "espacio_confluence": "QA",
                    "titulo_plan_pruebas": "Plan de Pruebas - Funcionalidad de Autenticación"
                }
            ]
        }
    )

    # English parameters
    jira_issue_id: Optional[str] = Field(default=None, description="Jira issue ID")
    confluence_space_key: Optional[str] = Field(default=None, description="Confluence space key")
    test_plan_title: Optional[str] = Field(default=None, description="Test plan title")

    # Spanish parameters
    id_issue_jira: Optional[str] = Field(default=None, description="ID del issue de Jira")
    espacio_confluence: Optional[str] = Field(default=None, description="Clave del espacio de Confluence")
    titulo_plan_pruebas: Optional[str] = Field(default=None, description="Título del plan de pruebas")

    @field_validator("jira_issue_id", "id_issue_jira")
    @classmethod
    def validate_jira_issue_id(cls, v, info):
        """Ensure at least one Jira issue ID is provided."""
        if not v and not info.data.get("jira_issue_id") and not info.data.get("id_issue_jira"):
            raise ValueError("Either 'jira_issue_id' or 'id_issue_jira' must be provided")
        return v

    def get_jira_issue_id(self) -> str:
        """Get Jira issue ID regardless of parameter name."""
        return self.jira_issue_id or self.id_issue_jira or ""

    def get_confluence_space_key(self) -> str:
        """Get Confluence space key regardless of parameter name."""
        return self.confluence_space_key or self.espacio_confluence or ""

    def get_test_plan_title(self) -> str:
        """Get test plan title regardless of parameter name."""
        return self.test_plan_title or self.titulo_plan_pruebas or ""


class ConfluenceTestPlanResponse(BaseModel):
    """Response from Confluence test plan generation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_issue_jira": "PROJ-123",
                "id_analisis": "confluence_PROJ123_1729768200",
                "titulo_plan": "Test Plan - User Authentication Feature",
                "estado": "completed",
                "casos_prueba": [
                    {
                        "id": "TC-001",
                        "title": "Verify successful login",
                        "description": "Test successful login flow",
                        "steps": ["Navigate to login", "Enter credentials", "Submit"],
                        "expected_result": "User logged in",
                        "priority": "high",
                        "category": "functional"
                    }
                ],
                "secciones_plan": [
                    {
                        "title": "1. Introduction",
                        "content": "This test plan covers authentication...",
                        "subsections": []
                    },
                    {
                        "title": "2. Test Strategy",
                        "content": "Testing will be performed in phases...",
                        "subsections": []
                    }
                ],
                "fases_ejecucion": [
                    {
                        "phase_number": 1,
                        "name": "Smoke Testing",
                        "description": "Initial smoke tests",
                        "test_cases": ["TC-001"],
                        "estimated_duration": "2 hours",
                        "dependencies": []
                    }
                ],
                "puntuacion_confianza": 0.87,
                "tiempo_procesamiento": 18.6,
                "fecha_creacion": "2024-10-24T10:30:00Z"
            }
        }
    )

    id_issue_jira: str = Field(..., description="Jira issue ID")
    id_analisis: str = Field(..., description="Analysis ID")
    titulo_plan: str = Field(..., description="Test plan title")
    estado: AnalysisStatus = Field(..., description="Analysis status")
    casos_prueba: List[TestCase] = Field(default_factory=list, description="Generated test cases")
    secciones_plan: List[TestPlanSection] = Field(default_factory=list, description="Test plan sections")
    fases_ejecucion: Optional[List[ExecutionPhase]] = Field(
        default=None,
        description="Test execution phases"
    )
    puntuacion_confianza: float = Field(..., description="Confidence score", ge=0.0, le=1.0)
    tiempo_procesamiento: float = Field(..., description="Processing time in seconds")
    fecha_creacion: datetime = Field(..., description="Creation timestamp")
