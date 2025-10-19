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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
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

# Inicializar componentes
tracker_client = TrackerClient()
llm_wrapper = LLMWrapper()
prompt_templates = PromptTemplates()
sanitizer = PIISanitizer()

# Endpoint raíz que redirige a la documentación
@app.get("/", 
         summary="Redirigir a la documentación",
         description="Redirige a la documentación de Swagger de la API",
         tags=["Información"])
async def root():
    """Redirige a la documentación de Swagger"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

# Modelos Pydantic
class AnalysisRequest(BaseModel):
    """Solicitud unificada de análisis de contenido para generar casos de prueba"""
    content_id: str = Field(
        ..., 
        description="ID único del contenido a analizar",
        example="TC-001",
        min_length=1,
        max_length=50
    )
    content: str = Field(
        ..., 
        description="Contenido a analizar (caso de prueba, requerimiento, historia de usuario)",
        example="Verificar que el usuario pueda iniciar sesión con credenciales válidas",
        min_length=10,
        max_length=10000
    )
    content_type: str = Field(
        "test_case",
        description="Tipo de contenido a analizar",
        example="test_case",
        pattern="^(test_case|requirement|user_story)$"
    )
    analysis_level: Optional[str] = Field(
        "medium",
        description="Nivel de análisis y cobertura",
        example="high",
        pattern="^(low|medium|high|comprehensive)$"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "content_id": "TC-001",
                "content": "Verificar que el usuario pueda iniciar sesión con credenciales válidas. Pasos: 1) Abrir la página de login, 2) Ingresar usuario válido, 3) Ingresar contraseña válida, 4) Hacer clic en 'Iniciar Sesión'. Resultado esperado: Usuario logueado exitosamente y redirigido al dashboard.",
                "content_type": "test_case",
                "analysis_level": "high"
            }
        }

class Suggestion(BaseModel):
    """Sugerencia de mejora para un caso de prueba"""
    type: str = Field(..., description="Tipo de sugerencia", example="clarity")
    title: str = Field(..., description="Título de la sugerencia", example="Definir datos de prueba específicos")
    description: str = Field(..., description="Descripción detallada", example="El caso de prueba debe incluir datos específicos de usuario y contraseña")
    priority: str = Field(..., description="Prioridad de la sugerencia", example="high")
    category: str = Field(..., description="Categoría de la mejora", example="improvement")

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

class AnalysisResponse(BaseModel):
    """Respuesta unificada del análisis de contenido"""
    content_id: str = Field(..., description="ID del contenido analizado", example="TC-001")
    analysis_id: str = Field(..., description="ID único del análisis", example="analysis_TC001_1760825804")
    status: str = Field(..., description="Estado del análisis", example="completed")
    test_cases: List[TestCase] = Field(default_factory=list, description="Lista de casos de prueba generados")
    suggestions: List[Suggestion] = Field(default_factory=list, description="Lista de sugerencias de mejora")
    coverage_analysis: Dict[str, Any] = Field(default_factory=dict, description="Análisis de cobertura de pruebas")
    confidence_score: float = Field(..., description="Puntuación de confianza del análisis (0-1)", example=0.85)
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos", example=8.81)
    created_at: datetime = Field(..., description="Timestamp de creación del análisis")
    
    class Config:
        schema_extra = {
            "example": {
                "content_id": "TC-001",
                "analysis_id": "analysis_TC001_1760825804",
                "status": "completed",
                "test_cases": [
                    {
                        "test_case_id": "CP-001-SISTEMA_AUTH-AUTENTICACION-DATO-CONDICION-RESULTADO",
                        "title": "CP - 001 - SISTEMA_AUTH - AUTENTICACION - DATO - CONDICION - RESULTADO",
                        "description": "Caso de prueba para verificar autenticación exitosa",
                        "test_type": "functional",
                        "priority": "high",
                        "steps": ["Navegar a login", "Ingresar credenciales", "Hacer clic en login"],
                        "expected_result": "Resultado Esperado: Usuario autenticado exitosamente y redirigido al dashboard",
                        "preconditions": ["Precondicion: Ingresar al publicado https://auth.sistema.com/login", "Precondicion: Usuario existe en la base de datos", "Precondicion: Sistema de autenticación activo"],
                        "test_data": {"email": "test@example.com", "password": "Test123!"},
                        "automation_potential": "high",
                        "estimated_duration": "5-10 minutes"
                    }
                ],
                "suggestions": [
                    {
                        "type": "clarity",
                        "title": "Definir datos de prueba específicos",
                        "description": "El caso de prueba debe incluir datos específicos de usuario y contraseña",
                        "priority": "high",
                        "category": "improvement"
                    }
                ],
                "coverage_analysis": {
                    "functional_coverage": "90%",
                    "edge_case_coverage": "75%",
                    "integration_coverage": "80%"
                },
                "confidence_score": 0.85,
                "processing_time": 8.81,
                "created_at": "2025-10-18T19:16:44.520862"
            }
        }

class JiraAnalysisRequest(BaseModel):
    """Solicitud simplificada de análisis de work item de Jira"""
    work_item_id: str = Field(
        ..., 
        description="ID del work item en Jira (ej: PROJ-123)",
        example="AUTH-123",
        min_length=1,
        max_length=50
    )
    analysis_level: Optional[str] = Field(
        "medium",
        description="Nivel de análisis y cobertura",
        example="high",
        pattern="^(low|medium|high|comprehensive)$"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "work_item_id": "AUTH-123",
                "analysis_level": "high"
            }
        }

class JiraAnalysisResponse(BaseModel):
    """Respuesta del análisis de work item de Jira"""
    work_item_id: str = Field(..., description="ID del work item analizado", example="AUTH-123")
    jira_data: Dict[str, Any] = Field(..., description="Datos obtenidos de Jira")
    analysis_id: str = Field(..., description="ID único del análisis", example="jira_analysis_AUTH123_1760825804")
    status: str = Field(..., description="Estado del análisis", example="completed")
    test_cases: List[TestCase] = Field(..., description="Lista de casos de prueba generados")
    coverage_analysis: Dict[str, Any] = Field(..., description="Análisis de cobertura de pruebas")
    confidence_score: float = Field(..., description="Puntuación de confianza del análisis (0-1)", example=0.85)
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos", example=15.5)
    created_at: datetime = Field(..., description="Timestamp de creación del análisis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "work_item_id": "AUTH-123",
                "jira_data": {
                    "summary": "Implementar autenticación de usuarios",
                    "description": "El sistema debe permitir a los usuarios autenticarse...",
                    "issue_type": "Story",
                    "priority": "High",
                    "status": "In Progress"
                },
                "analysis_id": "jira_analysis_AUTH123_1760825804",
                "status": "completed",
                "test_cases": [
                    {
                        "test_case_id": "CP-001-SISTEMA_AUTH-AUTENTICACION-DATO-CONDICION-RESULTADO",
                        "title": "CP - 001 - SISTEMA_AUTH - AUTENTICACION - DATO - CONDICION - RESULTADO",
                        "description": "Caso de prueba para verificar autenticación exitosa",
                        "test_type": "functional",
                        "priority": "high",
                        "steps": ["Navegar a login", "Ingresar credenciales", "Hacer clic en login"],
                        "expected_result": "Resultado Esperado: Usuario autenticado exitosamente y redirigido al dashboard",
                        "preconditions": ["Precondicion: Ingresar al publicado https://auth.sistema.com/login", "Precondicion: Usuario existe en la base de datos", "Precondicion: Sistema de autenticación activo"],
                        "test_data": {"email": "test@example.com", "password": "Test123!"},
                        "automation_potential": "high",
                        "estimated_duration": "5-10 minutes"
                    }
                ],
                "coverage_analysis": {
                    "functional_coverage": "90%",
                    "edge_case_coverage": "75%",
                    "integration_coverage": "80%"
                },
                "confidence_score": 0.85,
                "processing_time": 15.5,
                "created_at": "2025-10-18T19:16:44.520862"
            }
        }

class AdvancedTestGenerationRequest(BaseModel):
    """Solicitud simplificada de generación de casos de prueba avanzados"""
    requerimiento: str = Field(
        ..., 
        description="Requerimiento completo a analizar y generar casos de prueba",
        example="El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado.",
        min_length=50,
        max_length=5000
    )
    aplicacion: str = Field(
        ..., 
        description="Nombre de la aplicación o sistema",
        example="SISTEMA_AUTH",
        min_length=1,
        max_length=50
    )
    modulo: str = Field(
        ..., 
        description="Módulo específico del sistema que se va a probar",
        example="AUTENTICACION",
        min_length=1,
        max_length=50
    )
    servicio_publicado: Optional[str] = Field(
        None,
        description="URL o nombre del servicio publicado (si existe)",
        example="https://auth.sistema.com/login",
        max_length=200
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "requerimiento": "El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado.",
                "aplicacion": "SISTEMA_AUTH",
                "modulo": "AUTENTICACION",
                "servicio_publicado": "https://auth.sistema.com/login"
            }
        }

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
    
    class Config:
        json_schema_extra = {
            "example": {
                "aplicacion": "SISTEMA_AUTH",
                "generation_id": "advanced_SISTEMA_AUTH_1760825804",
                "status": "completed",
                "test_cases": [
                    {
                        "test_case_id": "CP-001-SISTEMA_AUTH-AUTENTICACION-DATO-CONDICION-RESULTADO",
                        "title": "CP - 001 - SISTEMA_AUTH - AUTENTICACION - DATO - CONDICION - RESULTADO",
                        "description": "Caso de prueba para verificar autenticación exitosa",
                        "test_type": "functional",
                        "priority": "high",
                        "steps": ["Navegar a login", "Ingresar credenciales", "Hacer clic en login"],
                        "expected_result": "Resultado Esperado: Usuario autenticado exitosamente y redirigido al dashboard",
                        "preconditions": ["Precondicion: Ingresar al publicado https://auth.sistema.com/login", "Precondicion: Usuario existe en la base de datos", "Precondicion: Sistema de autenticación activo"],
                        "test_data": {"email": "test@example.com", "password": "Test123!"},
                        "automation_potential": "high",
                        "estimated_duration": "5-10 minutes"
                    }
                ],
                "coverage_analysis": {
                    "functional_coverage": "90%",
                    "edge_case_coverage": "75%",
                    "integration_coverage": "80%"
                },
                "confidence_score": 0.85,
                "processing_time": 25.3,
                "created_at": "2025-10-18T19:16:44.520862"
            }
        }

class HealthResponse(BaseModel):
    """Respuesta de salud del servicio"""
    status: str
    timestamp: datetime
    version: str
    components: Dict[str, str]


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

@app.post("/analyze", 
          response_model=AnalysisResponse,
          summary="Analizar contenido y generar casos de prueba",
          description="Analiza cualquier tipo de contenido (caso de prueba, requerimiento, historia de usuario) y genera casos de prueba usando IA",
          tags=["Análisis"],
          responses={
              200: {
                  "description": "Análisis completado exitosamente",
                  "model": AnalysisResponse
              },
              422: {
                  "description": "Datos de entrada inválidos",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Error de validación en los datos de entrada"}
                      }
                  }
              },
              500: {
                  "description": "Error interno del servidor",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Error interno del servidor"}
                      }
                  }
              }
          })
async def analyze_content(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    ## Analizar Contenido y Generar Casos de Prueba
    
    Analiza cualquier tipo de contenido (caso de prueba, requerimiento, historia de usuario) y genera casos de prueba estructurados usando IA generativa.
    
    ### Proceso:
    1. **Sanitización**: Se elimina información sensible del contenido
    2. **Análisis IA**: Se procesa con Google Gemini usando prompts especializados según el tipo de contenido
    3. **Generación de Casos**: Se crean casos de prueba estructurados
    4. **Análisis de Cobertura**: Se evalúa la cobertura de pruebas generada
    5. **Observabilidad**: Se registra en Langfuse para monitoreo
    
    ### Tipos de Contenido Soportados:
    - **test_case**: Análisis de casos de prueba existentes con sugerencias de mejora
    - **requirement**: Análisis de requerimientos para generar casos de prueba
    - **user_story**: Análisis de historias de usuario para generar casos de prueba
    
    ### Niveles de Análisis:
    - **low**: Análisis básico con casos esenciales
    - **medium**: Análisis estándar con casos edge
    - **high**: Análisis completo con casos complejos
    - **comprehensive**: Análisis exhaustivo con todos los escenarios
    
    ### Respuesta:
    - **test_cases**: Lista de casos de prueba generados
    - **suggestions**: Lista de sugerencias de mejora (para casos de prueba existentes)
    - **coverage_analysis**: Análisis de cobertura por tipo
    - **confidence_score**: Puntuación de confianza (0-1)
    - **processing_time**: Tiempo de procesamiento en segundos
    """
    start_time = datetime.utcnow()
    analysis_id = f"analysis_{request.content_id}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting content analysis",
            content_id=request.content_id,
            content_type=request.content_type,
            analysis_level=request.analysis_level,
            analysis_id=analysis_id
        )
        
        # Sanitizar contenido sensible
        sanitized_content = sanitizer.sanitize(request.content)
        
        # Obtener prompt según el tipo de contenido
        if request.content_type == "test_case":
            prompt = prompt_templates.get_analysis_prompt(
                test_case_content=sanitized_content,
                project_key="",  # Ya no requerido
                priority="",     # Ya no requerido
                labels=[]        # Ya no requerido
            )
        elif request.content_type == "requirement":
            prompt = prompt_templates.get_requirements_analysis_prompt(
                requirement_content=sanitized_content,
                project_key="",  # Ya no requerido
                priority="",     # Ya no requerido
                test_types=["functional", "integration"],  # Valores por defecto
                coverage_level=request.analysis_level
            )
        else:  # user_story
            prompt = prompt_templates.get_requirements_analysis_prompt(
                requirement_content=sanitized_content,
                project_key="",  # Ya no requerido
                priority="",     # Ya no requerido
                test_types=["functional", "integration"],  # Valores por defecto
                coverage_level=request.analysis_level
            )
        
        # Ejecutar análisis con LLM
        if request.content_type == "test_case":
            analysis_result = await llm_wrapper.analyze_test_case(
                prompt=prompt,
                test_case_id=request.content_id,
                analysis_id=analysis_id
            )
        else:
            analysis_result = await llm_wrapper.analyze_requirements(
                prompt=prompt,
                requirement_id=request.content_id,
                analysis_id=analysis_id
            )
        
        # Procesar casos de prueba generados
        test_cases = []
        if analysis_result.get("test_cases"):
            for tc_data in analysis_result["test_cases"]:
                test_case = TestCase(
                    test_case_id=tc_data.get("test_case_id", f"TC-{request.content_id}-001"),
                    title=tc_data.get("title", ""),
                    description=tc_data.get("description", ""),
                    test_type=tc_data.get("test_type", "functional"),
                    priority=tc_data.get("priority", "medium"),
                    steps=tc_data.get("steps", []),
                    expected_result=tc_data.get("expected_result", ""),
                    preconditions=tc_data.get("preconditions", []),
                    test_data=tc_data.get("test_data", {}),
                    automation_potential=tc_data.get("automation_potential", "medium"),
                    estimated_duration=tc_data.get("estimated_duration", "5-10 minutes")
                )
                test_cases.append(test_case)
        
        # Procesar sugerencias (solo para casos de prueba existentes)
        suggestions = []
        if request.content_type == "test_case" and analysis_result.get("suggestions"):
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
        response = AnalysisResponse(
            content_id=request.content_id,
            analysis_id=analysis_id,
            status="completed",
            test_cases=test_cases,
            suggestions=suggestions,
            coverage_analysis=analysis_result.get("coverage_analysis", {}),
            confidence_score=analysis_result.get("confidence_score", 0.8),
            processing_time=processing_time,
            created_at=start_time
        )
        
        # Registrar en background task para tracking
        background_tasks.add_task(
            log_analysis_completion,
            analysis_id,
            request.content_id,
            response
        )
        
        logger.info(
            "Content analysis completed",
            content_id=request.content_id,
            content_type=request.content_type,
            analysis_id=analysis_id,
            test_cases_count=len(test_cases),
            suggestions_count=len(suggestions),
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Content analysis failed",
            content_id=request.content_id,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing content: {str(e)}"
        )

@app.post("/analyze-jira", 
          response_model=JiraAnalysisResponse,
          summary="Analizar work item de Jira y generar casos de prueba",
          description="Obtiene un work item de Jira y genera casos de prueba estructurados usando IA",
          tags=["Integración Jira"],
          responses={
              200: {
                  "description": "Análisis de work item completado exitosamente",
                  "model": JiraAnalysisResponse
              },
              404: {
                  "description": "Work item no encontrado en Jira",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Work item no encontrado en Jira"}
                      }
                  }
              },
              422: {
                  "description": "Datos de entrada inválidos",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Error de validación en los datos de entrada"}
                      }
                  }
              },
              500: {
                  "description": "Error interno del servidor",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Error interno del servidor"}
                      }
                  }
              }
          })
async def analyze_jira_workitem(
    request: JiraAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    ## Analizar Work Item de Jira y Generar Casos de Prueba
    
    Obtiene un work item específico de Jira y genera casos de prueba estructurados basados en su contenido.
    
    ### Proceso:
    1. **Obtención de Jira**: Se recupera el work item desde Jira API
    2. **Extracción de Datos**: Se extrae información relevante (summary, description, acceptance criteria)
    3. **Análisis IA**: Se procesa con Google Gemini usando prompts especializados
    4. **Generación de Casos**: Se crean casos de prueba estructurados
    5. **Análisis de Cobertura**: Se evalúa la cobertura de pruebas generada
    
    ### Datos Obtenidos de Jira:
    - **Summary**: Título del work item
    - **Description**: Descripción detallada
    - **Acceptance Criteria**: Criterios de aceptación (si están disponibles)
    - **Issue Type**: Tipo de issue (Story, Task, Bug, etc.)
    - **Priority**: Prioridad del work item
    - **Status**: Estado actual
    
    ### Niveles de Análisis:
    - **low**: Análisis básico con casos esenciales
    - **medium**: Análisis estándar con casos edge
    - **high**: Análisis completo con casos complejos
    - **comprehensive**: Análisis exhaustivo con todos los escenarios
    
    ### Respuesta:
    - **jira_data**: Datos completos obtenidos de Jira
    - **test_cases**: Lista de casos de prueba generados
    - **coverage_analysis**: Análisis de cobertura por tipo
    - **confidence_score**: Puntuación de confianza (0-1)
    - **processing_time**: Tiempo de procesamiento en segundos
    """
    start_time = datetime.utcnow()
    analysis_id = f"jira_analysis_{request.work_item_id.replace('-', '')}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting Jira work item analysis",
            work_item_id=request.work_item_id,
            analysis_level=request.analysis_level,
            analysis_id=analysis_id
        )
        
        # Obtener datos del work item desde Jira (sin project_key requerido)
        jira_data = await tracker_client.get_work_item_details(
            work_item_id=request.work_item_id,
            project_key=""  # Se detecta automáticamente del work_item_id
        )
        
        if not jira_data:
            raise HTTPException(
                status_code=404,
                detail=f"Work item {request.work_item_id} not found"
            )
        
        # Construir contenido para análisis
        requirement_content = f"""
        TÍTULO: {jira_data.get('summary', '')}
        
        DESCRIPCIÓN:
        {jira_data.get('description', '')}
        
        TIPO DE ISSUE: {jira_data.get('issue_type', '')}
        PRIORIDAD: {jira_data.get('priority', '')}
        ESTADO: {jira_data.get('status', '')}
        """
        
        # Agregar criterios de aceptación si están disponibles
        if jira_data.get('acceptance_criteria'):
            requirement_content += f"""
            
            CRITERIOS DE ACEPTACIÓN:
            {jira_data.get('acceptance_criteria', '')}
            """
        
        # Sanitizar contenido sensible
        sanitized_content = sanitizer.sanitize(requirement_content)
        
        # Generar prompt para análisis de work item
        prompt = prompt_templates.get_jira_workitem_analysis_prompt(
            work_item_data=jira_data,
            requirement_content=sanitized_content,
            project_key="",  # Ya no requerido
            test_types=["functional", "integration"],  # Valores por defecto
            coverage_level=request.analysis_level
        )
        
        # Ejecutar análisis con LLM
        analysis_result = await llm_wrapper.analyze_jira_workitem(
            prompt=prompt,
            work_item_id=request.work_item_id,
            analysis_id=analysis_id
        )
        
        # Procesar casos de prueba generados
        test_cases = []
        if analysis_result.get("test_cases"):
            for tc_data in analysis_result["test_cases"]:
                test_case = TestCase(
                    test_case_id=tc_data.get("test_case_id", f"TC-{request.work_item_id}-001"),
                    title=tc_data.get("title", ""),
                    description=tc_data.get("description", ""),
                    test_type=tc_data.get("test_type", "functional"),
                    priority=tc_data.get("priority", "medium"),
                    steps=tc_data.get("steps", []),
                    expected_result=tc_data.get("expected_result", ""),
                    preconditions=tc_data.get("preconditions", []),
                    test_data=tc_data.get("test_data", {}),
                    automation_potential=tc_data.get("automation_potential", "medium"),
                    estimated_duration=tc_data.get("estimated_duration", "5-10 minutes")
                )
                test_cases.append(test_case)
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = JiraAnalysisResponse(
            work_item_id=request.work_item_id,
            jira_data=jira_data,
            analysis_id=analysis_id,
            status="completed",
            test_cases=test_cases,
            coverage_analysis=analysis_result.get("coverage_analysis", {}),
            confidence_score=analysis_result.get("confidence_score", 0.8),
            processing_time=processing_time,
            created_at=start_time
        )
        
        # Registrar en background task para tracking
        background_tasks.add_task(
            log_jira_workitem_analysis_completion,
            analysis_id,
            request.work_item_id,
            response
        )
        
        logger.info(
            "Jira work item analysis completed",
            work_item_id=request.work_item_id,
            analysis_id=analysis_id,
            test_cases_count=len(test_cases),
            processing_time=processing_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Jira work item analysis failed",
            work_item_id=request.work_item_id,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing Jira work item: {str(e)}"
        )

@app.post("/generate-advanced-tests", 
          response_model=AdvancedTestGenerationResponse,
          summary="Generar casos de prueba con técnicas avanzadas",
          description="Genera casos de prueba aplicando técnicas de diseño avanzadas de testing",
          tags=["Generación Avanzada"],
          responses={
              200: {
                  "description": "Generación de casos avanzados completada exitosamente",
                  "model": AdvancedTestGenerationResponse
              },
              422: {
                  "description": "Datos de entrada inválidos",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Error de validación en los datos de entrada"}
                      }
                  }
              },
              500: {
                  "description": "Error interno del servidor",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Error interno del servidor"}
                      }
                  }
              }
          })
async def generate_advanced_test_cases(
    request: AdvancedTestGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    ## Generar Casos de Prueba con Técnicas Avanzadas
    
    Genera casos de prueba aplicando técnicas de diseño avanzadas de testing con observabilidad completa.
    
    ### Proceso:
    1. **Análisis del Requerimiento**: Se procesa el requerimiento completo con IA
    2. **Aplicación de Técnicas**: Se aplican técnicas avanzadas de testing automáticamente
    3. **Generación Estructurada**: Se crean casos de prueba con estructura estandarizada
    4. **Análisis de Cobertura**: Se evalúa la cobertura de pruebas generada
    5. **Observabilidad**: Se registra en Langfuse para monitoreo y análisis
    
    ### Técnicas Aplicadas Automáticamente:
    - **Partición de Equivalencia**: Clases válidas e inválidas
    - **Valores Límite**: Casos boundary y edge cases
    - **Casos de Uso**: Flujos principales y alternos
    - **Casos de Error**: Validaciones y manejo de errores
    - **Casos de Integración**: Flujos end-to-end
    - **Casos de Seguridad**: Autenticación y autorización
    
    ### Parámetros de Entrada:
    - **requerimiento**: Requerimiento completo a analizar
    - **aplicacion**: Nombre de la aplicación o sistema
    - **modulo**: Módulo específico del sistema que se va a probar
    - **servicio_publicado**: URL o nombre del servicio publicado (opcional)
    
    ### Formato de Salida:
    - **test_cases**: Lista de casos de prueba con estructura estandarizada
    - **coverage_analysis**: Análisis de cobertura por tipo de prueba
    - **confidence_score**: Puntuación de confianza (0-1)
    - **processing_time**: Tiempo de procesamiento en segundos
    
    ### Estructura de Casos de Prueba:
    - **ID**: CP-001-APLICACION-MODULO-DATO-CONDICION-RESULTADO
    - **Título**: CP - 001 - APLICACION - MODULO - DATO - CONDICION - RESULTADO
    - **Precondiciones**: Incluye "Ingresar al publicado XXXX" si se proporciona servicio_publicado
    - **Resultado Esperado**: Formato "Resultado Esperado: [descripción específica]"
    """
    start_time = datetime.utcnow()
    generation_id = f"advanced_{request.aplicacion}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting advanced test case generation",
            aplicacion=request.aplicacion,
            generation_id=generation_id
        )
        
        # Generar prompt para análisis de requerimientos
        prompt = prompt_templates.get_requirements_analysis_prompt(
            requirement_content=request.requerimiento,
            project_key=request.aplicacion,
            priority="High",
            test_types=["functional", "integration", "security"],
            coverage_level="high"
        )
        
        # Ejecutar análisis con LLM
        analysis_result = await llm_wrapper.analyze_requirements(
            prompt=prompt,
            requirement_id=f"REQ-{request.aplicacion}",
            analysis_id=generation_id
        )
        
        # Procesar casos de prueba generados
        test_cases = []
        if analysis_result.get("test_cases"):
            for i, tc_data in enumerate(analysis_result["test_cases"], 1):
                # Generar ID y título con el módulo específico
                test_case_id = f"CP-{i:03d}-{request.aplicacion}-{request.modulo}-DATO-CONDICION-RESULTADO"
                title = f"CP - {i:03d} - {request.aplicacion} - {request.modulo} - DATO - CONDICION - RESULTADO"
                
                # Agregar precondición del servicio publicado si existe
                preconditions = tc_data.get("preconditions", ["Precondicion: [Descripción específica]"])
                if request.servicio_publicado:
                    preconditions.insert(0, f"Precondicion: Ingresar al publicado {request.servicio_publicado}")
                
                test_case = TestCase(
                    test_case_id=test_case_id,
                    title=title,
                    description=tc_data.get("description", ""),
                    test_type=tc_data.get("test_type", "functional"),
                    priority=tc_data.get("priority", "high"),
                    steps=tc_data.get("steps", []),
                    expected_result=tc_data.get("expected_result", "Resultado Esperado: [Descripción específica]"),
                    preconditions=preconditions,
                    test_data=tc_data.get("test_data", {}),
                    automation_potential=tc_data.get("automation_potential", "high"),
                    estimated_duration=tc_data.get("estimated_duration", "5-10 minutes")
                )
                test_cases.append(test_case)
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = AdvancedTestGenerationResponse(
            aplicacion=request.aplicacion,
            generation_id=generation_id,
            status="completed",
            test_cases=test_cases,
            coverage_analysis=analysis_result.get("coverage_analysis", {}),
            confidence_score=analysis_result.get("confidence_score", 0.8),
            processing_time=processing_time,
            created_at=start_time
        )
        
        # Registrar en background task para tracking
        background_tasks.add_task(
            log_advanced_generation_completion,
            generation_id,
            request.aplicacion,
            response
        )
        
        logger.info(
            "Advanced test case generation completed",
            aplicacion=request.aplicacion,
            generation_id=generation_id,
            test_cases_count=len(test_cases),
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Advanced test case generation failed",
            aplicacion=request.aplicacion,
            generation_id=generation_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error generating advanced test cases: {str(e)}"
        )


async def log_analysis_completion(
    analysis_id: str,
    content_id: str,
    response: AnalysisResponse
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
            content_id=content_id,
            test_cases_count=len(response.test_cases),
            suggestions_count=len(response.suggestions)
        )
    except Exception as e:
        logger.error(
            "Failed to log analysis completion",
            analysis_id=analysis_id,
            error=str(e)
        )

async def log_jira_workitem_analysis_completion(
    analysis_id: str,
    work_item_id: str,
    response: JiraAnalysisResponse
):
    """Background task para registrar la finalización del análisis de work item de Jira"""
    try:
        # Aquí podrías implementar lógica adicional como:
        # - Guardar en base de datos
        # - Enviar notificaciones
        # - Actualizar métricas
        # - Crear casos de prueba en Jira
        logger.info(
            "Jira work item analysis completion logged",
            analysis_id=analysis_id,
            work_item_id=work_item_id,
            test_cases_count=len(response.test_cases)
        )
    except Exception as e:
        logger.error(
            "Failed to log Jira work item analysis completion",
            analysis_id=analysis_id,
            error=str(e)
        )

async def log_istqb_generation_completion(
    generation_id: str,
    programa: str,
    response: AdvancedTestGenerationResponse
):
    """Background task para registrar la finalización de la generación ISTQB"""
    try:
        # Aquí podrías implementar lógica adicional como:
        # - Guardar en base de datos
        # - Enviar notificaciones
        # - Actualizar métricas
        # - Crear casos de prueba en Jira
        # - Generar reportes de cobertura
        logger.info(
            "Advanced test generation completion logged",
            generation_id=generation_id,
            aplicacion=programa,
            test_cases_count=len(response.test_cases),
            confidence_score=response.confidence_score,
            processing_time=response.processing_time
        )
    except Exception as e:
        logger.error(
            "Failed to log advanced generation completion",
            generation_id=generation_id,
            error=str(e)
        )

async def log_advanced_generation_completion(
    generation_id: str,
    aplicacion: str,
    response: AdvancedTestGenerationResponse
):
    """Background task para registrar la finalización de la generación avanzada"""
    try:
        # Aquí podrías implementar lógica adicional como:
        # - Guardar en base de datos
        # - Enviar notificaciones
        # - Actualizar métricas
        # - Crear casos de prueba en Jira
        # - Generar reportes de cobertura
        logger.info(
            "Advanced test generation completion logged",
            generation_id=generation_id,
            aplicacion=aplicacion,
            test_cases_count=len(response.test_cases),
            confidence_score=response.confidence_score,
            processing_time=response.processing_time
        )
    except Exception as e:
        logger.error(
            "Failed to log advanced generation completion",
            generation_id=generation_id,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    is_production = os.getenv("RAILWAY_ENVIRONMENT") == "production"
    
    logger.info("Starting Microservicio de Análisis QA", port=port, log_level=log_level, is_production=is_production)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,
        log_level=log_level
    )
