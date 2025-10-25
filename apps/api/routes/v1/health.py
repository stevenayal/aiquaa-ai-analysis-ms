"""Health check endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, status

from schemas.common import HealthResponse, LLMDiagnosticResponse, ErrorResponse
from infrastructure.ai import LLMWrapper
from infrastructure.http import TrackerClient
from infrastructure.telemetry import LangfuseClient
from apps.api.deps import get_llm_wrapper, get_tracker_client
from core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get(
    "/salud",
    response_model=HealthResponse,
    responses={
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "Health check failed",
                        "details": {"service": "llm", "error": "Connection timeout"}
                    }
                }
            }
        }
    },
    summary="Health Check",
    description="Check the health status of the service and its dependencies",
    dependencies=[]  # Public endpoint - no authentication required
)
async def health_check(
    llm: LLMWrapper = Depends(get_llm_wrapper),
    jira: TrackerClient = Depends(get_tracker_client)
):
    """
    Perform health check on all service dependencies.

    Returns the overall health status along with the status of individual services:
    - **LLM**: Google Gemini AI connection
    - **Jira**: Jira API connection (if configured)
    - **Langfuse**: Observability service (if configured)

    This endpoint does not require authentication.
    """
    services = {}

    # Check LLM
    try:
        llm_healthy = await llm.test_connection()
        services["llm"] = "healthy" if llm_healthy else "unhealthy"
    except Exception:
        services["llm"] = "unhealthy"

    # Check Jira (if configured)
    if settings.jira_configured:
        try:
            jira_healthy = await jira.health_check()
            services["jira"] = "healthy" if jira_healthy else "unhealthy"
        except Exception:
            services["jira"] = "unhealthy"
    else:
        services["jira"] = "not_configured"

    # Check Langfuse (if configured)
    if settings.langfuse_configured:
        try:
            langfuse_client = LangfuseClient()
            langfuse_healthy = await langfuse_client.health_check()
            services["langfuse"] = "healthy" if langfuse_healthy else "unhealthy"
        except Exception:
            services["langfuse"] = "unhealthy"
    else:
        services["langfuse"] = "not_configured"

    # Determine overall status
    unhealthy_services = [k for k, v in services.items() if v == "unhealthy"]
    overall_status = "degraded" if unhealthy_services else "healthy"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        services=services,
        feature_flags={
            "use_spanish_params": settings.use_spanish_params,
            "enable_pii_sanitization": settings.enable_pii_sanitization,
            "enable_rate_limiting": settings.enable_rate_limiting,
        }
    )


@router.get(
    "/diagnostico-llm",
    response_model=LLMDiagnosticResponse,
    responses={
        500: {
            "model": ErrorResponse,
            "description": "LLM connection failed"
        }
    },
    summary="LLM Diagnostic",
    description="Perform diagnostic check on LLM connection",
    dependencies=[]  # Public endpoint
)
async def llm_diagnostic(llm: LLMWrapper = Depends(get_llm_wrapper)):
    """
    Test LLM connection and return diagnostic information.

    This endpoint performs a test connection to Google Gemini AI
    and returns information about the connection status and configuration.

    This endpoint does not require authentication.
    """
    try:
        is_connected = await llm.test_connection()

        return LLMDiagnosticResponse(
            status="connected" if is_connected else "disconnected",
            model=settings.gemini_model,
            langfuse_enabled=settings.langfuse_configured,
            test_message="LLM connection successful" if is_connected else None,
            timestamp=datetime.utcnow(),
            error=None if is_connected else "Connection test failed"
        )
    except Exception as e:
        return LLMDiagnosticResponse(
            status="error",
            model=settings.gemini_model,
            langfuse_enabled=settings.langfuse_configured,
            test_message=None,
            timestamp=datetime.utcnow(),
            error=str(e)
        )
