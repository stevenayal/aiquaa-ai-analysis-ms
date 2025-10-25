"""Analysis endpoints for content analysis and test generation."""

from fastapi import APIRouter, Depends, status, BackgroundTasks

from schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AdvancedTestRequest,
    AdvancedTestResponse
)
from schemas.common import ErrorResponse
from domain.services import AnalysisService
from apps.api.deps import get_analysis_service
from core.config import get_settings

router = APIRouter()
settings = get_settings()


# Common error responses
error_responses = {
    400: {
        "model": ErrorResponse,
        "description": "Bad Request - Invalid input data",
        "content": {
            "application/json": {
                "example": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid content type provided",
                    "details": {"field": "content_type", "allowed_values": ["requirement", "test_case", "user_story", "general"]}
                }
            }
        }
    },
    422: {
        "model": ErrorResponse,
        "description": "Unprocessable Entity - Validation failed",
        "content": {
            "application/json": {
                "example": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                    "details": {"errors": [{"loc": ["body", "content"], "msg": "field required", "type": "value_error.missing"}]}
                }
            }
        }
    },
    429: {
        "model": ErrorResponse,
        "description": "Too Many Requests - Rate limit exceeded",
        "content": {
            "application/json": {
                "example": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded. Please try again later.",
                    "details": {"limit": "60 requests per minute", "retry_after": 30}
                }
            }
        }
    },
    500: {
        "model": ErrorResponse,
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": None
                }
            }
        }
    }
}


@router.post(
    "/analizar",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    responses=error_responses,
    summary="Analyze Content",
    description="Analyze content and generate comprehensive test cases with AI"
)
async def analyze_content(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Analyze content (requirements, user stories, etc.) and generate test cases.

    This endpoint uses AI to analyze the provided content and generate:
    - **Test cases**: Comprehensive test cases covering functional and edge cases
    - **Coverage analysis**: Analysis of test coverage gaps
    - **Suggestions**: Recommendations for improving test coverage

    **Supports both English and Spanish parameters** based on the `USE_SPANISH_PARAMS` feature flag.

    ### Example Request (English):
    ```json
    {
        "content": "As a user, I want to reset my password...",
        "content_type": "user_story",
        "analysis_level": "comprehensive"
    }
    ```

    ### Example Request (Spanish):
    ```json
    {
        "contenido": "Como usuario, quiero restablecer mi contraseña...",
        "tipo_contenido": "user_story",
        "nivel_analisis": "comprehensive"
    }
    ```
    """
    # Perform analysis
    result = await service.analyze_content(
        content=request.get_content(),
        content_type=request.get_content_type(),
        analysis_level=request.get_analysis_level(),
        sanitize_pii=settings.enable_pii_sanitization
    )

    return AnalysisResponse(**result)


@router.post(
    "/generar-pruebas-avanzadas",
    response_model=AdvancedTestResponse,
    status_code=status.HTTP_200_OK,
    responses=error_responses,
    summary="Generate Advanced Test Cases",
    description="Generate advanced test cases using ISTQB techniques"
)
async def generate_advanced_tests(
    request: AdvancedTestRequest,
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Generate advanced test cases using ISTQB Foundation Level techniques.

    This endpoint applies professional test design strategies including:
    - **Equivalence Partitioning**: Divide input data into valid/invalid partitions
    - **Boundary Value Analysis**: Test values at boundaries
    - **Decision Tables**: Cover all combinations of conditions
    - **State Transition**: Test state changes
    - **Use Case Testing**: Derive tests from use cases
    - **Error Guessing**: Apply experience-based testing

    Returns:
    - **CSV cases**: Test cases in CSV format (CP - NNN - PROGRAM - MODULE - CONDITION - SCENARIO)
    - **Test cards**: Detailed test case cards with preconditions and expected results
    - **Technical artifacts**: Equivalence classes, boundary values, decision tables, etc.
    - **Execution plan**: Optional test execution plan in cursor_playwright_mcp format

    ### Example Request:
    ```json
    {
        "requirement": "The system shall support user authentication via OAuth 2.0",
        "strategies": ["equivalence_partitioning", "boundary_value", "decision_table"],
        "include_istqb_format": true,
        "include_execution_plan": false
    }
    ```
    """
    result = await service.generate_advanced_tests(
        requirement=request.requirement,
        strategies=request.strategies or [],
        include_istqb_format=request.include_istqb_format,
        include_execution_plan=request.include_execution_plan
    )

    return AdvancedTestResponse(**result)
