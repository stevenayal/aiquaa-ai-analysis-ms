"""Jira integration endpoints."""

from fastapi import APIRouter, Depends, status

from schemas.jira import JiraAnalysisRequest, JiraAnalysisResponse
from schemas.common import ErrorResponse
from domain.services import JiraService
from apps.api.deps import get_jira_service

router = APIRouter()


error_responses = {
    400: {"model": ErrorResponse, "description": "Bad Request"},
    404: {
        "model": ErrorResponse,
        "description": "Jira work item not found",
        "content": {
            "application/json": {
                "example": {
                    "code": "NOT_FOUND",
                    "message": "Jira work item not found",
                    "details": {"work_item_id": "PROJ-999"}
                }
            }
        }
    },
    422: {"model": ErrorResponse, "description": "Validation Error"},
    429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"}
}


@router.post(
    "/analizar-jira",
    response_model=JiraAnalysisResponse,
    status_code=status.HTTP_200_OK,
    responses=error_responses,
    summary="Analyze Jira Work Item",
    description="Analyze a Jira work item and generate test cases"
)
async def analyze_jira_workitem(
    request: JiraAnalysisRequest,
    service: JiraService = Depends(get_jira_service)
):
    """
    Analyze a Jira work item and generate comprehensive test cases.

    This endpoint:
    1. Fetches work item details from Jira (title, description, acceptance criteria, etc.)
    2. Analyzes the work item using AI
    3. Generates test cases tailored to the work item
    4. Provides coverage analysis

    **Supports both English and Spanish parameters**.

    ### Example Request (English):
    ```json
    {
        "work_item_id": "PROJ-123",
        "analysis_level": "comprehensive"
    }
    ```

    ### Example Request (Spanish):
    ```json
    {
        "id_work_item": "PROJ-456",
        "nivel_analisis": "detailed"
    }
    ```

    ### Response includes:
    - Jira work item data (summary, description, type, priority, status, acceptance criteria)
    - Generated test cases
    - Coverage analysis
    - Confidence score
    """
    result = await service.analyze_work_item(
        work_item_id=request.get_work_item_id(),
        analysis_level=request.get_analysis_level()
    )

    return JiraAnalysisResponse(**result)
