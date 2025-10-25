"""Common schemas used across the API."""

from typing import Any, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ErrorResponse(BaseModel):
    """Standard error response.

    Used for all error responses across the API to ensure consistency.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data provided",
                "details": {
                    "field": "content",
                    "error": "Field required"
                }
            }
        }
    )

    code: str = Field(
        ...,
        description="Machine-readable error code",
        examples=["VALIDATION_ERROR", "NOT_FOUND", "EXTERNAL_SERVICE_ERROR"]
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Invalid input data provided"]
    )
    details: Optional[Any] = Field(
        default=None,
        description="Additional error details (optional)",
        examples=[{"field": "content", "error": "Field required"}]
    )


class HealthResponse(BaseModel):
    """Health check response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2024-10-24T10:30:00Z",
                "version": "v1",
                "services": {
                    "llm": "healthy",
                    "jira": "healthy",
                    "langfuse": "healthy"
                },
                "feature_flags": {
                    "use_spanish_params": False,
                    "enable_pii_sanitization": True
                }
            }
        }
    )

    status: str = Field(
        ...,
        description="Overall health status",
        examples=["healthy", "degraded", "unhealthy"]
    )
    timestamp: datetime = Field(
        ...,
        description="Health check timestamp"
    )
    version: str = Field(
        ...,
        description="API version",
        examples=["v1"]
    )
    services: Dict[str, str] = Field(
        default_factory=dict,
        description="Status of individual services"
    )
    feature_flags: Optional[Dict[str, bool]] = Field(
        default=None,
        description="Active feature flags"
    )


class LLMDiagnosticResponse(BaseModel):
    """LLM diagnostic response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "connected",
                "model": "gemini-pro",
                "langfuse_enabled": True,
                "test_message": "LLM connection successful",
                "timestamp": "2024-10-24T10:30:00Z"
            }
        }
    )

    status: str = Field(
        ...,
        description="LLM connection status",
        examples=["connected", "disconnected", "error"]
    )
    model: str = Field(
        ...,
        description="LLM model name",
        examples=["gemini-pro"]
    )
    langfuse_enabled: bool = Field(
        ...,
        description="Whether Langfuse observability is enabled"
    )
    test_message: Optional[str] = Field(
        default=None,
        description="Test message from LLM (if successful)"
    )
    timestamp: datetime = Field(
        ...,
        description="Diagnostic timestamp"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if connection failed"
    )
