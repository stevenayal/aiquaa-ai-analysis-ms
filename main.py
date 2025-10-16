"""
Microservicio de Análisis QA con Langfuse
FastAPI Service para análisis automatizado de casos de prueba
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Importar módulos locales
from tracker_client import TrackerClient
from llm_wrapper import LLMWrapper
from prompt_templates import PromptTemplates
from sanitizer import PIISanitizer

# Cargar variables de entorno
load_dotenv()

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
    title="Microservicio de Análisis QA",
    description="Análisis automatizado de casos de prueba con observabilidad completa",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Inicializar componentes
tracker_client = TrackerClient()
llm_wrapper = LLMWrapper()
prompt_templates = PromptTemplates()
sanitizer = PIISanitizer()

# Modelos Pydantic
class TestCaseAnalysisRequest(BaseModel):
    """Solicitud de análisis de caso de prueba"""
    test_case_id: str = Field(..., description="ID del caso de prueba")
    test_case_content: str = Field(..., description="Contenido del caso de prueba")
    project_key: str = Field(..., description="Clave del proyecto")
    priority: Optional[str] = Field("Medium", description="Prioridad del caso")
    labels: Optional[List[str]] = Field(default_factory=list, description="Etiquetas del caso")

class TestCaseAnalysisResponse(BaseModel):
    """Respuesta del análisis de caso de prueba"""
    test_case_id: str
    analysis_id: str
    status: str
    suggestions: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    created_at: datetime

class HealthResponse(BaseModel):
    """Respuesta de salud del servicio"""
    status: str
    timestamp: datetime
    version: str
    components: Dict[str, str]

@app.get("/", response_model=Dict[str, str])
async def root():
    """Endpoint raíz"""
    return {
        "message": "Microservicio de Análisis QA",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificación de salud del servicio"""
    components = {}
    
    # Verificar Langfuse
    try:
        await llm_wrapper.health_check()
        components["langfuse"] = "healthy"
    except Exception as e:
        logger.error("Langfuse health check failed", error=str(e))
        components["langfuse"] = "unhealthy"
    
    # Verificar Jira
    try:
        await tracker_client.health_check()
        components["jira"] = "healthy"
    except Exception as e:
        logger.error("Jira health check failed", error=str(e))
        components["jira"] = "unhealthy"
    
    # Verificar LLM
    try:
        await llm_wrapper.test_connection()
        components["llm"] = "healthy"
    except Exception as e:
        logger.error("LLM health check failed", error=str(e))
        components["llm"] = "unhealthy"
    
    overall_status = "healthy" if all(status == "healthy" for status in components.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        components=components
    )

@app.post("/analyze", response_model=TestCaseAnalysisResponse)
async def analyze_test_case(
    request: TestCaseAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analizar un caso de prueba y generar sugerencias de mejora
    """
    start_time = datetime.utcnow()
    analysis_id = f"analysis_{request.test_case_id}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting test case analysis",
            test_case_id=request.test_case_id,
            analysis_id=analysis_id,
            project_key=request.project_key
        )
        
        # Sanitizar contenido sensible
        sanitized_content = sanitizer.sanitize(request.test_case_content)
        
        # Obtener prompt para análisis
        prompt = prompt_templates.get_analysis_prompt(
            test_case_content=sanitized_content,
            project_key=request.project_key,
            priority=request.priority,
            labels=request.labels
        )
        
        # Ejecutar análisis con LLM
        analysis_result = await llm_wrapper.analyze_test_case(
            prompt=prompt,
            test_case_id=request.test_case_id,
            analysis_id=analysis_id
        )
        
        # Procesar sugerencias
        suggestions = []
        if analysis_result.get("suggestions"):
            for suggestion in analysis_result["suggestions"]:
                suggestions.append({
                    "type": suggestion.get("type", "general"),
                    "title": suggestion.get("title", ""),
                    "description": suggestion.get("description", ""),
                    "priority": suggestion.get("priority", "medium"),
                    "category": suggestion.get("category", "improvement")
                })
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = TestCaseAnalysisResponse(
            test_case_id=request.test_case_id,
            analysis_id=analysis_id,
            status="completed",
            suggestions=suggestions,
            confidence_score=analysis_result.get("confidence_score", 0.8),
            processing_time=processing_time,
            created_at=start_time
        )
        
        # Registrar en background task para tracking
        background_tasks.add_task(
            log_analysis_completion,
            analysis_id,
            request.test_case_id,
            response
        )
        
        logger.info(
            "Test case analysis completed",
            test_case_id=request.test_case_id,
            analysis_id=analysis_id,
            suggestions_count=len(suggestions),
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Test case analysis failed",
            test_case_id=request.test_case_id,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing test case: {str(e)}"
        )

@app.post("/batch-analyze")
async def batch_analyze_test_cases(
    requests: List[TestCaseAnalysisRequest],
    background_tasks: BackgroundTasks
):
    """
    Analizar múltiples casos de prueba en lote
    """
    logger.info("Starting batch analysis", count=len(requests))
    
    results = []
    for request in requests:
        try:
            result = await analyze_test_case(request, background_tasks)
            results.append(result)
        except Exception as e:
            logger.error(
                "Failed to analyze test case in batch",
                test_case_id=request.test_case_id,
                error=str(e)
            )
            results.append({
                "test_case_id": request.test_case_id,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "total_processed": len(requests),
        "successful": len([r for r in results if r.get("status") == "completed"]),
        "failed": len([r for r in results if r.get("status") == "failed"]),
        "results": results
    }

@app.get("/analysis/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """
    Obtener resultado de análisis por ID
    """
    try:
        # Aquí implementarías la lógica para recuperar el análisis
        # Por ahora retornamos un placeholder
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "message": "Analysis result retrieval not implemented yet"
        }
    except Exception as e:
        logger.error("Failed to get analysis result", analysis_id=analysis_id, error=str(e))
        raise HTTPException(status_code=404, detail="Analysis not found")

async def log_analysis_completion(
    analysis_id: str,
    test_case_id: str,
    response: TestCaseAnalysisResponse
):
    """Background task para registrar la finalización del análisis"""
    try:
        # Aquí podrías implementar lógica adicional como:
        # - Guardar en base de datos
        # - Enviar notificaciones
        # - Actualizar métricas
        logger.info(
            "Analysis completion logged",
            analysis_id=analysis_id,
            test_case_id=test_case_id
        )
    except Exception as e:
        logger.error(
            "Failed to log analysis completion",
            analysis_id=analysis_id,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    logger.info("Starting Microservicio de Análisis QA", port=port, log_level=log_level)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level=log_level
    )
