"""Analysis schemas for content analysis endpoints."""

from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

from core.constants import ContentType, AnalysisLevel, AnalysisStatus


class TestCase(BaseModel):
    """Test case model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "TC-001",
                "title": "Verify user login with valid credentials",
                "description": "Test that a user can successfully log in with valid username and password",
                "preconditions": ["User account exists", "Application is accessible"],
                "steps": [
                    "Navigate to login page",
                    "Enter valid username",
                    "Enter valid password",
                    "Click login button"
                ],
                "expected_result": "User is redirected to dashboard",
                "priority": "high",
                "category": "functional"
            }
        }
    )

    id: str = Field(..., description="Test case identifier")
    title: str = Field(..., description="Test case title")
    description: str = Field(..., description="Detailed description")
    preconditions: Optional[List[str]] = Field(default=None, description="Preconditions")
    steps: List[str] = Field(..., description="Test steps")
    expected_result: str = Field(..., description="Expected result")
    priority: Optional[str] = Field(default="medium", description="Priority level")
    category: Optional[str] = Field(default="functional", description="Test category")


class CoverageAnalysis(BaseModel):
    """Coverage analysis model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "functional_coverage": 85.0,
                "edge_case_coverage": 60.0,
                "negative_test_coverage": 70.0,
                "missing_scenarios": [
                    "Password reset flow",
                    "Session timeout handling"
                ],
                "recommendations": [
                    "Add tests for concurrent user sessions",
                    "Include boundary value tests for input fields"
                ]
            }
        }
    )

    functional_coverage: float = Field(..., description="Functional coverage percentage", ge=0.0, le=100.0)
    edge_case_coverage: float = Field(..., description="Edge case coverage percentage", ge=0.0, le=100.0)
    negative_test_coverage: float = Field(..., description="Negative test coverage percentage", ge=0.0, le=100.0)
    missing_scenarios: Optional[List[str]] = Field(default=None, description="Missing test scenarios")
    recommendations: Optional[List[str]] = Field(default=None, description="Coverage improvement recommendations")


class AnalysisRequest(BaseModel):
    """Request for content analysis.

    Supports both English and Spanish parameter names based on feature flag.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "content": "As a user, I want to be able to reset my password so that I can regain access to my account if I forget my credentials.",
                    "content_type": "user_story",
                    "analysis_level": "comprehensive"
                },
                {
                    "contenido": "El sistema debe permitir a los usuarios iniciar sesión con nombre de usuario y contraseña.",
                    "tipo_contenido": "requirement",
                    "nivel_analisis": "detailed"
                }
            ]
        }
    )

    # English parameters
    content: Optional[str] = Field(default=None, description="Content to analyze")
    content_type: Optional[ContentType] = Field(default=ContentType.GENERAL, description="Type of content")
    analysis_level: Optional[AnalysisLevel] = Field(default=AnalysisLevel.DETAILED, description="Analysis depth")

    # Spanish parameters
    contenido: Optional[str] = Field(default=None, description="Contenido a analizar")
    tipo_contenido: Optional[str] = Field(default=None, description="Tipo de contenido")
    nivel_analisis: Optional[str] = Field(default=None, description="Nivel de análisis")

    @field_validator("content", "contenido")
    @classmethod
    def validate_content_present(cls, v, info):
        """Ensure at least one content field is provided."""
        if not v and not info.data.get("content") and not info.data.get("contenido"):
            raise ValueError("Either 'content' or 'contenido' must be provided")
        return v

    def get_content(self) -> str:
        """Get content regardless of parameter name."""
        return self.content or self.contenido or ""

    def get_content_type(self) -> ContentType:
        """Get content type regardless of parameter name."""
        if self.tipo_contenido:
            return ContentType(self.tipo_contenido)
        return self.content_type or ContentType.GENERAL

    def get_analysis_level(self) -> AnalysisLevel:
        """Get analysis level regardless of parameter name."""
        if self.nivel_analisis:
            return AnalysisLevel(self.nivel_analisis)
        return self.analysis_level or AnalysisLevel.DETAILED


class AnalysisResponse(BaseModel):
    """Response from content analysis."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_contenido": "analysis_user_story_1729768200",
                "tipo_contenido": "user_story",
                "estado": "completed",
                "casos_prueba": [
                    {
                        "id": "TC-001",
                        "title": "Verify password reset email sent",
                        "description": "Test that password reset email is sent when user requests reset",
                        "steps": ["Navigate to password reset", "Enter email", "Submit request"],
                        "expected_result": "Reset email sent successfully",
                        "priority": "high",
                        "category": "functional"
                    }
                ],
                "sugerencias": [
                    "Add test for invalid email format",
                    "Include test for expired reset tokens"
                ],
                "analisis_cobertura": {
                    "functional_coverage": 85.0,
                    "edge_case_coverage": 60.0,
                    "negative_test_coverage": 70.0,
                    "missing_scenarios": ["Concurrent reset requests"],
                    "recommendations": ["Add boundary value tests"]
                },
                "puntuacion_confianza": 0.85,
                "tiempo_procesamiento": 12.5,
                "fecha_creacion": "2024-10-24T10:30:00Z"
            }
        }
    )

    id_contenido: str = Field(..., description="Analysis ID")
    tipo_contenido: str = Field(..., description="Content type analyzed")
    estado: AnalysisStatus = Field(..., description="Analysis status")
    casos_prueba: List[TestCase] = Field(default_factory=list, description="Generated test cases")
    sugerencias: Optional[List[str]] = Field(default=None, description="Improvement suggestions")
    analisis_cobertura: Optional[CoverageAnalysis] = Field(default=None, description="Coverage analysis")
    puntuacion_confianza: float = Field(..., description="Confidence score", ge=0.0, le=1.0)
    tiempo_procesamiento: float = Field(..., description="Processing time in seconds")
    fecha_creacion: datetime = Field(..., description="Creation timestamp")


class AdvancedTestRequest(BaseModel):
    """Request for advanced test generation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "requirement": "The system shall support user authentication via OAuth 2.0",
                "strategies": ["equivalence_partitioning", "boundary_value", "decision_table"],
                "include_istqb_format": True,
                "include_execution_plan": False
            }
        }
    )

    requirement: str = Field(..., description="Requirement or user story to analyze")
    strategies: Optional[List[str]] = Field(
        default=None,
        description="Test design strategies to apply",
        examples=[["equivalence_partitioning", "boundary_value", "state_transition"]]
    )
    include_istqb_format: bool = Field(default=True, description="Include ISTQB-formatted test cases")
    include_execution_plan: bool = Field(default=False, description="Include test execution plan")


class AdvancedTestResponse(BaseModel):
    """Response from advanced test generation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_analisis": "istqb_analysis_1729768200",
                "estado": "completed",
                "csv_cases": "CP - 001 - AUTH - LOGIN - VALID - Successful login with valid credentials\nCP - 002 - AUTH - LOGIN - INVALID - Failed login with invalid password",
                "fichas": [
                    {
                        "id": "TC-001",
                        "precondition": "User account exists",
                        "expected_result": "User logged in successfully"
                    }
                ],
                "artefactos_tecnicos": {
                    "equivalence_partitioning": ["Valid credentials", "Invalid credentials"],
                    "boundary_values": ["Min password length", "Max password length"],
                    "decision_table": "Decision table for authentication scenarios"
                },
                "plan_ejecucion": None,
                "tiempo_procesamiento": 15.2,
                "fecha_creacion": "2024-10-24T10:30:00Z"
            }
        }
    )

    id_analisis: str = Field(..., description="Analysis ID")
    estado: AnalysisStatus = Field(..., description="Analysis status")
    csv_cases: Optional[str] = Field(default=None, description="CSV formatted test cases")
    fichas: Optional[List[Dict[str, Any]]] = Field(default=None, description="Test case cards")
    artefactos_tecnicos: Optional[Dict[str, Any]] = Field(default=None, description="Technical artifacts")
    plan_ejecucion: Optional[str] = Field(default=None, description="Execution plan")
    tiempo_procesamiento: float = Field(..., description="Processing time in seconds")
    fecha_creacion: datetime = Field(..., description="Creation timestamp")
