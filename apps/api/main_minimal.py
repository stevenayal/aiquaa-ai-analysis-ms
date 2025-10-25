"""Minimal FastAPI app for Railway testing."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

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
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "syntaxHighlight.theme": "monokai",
    }
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Redirect to docs."""
    return RedirectResponse(url="/docs")


@app.get("/api/v1/salud")
async def health():
    """Simple health check."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "v1",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "port": os.getenv("PORT", "unknown"),
        "message": "Minimal app running successfully"
    })


@app.get("/debug")
async def debug():
    """Debug endpoint."""
    import sys
    return {
        "python_version": sys.version,
        "python_path": sys.path[:5],
        "environment": {
            "PORT": os.getenv("PORT"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT"),
            "PYTHONPATH": os.getenv("PYTHONPATH"),
            "GOOGLE_API_KEY_SET": bool(os.getenv("GOOGLE_API_KEY")),
        },
        "working_directory": os.getcwd(),
        "files_in_root": os.listdir(".")[:10]
    }


@app.get("/api/v1/status", tags=["health"])
async def status():
    """Get detailed service status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "v1",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "port": os.getenv("PORT", "unknown"),
        "message": "Minimal app running successfully",
        "swagger_available": True,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/api/v1/info", tags=["health"])
async def info():
    """Get service information."""
    return {
        "service": "AIQUAA AI Analysis MS",
        "version": "v1",
        "description": "AI-powered test case generation and quality assurance analysis platform",
        "features": [
            "AI-Powered Analysis",
            "Coverage Analysis", 
            "Jira Integration",
            "Confluence Integration",
            "PII Sanitization",
            "Multi-language Support"
        ],
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
