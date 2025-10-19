"""
Microservicio de Análisis QA - Versión Mínima
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
    description="""
    ## API de Análisis Automatizado de Casos de Prueba
    
    Esta API proporciona análisis inteligente de contenido (casos de prueba, requerimientos, historias de usuario) utilizando IA generativa y técnicas avanzadas de testing.
    
    ### Características:
    - 🤖 Análisis automatizado con Google Gemini
    - 📊 Observabilidad completa con Langfuse
    - 🔗 Integración simplificada con Jira
    - 📝 Generación de casos de prueba estructurados
    - 🎯 **NUEVO**: Generación de casos con técnicas avanzadas
    - 🔬 **NUEVO**: Aplicación automática de técnicas de diseño de pruebas
    - 📋 **NUEVO**: Formato estructurado estandarizado
    - ⚡ **OPTIMIZADO**: Endpoints unificados y parámetros simplificados
    
    ### Técnicas Aplicadas Automáticamente:
    - **Partición de Equivalencia**: Clases válidas e inválidas
    - **Valores Límite**: Casos boundary y edge cases
    - **Casos de Uso**: Flujos principales y alternos
    - **Casos de Error**: Validaciones y manejo de errores
    - **Casos de Integración**: Flujos end-to-end
    - **Casos de Seguridad**: Autenticación y autorización
    
    ### Autenticación:
    No se requiere autenticación para las pruebas locales.
    
    ### Uso Simplificado:
    1. **Análisis unificado**: Usa `/analyze` para cualquier tipo de contenido
    2. **Integración Jira**: Usa `/analyze-jira` para work items (solo ID requerido)
    3. **Generación avanzada**: Usa `/generate-advanced-tests` para casos avanzados
    4. **Monitoreo**: Verifica el estado con `/health`
    
    ### Tipos de Contenido Soportados:
    - **test_case**: Análisis de casos de prueba existentes
    - **requirement**: Análisis de requerimientos
    - **user_story**: Análisis de historias de usuario
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Equipo de QA",
        "email": "qa-team@company.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
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

# Configurar CORS para Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ia-analisis-production.up.railway.app",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar TrustedHostMiddleware para Railway
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "ia-analisis-production.up.railway.app",
        "localhost",
        "127.0.0.1",
        "*.railway.app"
    ]
)

# Modelos Pydantic
class TestCase(BaseModel):
    """Caso de prueba generado con estructura estandarizada"""
    test_case_id: str = Field(..., description="ID del caso de prueba", example="CP-001-APLICACION-MODULO-DATO-CONDICION-RESULTADO")
    title: str = Field(..., description="Título del caso de prueba en formato CP - 001 - Aplicacion - Modulo - Dato - Condicion - Resultado", example="CP - 001 - Aplicacion - Modulo - Dato - Condicion - Resultado")
    description: str = Field(..., description="Descripción detallada del caso de prueba")
    test_type: str = Field(..., description="Tipo de prueba", example="functional")
    priority: str = Field(..., description="Prioridad del caso de prueba", example="high")
    steps: List[str] = Field(..., description="Pasos detallados del caso de prueba")
    expected_result: str = Field(..., description="Resultado esperado en formato 'Resultado Esperado: [descripción]'", example="Resultado Esperado: Usuario autenticado exitosamente y redirigido al dashboard")
    preconditions: List[str] = Field(default_factory=list, description="Precondiciones en formato 'Precondicion: [descripción]'", example=["Precondicion: Usuario existe en la base de datos", "Precondicion: Sistema de autenticación activo"])
    test_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Datos de prueba específicos")
    automation_potential: str = Field(..., description="Potencial de automatización", example="high")
    estimated_duration: str = Field(..., description="Duración estimada", example="5-10 minutes")

class AnalysisRequest(BaseModel):
    """Solicitud unificada de análisis de contenido para generar casos de prueba"""
    content_id: str = Field(..., description="ID único del contenido a analizar", example="TC-001", min_length=1, max_length=50)
    content: str = Field(..., description="Contenido a analizar (caso de prueba, requerimiento, historia de usuario)", example="Verificar que el usuario pueda iniciar sesión con credenciales válidas", min_length=10, max_length=10000)
    content_type: str = Field("test_case", description="Tipo de contenido a analizar", example="test_case", pattern="^(test_case|requirement|user_story)$")
    analysis_level: Optional[str] = Field("medium", description="Nivel de análisis y cobertura", example="high", pattern="^(low|medium|high|comprehensive)$")

class AnalysisResponse(BaseModel):
    """Respuesta unificada del análisis de contenido"""
    content_id: str = Field(..., description="ID del contenido analizado", example="TC-001")
    analysis_id: str = Field(..., description="ID único del análisis", example="analysis_TC001_1760825804")
    status: str = Field(..., description="Estado del análisis", example="completed")
    test_cases: List[TestCase] = Field(default_factory=list, description="Lista de casos de prueba generados")
    confidence_score: float = Field(..., description="Puntuación de confianza del análisis (0-1)", example=0.85)
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos", example=8.81)
    created_at: datetime = Field(..., description="Timestamp de creación del análisis")

class AdvancedTestGenerationRequest(BaseModel):
    """Solicitud simplificada de generación de casos de prueba avanzados"""
    requerimiento: str = Field(..., description="Requerimiento completo a analizar y generar casos de prueba", example="El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado.", min_length=50, max_length=5000)
    aplicacion: str = Field(..., description="Nombre de la aplicación o sistema", example="SISTEMA_AUTH", min_length=1, max_length=50)
    modulo: str = Field(..., description="Módulo específico del sistema que se va a probar", example="AUTENTICACION", min_length=1, max_length=50)
    servicio_publicado: Optional[str] = Field(None, description="URL o nombre del servicio publicado (si existe)", example="https://auth.sistema.com/login", max_length=200)

class AdvancedTestGenerationResponse(BaseModel):
    """Respuesta de la generación de casos de prueba avanzados"""
    aplicacion: str = Field(..., description="Nombre de la aplicación", example="SISTEMA_AUTH")
    generation_id: str = Field(..., description="ID único de la generación", example="advanced_SISTEMA_AUTH_1760825804")
    status: str = Field(..., description="Estado de la generación", example="completed")
    test_cases: List[TestCase] = Field(..., description="Lista de casos de prueba generados")
    coverage_analysis: Dict[str, Any] = Field(..., description="Análisis de cobertura de pruebas")
    confidence_score: float = Field(..., description="Puntuación de confianza (0-1)", example=0.85)
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos", example=25.3)
    created_at: datetime = Field(..., description="Timestamp de creación")

class HealthResponse(BaseModel):
    """Respuesta de salud del servicio"""
    status: str
    timestamp: datetime
    version: str
    components: Dict[str, str]

# Endpoint raíz
@app.get("/", 
         summary="Información del servicio",
         description="Endpoint raíz que proporciona información básica sobre el microservicio de análisis QA",
         tags=["Información"])
async def root():
    """Información del servicio"""
    return {
        "message": "Microservicio de Análisis QA",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificación de salud del servicio"""
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

# Endpoint de análisis (versión mock)
@app.post("/analyze", 
          response_model=AnalysisResponse,
          summary="Analizar contenido y generar casos de prueba",
          description="Analiza cualquier tipo de contenido (caso de prueba, requerimiento, historia de usuario) y genera casos de prueba usando IA",
          tags=["Análisis"])
async def analyze_content(request: AnalysisRequest):
    """Análisis de contenido (versión mock)"""
    start_time = datetime.utcnow()
    analysis_id = f"analysis_{request.content_id}_{int(start_time.timestamp())}"
    
    # Generar casos de prueba mock
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

# Endpoint de generación avanzada (versión mock)
@app.post("/generate-advanced-tests", 
          response_model=AdvancedTestGenerationResponse,
          summary="Generar casos de prueba con técnicas avanzadas",
          description="Genera casos de prueba aplicando técnicas de diseño avanzadas de testing",
          tags=["Generación Avanzada"])
async def generate_advanced_test_cases(request: AdvancedTestGenerationRequest):
    """Generación de casos avanzados (versión mock)"""
    start_time = datetime.utcnow()
    generation_id = f"advanced_{request.aplicacion}_{int(start_time.timestamp())}"
    
    # Generar casos de prueba mock
    test_cases = []
    for i in range(1, 4):  # Generar 3 casos de prueba
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
    
    try:
        port = int(os.getenv("PORT", 8000))
        log_level = os.getenv("LOG_LEVEL", "info").lower()
        is_production = os.getenv("RAILWAY_ENVIRONMENT") == "production"
        
        print(f"Starting Microservicio de Análisis QA - Port: {port}, Log Level: {log_level}, Production: {is_production}")
        
        uvicorn.run(
            "main_minimal:app",
            host="0.0.0.0",
            port=port,
            reload=not is_production,
            log_level=log_level,
            access_log=True
        )
    except Exception as e:
        print(f"Failed to start server: {e}")
        raise
