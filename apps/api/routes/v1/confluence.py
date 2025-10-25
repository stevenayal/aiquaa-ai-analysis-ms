"""Confluence integration endpoints."""

from fastapi import APIRouter, Depends, status

from schemas.confluence import ConfluenceTestPlanRequest, ConfluenceTestPlanResponse
from schemas.common import ErrorResponse
from domain.services import ConfluenceService
from apps.api.deps import get_confluence_service

router = APIRouter()


error_responses = {
    400: {"model": ErrorResponse, "description": "Bad Request"},
    404: {
        "model": ErrorResponse,
        "description": "Jira issue not found",
        "content": {
            "application/json": {
                "example": {
                    "code": "NOT_FOUND",
                    "message": "Jira issue not found",
                    "details": {"jira_issue_id": "PROJ-999"}
                }
            }
        }
    },
    422: {"model": ErrorResponse, "description": "Validation Error"},
    429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"}
}


@router.post(
    "/analizar-jira-confluence",
    response_model=ConfluenceTestPlanResponse,
    status_code=status.HTTP_200_OK,
    responses=error_responses,
    summary="Generate Confluence Test Plan",
    description="Generate a comprehensive test plan for Confluence from a Jira issue"
)
async def generate_confluence_test_plan(
    request: ConfluenceTestPlanRequest,
    service: ConfluenceService = Depends(get_confluence_service)
):
    """
    Generate a comprehensive test plan for Confluence documentation.

    This endpoint:
    1. Fetches Jira issue details
    2. Generates a structured test plan with multiple sections
    3. Creates test cases
    4. Organizes test execution phases

    **Supports both English and Spanish parameters**.

    ### Example Request (English):
    ```json
    {
        "jira_issue_id": "PROJ-123",
        "confluence_space_key": "QA",
        "test_plan_title": "Test Plan - User Authentication Feature"
    }
    ```

    ### Example Request (Spanish):
    ```json
    {
        "id_issue_jira": "PROJ-456",
        "espacio_confluence": "QA",
        "titulo_plan_pruebas": "Plan de Pruebas - Autenticación de Usuarios"
    }
    ```

    ### Response includes:
    - Test plan sections (Introduction, Test Strategy, Scope, etc.)
    - Generated test cases
    - Test execution phases
    - Confidence score
    """
    result = await service.generate_test_plan(
        jira_issue_id=request.get_jira_issue_id(),
        confluence_space_key=request.get_confluence_space_key(),
        test_plan_title=request.get_test_plan_title()
    )

    return ConfluenceTestPlanResponse(**result)
