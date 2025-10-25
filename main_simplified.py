"""
Microservicio de Análisis QA - Versión Simplificada
FastAPI Service para análisis automatizado de casos de prueba
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Importar módulos locales
from tracker_client import TrackerClient
from llm_wrapper import LLMWrapper
from prompt_templates import PromptTemplates
from sanitizer import PIISanitizer

# Importar endpoints simplificados
from jira_endpoints import JiraAnalysisRequest, analyze_jira_workitem, analyze_jira_workitem_simple
from confluence_endpoints import ConfluenceTestPlanRequest, analyze_jira_confluence, analyze_jira_confluence_simple
from basic_endpoints import AnalysisRequest, analyze_content, generate_advanced_tests

# Cargar variables de entorno
load_dotenv()

# Feature flags
USE_SPANISH_PARAMS = os.getenv("USE_SPANISH_PARAMS", "false").lower() == "true"

# Configurar logging estructurado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Inicializar FastAPI
app = FastAPI(
    title="Microservicio de Análisis QA - Simplificado",
    description="""
    ## API de Análisis Automatizado de Casos de Prueba - Versión Simplificada
    
    API simplificada que soporta tanto parámetros en inglés como en español mediante feature flag.
    
    ### Feature Flag:
    - `USE_SPANISH_PARAMS=false` (por defecto): Parámetros en inglés
    - `USE_SPANISH_PARAMS=true`: Parámetros en español
    
    ### Endpoints Disponibles:
    - **Análisis Básico**: `/analizar` - Análisis de contenido general
    - **Análisis de Jira**: `/analizar-jira` - Análisis de work items de Jira
    - **Análisis Simplificado de Jira**: `/analizar-jira-simple` - Versión rápida
    - **Análisis Jira-Confluence**: `/analizar-jira-confluence` - Planes de prueba para Confluence
    - **Análisis Simplificado Jira-Confluence**: `/analizar-jira-confluence-simple` - Versión rápida
    - **Generación Avanzada**: `/generar-pruebas-avanzadas` - Casos de prueba avanzados
    - **Salud**: `/salud` - Estado del servicio
    - **Diagnóstico LLM**: `/diagnostico-llm` - Diagnóstico de conectividad LLM
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Inicializar componentes
tracker_client = TrackerClient()
llm_wrapper = LLMWrapper()
prompt_templates = PromptTemplates()
sanitizer = PIISanitizer()

# Modelos de respuesta
class HealthResponse(BaseModel):
    status: str = Field(..., description="Estado del servicio")
    timestamp: str = Field(..., description="Timestamp de la respuesta")
    version: str = Field(..., description="Versión del servicio")
    feature_flags: Dict[str, Any] = Field(..., description="Estado de los feature flags")

class LLMDiagnosticResponse(BaseModel):
    status: str = Field(..., description="Estado del diagnóstico")
    response_time: float = Field(..., description="Tiempo de respuesta en segundos")
    timestamp: str = Field(..., description="Timestamp del diagnóstico")
    llm_available: bool = Field(..., description="Disponibilidad del LLM")

# Background tasks
async def log_analysis_completion(analysis_id: str, content_type: str, response: Dict[str, Any]):
    """Log completion of analysis"""
    logger.info(
        "Analysis completed",
        analysis_id=analysis_id,
        content_type=content_type,
        test_cases_count=len(response.get("casos_prueba", [])),
        processing_time=response.get("tiempo_procesamiento", 0)
    )

async def log_jira_workitem_analysis_completion(analysis_id: str, work_item_id: str, response: Dict[str, Any]):
    """Log completion of Jira work item analysis"""
    logger.info(
        "Jira work item analysis completed",
        analysis_id=analysis_id,
        work_item_id=work_item_id,
        test_cases_count=len(response.get("casos_prueba", [])),
        processing_time=response.get("tiempo_procesamiento", 0)
    )

async def log_confluence_analysis_completion(analysis_id: str, jira_issue_id: str, response: Dict[str, Any]):
    """Log completion of Confluence analysis"""
    logger.info(
        "Confluence analysis completed",
        analysis_id=analysis_id,
        jira_issue_id=jira_issue_id,
        test_cases_count=len(response.get("casos_prueba", [])),
        processing_time=response.get("processing_time", 0)
    )

# Endpoints
@app.get("/", response_class=RedirectResponse)
async def root():
    """Redirect to docs"""
    return RedirectResponse(url="/docs")

@app.get("/salud", response_model=HealthResponse, tags=["Sistema"])
async def health_check():
    """Verificar estado del servicio"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="2.0.0",
        feature_flags={
            "USE_SPANISH_PARAMS": USE_SPANISH_PARAMS,
            "JIRA_ENABLED": True,
            "CONFLUENCE_ENABLED": True,
            "LLM_ENABLED": True
        }
    )

@app.get("/diagnostico-llm", response_model=LLMDiagnosticResponse, tags=["Sistema"])
async def llm_diagnostic():
    """Diagnóstico de conectividad LLM"""
    start_time = datetime.utcnow()
    
    try:
        # Test simple con LLM
        test_prompt = "Responde solo con 'OK' si puedes procesar este mensaje."
        test_result = await llm_wrapper.analyze_requirements(
            prompt=test_prompt,
            requirement_id="test",
            analysis_id="diagnostic"
        )
        
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        return LLMDiagnosticResponse(
            status="success",
            response_time=response_time,
            timestamp=datetime.utcnow().isoformat(),
            llm_available=True
        )
        
    except Exception as e:
        response_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error("LLM diagnostic failed", error=str(e), response_time=response_time)
        
        return LLMDiagnosticResponse(
            status="error",
            response_time=response_time,
            timestamp=datetime.utcnow().isoformat(),
            llm_available=False
        )

@app.post("/analizar", tags=["Análisis Básico"])
async def analyze_content_endpoint(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Análisis de contenido general"""
    try:
        response = await analyze_content(
            request=request,
            llm_wrapper=llm_wrapper,
            prompt_templates=prompt_templates,
            sanitizer=sanitizer,
            background_tasks=background_tasks
        )
        
        # Log completion
        background_tasks.add_task(
            log_analysis_completion,
            response["id_contenido"],
            response["tipo_contenido"],
            response
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Content analysis endpoint failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/analizar-jira", tags=["Integración Jira"])
async def analyze_jira_endpoint(
    request: JiraAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Análisis de work item de Jira"""
    try:
        response = await analyze_jira_workitem(
            request=request,
            tracker_client=tracker_client,
            llm_wrapper=llm_wrapper,
            prompt_templates=prompt_templates,
            sanitizer=sanitizer,
            background_tasks=background_tasks
        )
        
        # Log completion
        background_tasks.add_task(
            log_jira_workitem_analysis_completion,
            response["id_analisis"],
            response["id_work_item"],
            response
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Jira analysis endpoint failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/analizar-jira-simple", tags=["Integración Jira"])
async def analyze_jira_simple_endpoint(
    request: JiraAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Análisis simplificado de work item de Jira"""
    try:
        response = await analyze_jira_workitem_simple(
            request=request,
            tracker_client=tracker_client,
            llm_wrapper=llm_wrapper,
            sanitizer=sanitizer,
            background_tasks=background_tasks
        )
        
        # Log completion
        background_tasks.add_task(
            log_jira_workitem_analysis_completion,
            response["id_analisis"],
            response["id_work_item"],
            response
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Jira simple analysis endpoint failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/analizar-jira-confluence", tags=["Integración Confluence"])
async def analyze_jira_confluence_endpoint(
    request: ConfluenceTestPlanRequest,
    background_tasks: BackgroundTasks
):
    """Análisis de Jira y diseño de plan de pruebas para Confluence"""
    try:
        response = await analyze_jira_confluence(
            request=request,
            tracker_client=tracker_client,
            llm_wrapper=llm_wrapper,
            prompt_templates=prompt_templates,
            sanitizer=sanitizer,
            background_tasks=background_tasks
        )
        
        # Log completion
        background_tasks.add_task(
            log_confluence_analysis_completion,
            response["id_analisis"],
            response["id_issue_jira"],
            response
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Jira-Confluence analysis endpoint failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/analizar-jira-confluence-simple", tags=["Integración Confluence"])
async def analyze_jira_confluence_simple_endpoint(
    request: ConfluenceTestPlanRequest,
    background_tasks: BackgroundTasks
):
    """Análisis simplificado de Jira y diseño de plan de pruebas para Confluence"""
    try:
        response = await analyze_jira_confluence_simple(
            request=request,
            tracker_client=tracker_client,
            llm_wrapper=llm_wrapper,
            sanitizer=sanitizer,
            background_tasks=background_tasks
        )
        
        # Log completion
        background_tasks.add_task(
            log_confluence_analysis_completion,
            response["id_analisis"],
            response["id_issue_jira"],
            response
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Jira-Confluence simple analysis endpoint failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/generar-pruebas-avanzadas", tags=["Generación Avanzada"])
async def generate_advanced_tests_endpoint(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Generación avanzada de casos de prueba"""
    try:
        response = await generate_advanced_tests(
            request=request,
            llm_wrapper=llm_wrapper,
            prompt_templates=prompt_templates,
            sanitizer=sanitizer,
            background_tasks=background_tasks
        )
        
        # Log completion
        background_tasks.add_task(
            log_analysis_completion,
            response["id_contenido"],
            response["tipo_contenido"],
            response
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Advanced test generation endpoint failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
