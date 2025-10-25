"""FastAPI application with complete OpenAPI configuration.

This is the main entry point for the AIQUAA AI Analysis microservice.
It configures:
- OpenAPI/Swagger UI with complete metadata
- Security schemes (API Key + Bearer JWT)
- Tags and external documentation
- CORS middleware
- Error handling
- Structured logging
"""

import sys
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.openapi.utils import get_openapi

from core.config import get_settings
from core.logging import setup_logging, get_logger
from core.constants import API_V1_PREFIX
from schemas.common import ErrorResponse
from apps.api.routes.v1 import health, analysis, jira, confluence
from apps.api.middleware.logging_middleware import LoggingMiddleware
from domain.errors import DomainError

# Setup logging
setup_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(
        "Starting AIQUAA AI Analysis MS",
        version=settings.app_version,
        environment=settings.environment
    )
    yield
    # Shutdown
    logger.info("Shutting down AIQUAA AI Analysis MS")


# OpenAPI Tags with descriptions and external docs
tags_metadata = [
    {
        "name": "health",
        "description": "Health check endpoints for monitoring service status",
        "externalDocs": {
            "description": "Health Check Documentation",
            "url": "https://docs.aiquaa.com/health-checks",
        },
    },
    {
        "name": "analysis",
        "description": "Content analysis and test case generation endpoints. "
                       "Analyze requirements, user stories, and other content to generate test cases.",
        "externalDocs": {
            "description": "Analysis API Guide",
            "url": "https://docs.aiquaa.com/analysis-api",
        },
    },
    {
        "name": "jira",
        "description": "Jira integration endpoints. Analyze Jira work items and generate test cases "
                       "directly from Jira issues.",
        "externalDocs": {
            "description": "Jira Integration Guide",
            "url": "https://docs.aiquaa.com/jira-integration",
        },
    },
    {
        "name": "confluence",
        "description": "Confluence integration endpoints. Generate comprehensive test plans "
                       "for Confluence documentation.",
        "externalDocs": {
            "description": "Confluence Integration Guide",
            "url": "https://docs.aiquaa.com/confluence-integration",
        },
    },
    {
        "name": "admin",
        "description": "Administrative endpoints for system management and diagnostics.",
    },
]


# Initialize FastAPI app with complete OpenAPI configuration
app = FastAPI(
    title="AIQUAA AI Analysis MS",
    version="v1",
    description="""
# AIQUAA AI Analysis Microservice

**AI-powered test case generation and quality assurance analysis platform.**

## Features

* 🤖 **AI-Powered Analysis**: Generate comprehensive test cases using Google Gemini AI
* 📊 **Coverage Analysis**: Automatic test coverage and gap analysis
* 🔗 **Jira Integration**: Direct integration with Jira work items
* 📝 **Confluence Integration**: Generate test plans for Confluence
* 🔒 **PII Sanitization**: Automatic detection and sanitization of sensitive data
* 📈 **Observability**: Full tracing with Langfuse integration
* 🌍 **Multi-language**: Supports English and Spanish parameters

## Authentication

This API supports two authentication methods:

1. **API Key Authentication**: Pass `X-API-Key` header with your API key
2. **Bearer Token (JWT)**: Pass `Authorization: Bearer <token>` header

## Rate Limiting

Requests are rate-limited to 60 requests per minute per API key.

## Support

For support, please contact: support@aiquaa.com
    """,
    terms_of_service="https://aiquaa.com/terms",
    contact={
        "name": "AIQUAA Support Team",
        "url": "https://aiquaa.com/support",
        "email": "support@aiquaa.com",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://aiquaa.com/license",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        },
        {
            "url": "https://aiquaa-ai-analysis-ms-v2-production.up.railway.app",
            "description": "Railway production server"
        },
        {
            "url": "https://api.aiquaa.com",
            "description": "Production server (main)"
        },
    ],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "syntaxHighlight.theme": "monokai",
    }
)


def custom_openapi() -> Dict[str, Any]:
    """Custom OpenAPI schema with security schemes."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
    )

    # Add security schemes
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key for authentication. Contact support@aiquaa.com to obtain an API key."
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer token for authentication. Obtain from /api/v1/auth/login endpoint."
        }
    }

    # Set default security (API Key) for all endpoints
    # Individual routes can override this with dependencies=[]
    openapi_schema["security"] = [{"ApiKeyAuth": []}]

    # Add common error responses to components
    if "schemas" not in openapi_schema["components"]:
        openapi_schema["components"]["schemas"] = {}

    # Ensure ErrorResponse is in components
    openapi_schema["components"]["schemas"]["ErrorResponse"] = {
        "type": "object",
        "required": ["code", "message"],
        "properties": {
            "code": {
                "type": "string",
                "description": "Machine-readable error code",
                "example": "VALIDATION_ERROR"
            },
            "message": {
                "type": "string",
                "description": "Human-readable error message",
                "example": "Invalid input data provided"
            },
            "details": {
                "type": "object",
                "description": "Additional error details (optional)",
                "example": {"field": "content", "error": "Field required"}
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Override OpenAPI schema
app.openapi = custom_openapi


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Logging Middleware
app.add_middleware(LoggingMiddleware)


# Exception Handlers
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    """Handle domain errors."""
    logger.error(
        "Domain error occurred",
        error_code=exc.code,
        error_message=exc.message,
        path=request.url.path
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=request.url.path
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid request data",
            details={"errors": exc.errors()}
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(
        "Unexpected error occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
            details={"error_type": type(exc).__name__} if settings.debug else None
        ).model_dump()
    )


# Root redirect
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


# Include routers
app.include_router(
    health.router,
    prefix=API_V1_PREFIX,
    tags=["health"]
)

app.include_router(
    analysis.router,
    prefix=API_V1_PREFIX,
    tags=["analysis"]
)

app.include_router(
    jira.router,
    prefix=API_V1_PREFIX,
    tags=["jira"]
)

app.include_router(
    confluence.router,
    prefix=API_V1_PREFIX,
    tags=["confluence"]
)


# CLI support for exporting OpenAPI schema
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="AIQUAA AI Analysis MS")
    parser.add_argument(
        "--export-openapi",
        type=str,
        help="Export OpenAPI schema to file"
    )
    args = parser.parse_args()

    if args.export_openapi:
        # Export OpenAPI schema
        schema = custom_openapi()
        with open(args.export_openapi, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        print(f"OpenAPI schema exported to: {args.export_openapi}")
        sys.exit(0)

    # Run server
    import uvicorn
    uvicorn.run(
        "apps.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
