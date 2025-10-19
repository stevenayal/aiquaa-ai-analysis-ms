"""
Microservicio de Análisis QA - Versión Simple
FastAPI Service para análisis automatizado de casos de prueba
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar FastAPI
app = FastAPI(
    title="Microservicio de Análisis QA",
    description="API de Análisis Automatizado de Casos de Prueba",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    servers=[
        {
            "url": "https://ia-analisis-production.up.railway.app",
            "description": "Servidor de producción en Railway"
        },
        {
            "url": "http://localhost:8000",
            "description": "Servidor de desarrollo local"
        }
    ]
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class TestCase(BaseModel):
    test_case_id: str
    title: str
    description: str
    test_type: str
    priority: str
    steps: List[str]
    expected_result: str
    preconditions: List[str]
    test_data: Dict[str, Any]
    automation_potential: str
    estimated_duration: str

class AnalysisRequest(BaseModel):
    content_id: str
    content: str
    content_type: str = "test_case"
    analysis_level: Optional[str] = "medium"

class AnalysisResponse(BaseModel):
    content_id: str
    analysis_id: str
    status: str
    test_cases: List[TestCase]
    confidence_score: float
    processing_time: float
    created_at: datetime

class AdvancedTestGenerationRequest(BaseModel):
    requerimiento: str
    aplicacion: str
    modulo: str
    servicio_publicado: Optional[str] = None

class AdvancedTestGenerationResponse(BaseModel):
    aplicacion: str
    generation_id: str
    status: str
    test_cases: List[TestCase]
    coverage_analysis: Dict[str, Any]
    confidence_score: float
    processing_time: float
    created_at: datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    components: Dict[str, str]

# Endpoints
@app.get("/")
async def root():
    return {
        "message": "Microservicio de Análisis QA",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        components={
            "api": "healthy",
            "database": "not_configured",
            "llm": "not_configured",
            "jira": "not_configured"
        }
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    start_time = datetime.utcnow()
    analysis_id = f"analysis_{request.content_id}_{int(start_time.timestamp())}"
    
    test_cases = [
        TestCase(
            test_case_id=f"CP-001-{request.content_id}-MODULO-DATO-CONDICION-RESULTADO",
            title=f"CP - 001 - {request.content_id} - MODULO - DATO - CONDICION - RESULTADO",
            description="Caso de prueba generado automáticamente",
            test_type="functional",
            priority="high",
            steps=[
                "Paso 1: Preparar el entorno de prueba",
                "Paso 2: Ejecutar la acción principal",
                "Paso 3: Verificar el resultado"
            ],
            expected_result="Resultado Esperado: Operación completada exitosamente",
            preconditions=["Precondicion: Sistema inicializado", "Precondicion: Datos de prueba disponibles"],
            test_data={"input": "datos de prueba"},
            automation_potential="high",
            estimated_duration="5-10 minutes"
        )
    ]
    
    processing_time = (datetime.utcnow() - start_time).total_seconds()
    
    return AnalysisResponse(
        content_id=request.content_id,
        analysis_id=analysis_id,
        status="completed",
        test_cases=test_cases,
        confidence_score=0.85,
        processing_time=processing_time,
        created_at=start_time
    )

@app.post("/generate-advanced-tests", response_model=AdvancedTestGenerationResponse)
async def generate_advanced_test_cases(request: AdvancedTestGenerationRequest):
    start_time = datetime.utcnow()
    generation_id = f"advanced_{request.aplicacion}_{int(start_time.timestamp())}"
    
    test_cases = []
    for i in range(1, 4):
        test_case_id = f"CP-{i:03d}-{request.aplicacion}-{request.modulo}-DATO-CONDICION-RESULTADO"
        title = f"CP - {i:03d} - {request.aplicacion} - {request.modulo} - DATO - CONDICION - RESULTADO"
        
        preconditions = ["Precondicion: Sistema inicializado", "Precondicion: Datos de prueba disponibles"]
        if request.servicio_publicado:
            preconditions.insert(0, f"Precondicion: Ingresar al publicado {request.servicio_publicado}")
        
        test_case = TestCase(
            test_case_id=test_case_id,
            title=title,
            description=f"Caso de prueba {i} generado para {request.aplicacion} - {request.modulo}",
            test_type="functional",
            priority="high",
            steps=[
                f"Paso 1: Preparar el entorno de prueba para {request.modulo}",
                f"Paso 2: Ejecutar la acción principal del caso {i}",
                f"Paso 3: Verificar el resultado esperado"
            ],
            expected_result=f"Resultado Esperado: Operación {i} completada exitosamente en {request.modulo}",
            preconditions=preconditions,
            test_data={"aplicacion": request.aplicacion, "modulo": request.modulo},
            automation_potential="high",
            estimated_duration="5-10 minutes"
        )
        test_cases.append(test_case)
    
    processing_time = (datetime.utcnow() - start_time).total_seconds()
    
    return AdvancedTestGenerationResponse(
        aplicacion=request.aplicacion,
        generation_id=generation_id,
        status="completed",
        test_cases=test_cases,
        coverage_analysis={
            "functional_coverage": "90%",
            "edge_case_coverage": "75%",
            "integration_coverage": "80%"
        },
        confidence_score=0.85,
        processing_time=processing_time,
        created_at=start_time
    )

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"Starting Microservicio de Análisis QA - Port: {port}, Log Level: {log_level}")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level=log_level,
        access_log=True
    )
