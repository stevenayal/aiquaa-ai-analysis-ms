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
    description="""
    ## API de Análisis Automatizado de Casos de Prueba con Técnicas ISTQB
    
    Esta API proporciona análisis inteligente de casos de prueba utilizando IA generativa y técnicas de diseño ISTQB Foundation Level.
    
    ### Características:
    - 🤖 Análisis automatizado con Google Gemini
    - 📊 Observabilidad completa con Langfuse
    - 🔗 Integración con Jira
    - 📝 Sugerencias de mejora estructuradas
    - 🚀 Procesamiento en lote
    - 🎯 **NUEVO**: Generación de casos con técnicas ISTQB avanzadas
    - 🔬 **NUEVO**: Aplicación de 9 técnicas de diseño de pruebas
    - 📋 **NUEVO**: Formato estructurado con CSV, fichas y artefactos técnicos
    
    ### Técnicas ISTQB Soportadas:
    - **Equivalencia**: Partición de clases de equivalencia
    - **Valores Límite**: Análisis de valores límite
    - **Tabla de Decisión**: Matrices de condiciones y acciones
    - **Transición de Estados**: Estados y transiciones del sistema
    - **Árbol de Clasificación**: Clases y restricciones
    - **Pairwise**: Combinaciones mínimas de pares
    - **Casos de Uso**: Flujos principales y alternos
    - **Error Guessing**: Hipótesis de fallos
    - **Checklist**: Verificación genérica de calidad
    
    ### Autenticación:
    No se requiere autenticación para las pruebas locales.
    
    ### Uso:
    1. **Análisis básico**: Envía un caso de prueba al endpoint `/analyze`
    2. **Generación ISTQB**: Usa `/generate-istqb-tests` para casos avanzados
    3. **Análisis de requerimientos**: Usa `/analyze-requirements` para generar casos
    4. **Integración Jira**: Usa `/analyze-jira-workitem` para work items
    5. **Monitoreo**: Verifica el estado con `/health`
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
            "url": "http://localhost:8000",
            "description": "Servidor de desarrollo local"
        }
    ]
)

# Inicializar componentes
tracker_client = TrackerClient()
llm_wrapper = LLMWrapper()
prompt_templates = PromptTemplates()
sanitizer = PIISanitizer()

# Modelos Pydantic
class TestCaseAnalysisRequest(BaseModel):
    """Solicitud de análisis de caso de prueba"""
    test_case_id: str = Field(
        ..., 
        description="ID único del caso de prueba",
        example="TC-001",
        min_length=1,
        max_length=50
    )
    test_case_content: str = Field(
        ..., 
        description="Descripción detallada del caso de prueba a analizar",
        example="Verificar que el usuario pueda iniciar sesión con credenciales válidas",
        min_length=10,
        max_length=5000
    )
    project_key: str = Field(
        ..., 
        description="Clave del proyecto en Jira",
        example="TEST",
        min_length=1,
        max_length=20
    )
    priority: Optional[str] = Field(
        "Medium", 
        description="Prioridad del caso de prueba",
        example="High",
        pattern="^(Low|Medium|High|Critical)$"
    )
    labels: Optional[List[str]] = Field(
        default_factory=list, 
        description="Etiquetas para categorizar el caso de prueba",
        example=["login", "authentication", "smoke-test"]
    )
    
    class Config:
        schema_extra = {
            "example": {
                "test_case_id": "TC-001",
                "test_case_content": "Verificar que el usuario pueda iniciar sesión con credenciales válidas. Pasos: 1) Abrir la página de login, 2) Ingresar usuario válido, 3) Ingresar contraseña válida, 4) Hacer clic en 'Iniciar Sesión'. Resultado esperado: Usuario logueado exitosamente y redirigido al dashboard.",
                "project_key": "TEST",
                "priority": "High",
                "labels": ["login", "authentication", "smoke-test"]
            }
        }

class Suggestion(BaseModel):
    """Sugerencia de mejora para un caso de prueba"""
    type: str = Field(..., description="Tipo de sugerencia", example="clarity")
    title: str = Field(..., description="Título de la sugerencia", example="Definir datos de prueba específicos")
    description: str = Field(..., description="Descripción detallada", example="El caso de prueba debe incluir datos específicos de usuario y contraseña")
    priority: str = Field(..., description="Prioridad de la sugerencia", example="high")
    category: str = Field(..., description="Categoría de la mejora", example="improvement")

class TestCaseAnalysisResponse(BaseModel):
    """Respuesta del análisis de caso de prueba"""
    test_case_id: str = Field(..., description="ID del caso de prueba analizado", example="TC-001")
    analysis_id: str = Field(..., description="ID único del análisis", example="analysis_TC001_1760825804")
    status: str = Field(..., description="Estado del análisis", example="completed")
    suggestions: List[Suggestion] = Field(..., description="Lista de sugerencias de mejora")
    confidence_score: float = Field(..., description="Puntuación de confianza del análisis (0-1)", example=0.85)
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos", example=8.81)
    created_at: datetime = Field(..., description="Timestamp de creación del análisis")
    
    class Config:
        schema_extra = {
            "example": {
                "test_case_id": "TC-001",
                "analysis_id": "analysis_TC001_1760825804",
                "status": "completed",
                "suggestions": [
                    {
                        "type": "clarity",
                        "title": "Definir datos de prueba específicos",
                        "description": "El caso de prueba debe incluir datos específicos de usuario y contraseña",
                        "priority": "high",
                        "category": "improvement"
                    }
                ],
                "confidence_score": 0.85,
                "processing_time": 8.81,
                "created_at": "2025-10-18T19:16:44.520862"
            }
        }

class RequirementsAnalysisRequest(BaseModel):
    """Solicitud de análisis de requerimientos para generar casos de prueba"""
    requirement_id: str = Field(
        ..., 
        description="ID único del requerimiento",
        example="REQ-001",
        min_length=1,
        max_length=50
    )
    requirement_content: str = Field(
        ..., 
        description="Descripción detallada del requerimiento a analizar",
        example="El sistema debe permitir a los usuarios autenticarse usando email y contraseña",
        min_length=10,
        max_length=10000
    )
    project_key: str = Field(
        ..., 
        description="Clave del proyecto en Jira",
        example="AUTH",
        min_length=1,
        max_length=20
    )
    priority: Optional[str] = Field(
        "Medium", 
        description="Prioridad del requerimiento",
        example="High",
        pattern="^(Low|Medium|High|Critical)$"
    )
    test_types: Optional[List[str]] = Field(
        default_factory=lambda: ["functional", "integration"],
        description="Tipos de pruebas a generar",
        example=["functional", "integration", "ui", "api", "security"]
    )
    coverage_level: Optional[str] = Field(
        "medium",
        description="Nivel de cobertura de pruebas",
        example="high",
        pattern="^(low|medium|high|comprehensive)$"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "requirement_id": "REQ-001",
                "requirement_content": "El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado.",
                "project_key": "AUTH",
                "priority": "High",
                "test_types": ["functional", "integration", "security"],
                "coverage_level": "high"
            }
        }

class TestCase(BaseModel):
    """Caso de prueba generado"""
    test_case_id: str = Field(..., description="ID del caso de prueba", example="TC-AUTH-001")
    title: str = Field(..., description="Título del caso de prueba", example="Verificar login con credenciales válidas")
    description: str = Field(..., description="Descripción detallada del caso de prueba")
    test_type: str = Field(..., description="Tipo de prueba", example="functional")
    priority: str = Field(..., description="Prioridad del caso de prueba", example="high")
    steps: List[str] = Field(..., description="Pasos detallados del caso de prueba")
    expected_result: str = Field(..., description="Resultado esperado")
    preconditions: List[str] = Field(default_factory=list, description="Precondiciones necesarias")
    test_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Datos de prueba específicos")
    automation_potential: str = Field(..., description="Potencial de automatización", example="high")
    estimated_duration: str = Field(..., description="Duración estimada", example="5-10 minutes")

class RequirementsAnalysisResponse(BaseModel):
    """Respuesta del análisis de requerimientos"""
    requirement_id: str = Field(..., description="ID del requerimiento analizado", example="REQ-001")
    analysis_id: str = Field(..., description="ID único del análisis", example="req_analysis_REQ001_1760825804")
    status: str = Field(..., description="Estado del análisis", example="completed")
    test_cases: List[TestCase] = Field(..., description="Lista de casos de prueba generados")
    coverage_analysis: Dict[str, Any] = Field(..., description="Análisis de cobertura de pruebas")
    confidence_score: float = Field(..., description="Puntuación de confianza del análisis (0-1)", example=0.85)
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos", example=12.5)
    created_at: datetime = Field(..., description="Timestamp de creación del análisis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "requirement_id": "REQ-001",
                "analysis_id": "req_analysis_REQ001_1760825804",
                "status": "completed",
                "test_cases": [
                    {
                        "test_case_id": "TC-AUTH-001",
                        "title": "Verificar login con credenciales válidas",
                        "description": "Caso de prueba para verificar que un usuario puede autenticarse exitosamente",
                        "test_type": "functional",
                        "priority": "high",
                        "steps": [
                            "Navegar a la página de login",
                            "Ingresar email válido",
                            "Ingresar contraseña válida",
                            "Hacer clic en 'Iniciar Sesión'"
                        ],
                        "expected_result": "Usuario autenticado exitosamente y redirigido al dashboard",
                        "preconditions": ["Usuario existe en la base de datos", "Usuario está activo"],
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
                "processing_time": 12.5,
                "created_at": "2025-10-18T19:16:44.520862"
            }
        }

class JiraWorkItemRequest(BaseModel):
    """Solicitud de análisis de work item de Jira"""
    work_item_id: str = Field(
        ..., 
        description="ID del work item en Jira (ej: PROJ-123)",
        example="AUTH-123",
        min_length=1,
        max_length=50
    )
    project_key: str = Field(
        ..., 
        description="Clave del proyecto en Jira",
        example="AUTH",
        min_length=1,
        max_length=20
    )
    test_types: Optional[List[str]] = Field(
        default_factory=lambda: ["functional", "integration"],
        description="Tipos de pruebas a generar",
        example=["functional", "integration", "ui", "api", "security"]
    )
    coverage_level: Optional[str] = Field(
        "medium",
        description="Nivel de cobertura de pruebas",
        example="high",
        pattern="^(low|medium|high|comprehensive)$"
    )
    include_acceptance_criteria: Optional[bool] = Field(
        True,
        description="Incluir criterios de aceptación en el análisis",
        example=True
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "work_item_id": "AUTH-123",
                "project_key": "AUTH",
                "test_types": ["functional", "integration", "security"],
                "coverage_level": "high",
                "include_acceptance_criteria": True
            }
        }

class JiraWorkItemResponse(BaseModel):
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
                        "test_case_id": "TC-AUTH-001",
                        "title": "Verificar login con credenciales válidas",
                        "description": "Caso de prueba para verificar autenticación exitosa",
                        "test_type": "functional",
                        "priority": "high",
                        "steps": ["Navegar a login", "Ingresar credenciales", "Hacer clic en login"],
                        "expected_result": "Usuario autenticado exitosamente",
                        "preconditions": ["Usuario existe en BD"],
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

class ISTQBTestGenerationRequest(BaseModel):
    """Solicitud de generación de casos de prueba con técnicas ISTQB"""
    programa: str = Field(
        ..., 
        description="Nombre del sistema/programa",
        example="SISTEMA_AUTH",
        min_length=1,
        max_length=50
    )
    dominio: str = Field(
        ..., 
        description="Breve descripción del requerimiento",
        example="Autenticación de usuarios con validación de credenciales",
        min_length=10,
        max_length=200
    )
    modulos: List[str] = Field(
        ..., 
        description="Lista de módulos del sistema",
        example=["AUTORIZACION", "VALIDACION", "AUDITORIA"],
        min_items=1,
        max_items=10
    )
    factores: Dict[str, List[str]] = Field(
        ..., 
        description="Factores de prueba con sus valores posibles",
        example={
            "TIPO_USUARIO": ["ADMIN", "USER", "GUEST"],
            "ESTADO_CREDENCIAL": ["VALIDA", "INVALIDA", "EXPIRADA"],
            "INTENTOS": ["OK", "ERROR_TIPO_1", "TIMEOUT"]
        }
    )
    limites: Dict[str, Any] = Field(
        ..., 
        description="Límites del sistema",
        example={
            "CAMPO_USUARIO_len": {"min": 1, "max": 64},
            "REINTENTOS": 3,
            "TIMEOUT_MS": 5000
        }
    )
    reglas: List[str] = Field(
        ..., 
        description="Reglas de negocio",
        example=[
            "R1: si TIPO_USUARIO=ADMIN y ESTADO_CREDENCIAL=VALIDA -> ACCESO_TOTAL",
            "R2: si INTENTOS=TIMEOUT -> reintentar 1 vez y marcar pendiente",
            "R3: si REINTENTOS supera límite -> bloquear y auditar"
        ],
        min_items=1
    )
    tecnicas: Dict[str, bool] = Field(
        ..., 
        description="Técnicas ISTQB a aplicar",
        example={
            "equivalencia": True,
            "valores_limite": True,
            "tabla_decision": True,
            "transicion_estados": True,
            "arbol_clasificacion": True,
            "pairwise": True,
            "casos_uso": True,
            "error_guessing": True,
            "checklist": True
        }
    )
    priorizacion: Optional[str] = Field(
        "Riesgo", 
        description="Criterio de priorización",
        example="Riesgo",
        pattern="^(Riesgo|Impacto|Uso)$"
    )
    cantidad_max: Optional[int] = Field(
        150, 
        description="Cantidad máxima de casos de prueba a generar",
        example=150,
        ge=10,
        le=500
    )
    salida_plan_ejecucion: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"incluir": True, "formato": "cursor_playwright_mcp"},
        description="Configuración del plan de ejecución"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "programa": "SISTEMA_AUTH",
                "dominio": "Autenticación de usuarios con validación de credenciales",
                "modulos": ["AUTORIZACION", "VALIDACION", "AUDITORIA"],
                "factores": {
                    "TIPO_USUARIO": ["ADMIN", "USER", "GUEST"],
                    "ESTADO_CREDENCIAL": ["VALIDA", "INVALIDA", "EXPIRADA"],
                    "INTENTOS": ["OK", "ERROR_TIPO_1", "TIMEOUT"]
                },
                "limites": {
                    "CAMPO_USUARIO_len": {"min": 1, "max": 64},
                    "REINTENTOS": 3,
                    "TIMEOUT_MS": 5000
                },
                "reglas": [
                    "R1: si TIPO_USUARIO=ADMIN y ESTADO_CREDENCIAL=VALIDA -> ACCESO_TOTAL",
                    "R2: si INTENTOS=TIMEOUT -> reintentar 1 vez y marcar pendiente",
                    "R3: si REINTENTOS supera límite -> bloquear y auditar"
                ],
                "tecnicas": {
                    "equivalencia": True,
                    "valores_limite": True,
                    "tabla_decision": True,
                    "transicion_estados": True,
                    "arbol_clasificacion": True,
                    "pairwise": True,
                    "casos_uso": True,
                    "error_guessing": True,
                    "checklist": True
                },
                "priorizacion": "Riesgo",
                "cantidad_max": 150,
                "salida_plan_ejecucion": {
                    "incluir": True,
                    "formato": "cursor_playwright_mcp"
                }
            }
        }

class ISTQBTestGenerationResponse(BaseModel):
    """Respuesta de la generación de casos de prueba ISTQB"""
    programa: str = Field(..., description="Nombre del programa", example="SISTEMA_AUTH")
    generation_id: str = Field(..., description="ID único de la generación", example="istqb_SISTEMA_AUTH_1760825804")
    status: str = Field(..., description="Estado de la generación", example="completed")
    csv_cases: List[str] = Field(..., description="Lista de casos de prueba en formato CSV")
    fichas: List[str] = Field(..., description="Fichas detalladas de casos de prueba")
    artefactos_tecnicos: Dict[str, Any] = Field(..., description="Artefactos técnicos generados")
    plan_ejecucion: Dict[str, Any] = Field(..., description="Plan de ejecución (si aplica)")
    confidence_score: float = Field(..., description="Puntuación de confianza (0-1)", example=0.85)
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos", example=25.3)
    created_at: datetime = Field(..., description="Timestamp de creación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "programa": "SISTEMA_AUTH",
                "generation_id": "istqb_SISTEMA_AUTH_1760825804",
                "status": "completed",
                "csv_cases": [
                    "CP - 001 - SISTEMA_AUTH - AUTORIZACION - TIPO_USUARIO_ADMIN - AUTORIZA Y REGISTRA OPERACION",
                    "CP - 002 - SISTEMA_AUTH - VALIDACION - ESTADO_CREDENCIAL_VALIDA - VALIDA Y PERMITE ACCESO"
                ],
                "fichas": [
                    "1 - CP - 001 - SISTEMA_AUTH - AUTORIZACION - TIPO_USUARIO_ADMIN - AUTORIZA Y REGISTRA OPERACION\n2- Precondicion: Usuario activo; datos completos; firma válida\n3- Resultado Esperado: Operación autorizada; ID transacción generado; registro persistido y auditado"
                ],
                "artefactos_tecnicos": {
                    "equivalencias": "Particiones válidas/inválidas por cada factor",
                    "valores_limite": "Casos min-1,min,min+1,max-1,max,max+1 para límites",
                    "tabla_decision": "Matriz Condiciones→Acciones"
                },
                "plan_ejecucion": {
                    "formato": "cursor_playwright_mcp",
                    "casos": []
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

@app.get("/", 
         response_model=Dict[str, str],
         summary="Información del servicio",
         description="Endpoint raíz que proporciona información básica sobre el microservicio de análisis QA",
         tags=["Información"])
async def root():
    """
    ## Información del Servicio
    
    Retorna información básica sobre el microservicio de análisis QA.
    
    ### Respuesta:
    - **message**: Descripción del servicio
    - **version**: Versión actual de la API
    - **docs**: URL de la documentación Swagger
    """
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

@app.post("/analyze", 
          response_model=TestCaseAnalysisResponse,
          summary="Analizar caso de prueba",
          description="Analiza un caso de prueba individual y genera sugerencias de mejora usando IA",
          tags=["Análisis"],
          responses={
              200: {
                  "description": "Análisis completado exitosamente",
                  "model": TestCaseAnalysisResponse
              },
              400: {
                  "description": "Datos de entrada inválidos",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Datos de entrada inválidos"}
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
async def analyze_test_case(
    request: TestCaseAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    ## Analizar Caso de Prueba
    
    Analiza un caso de prueba individual utilizando IA generativa (Google Gemini) y genera sugerencias de mejora estructuradas.
    
    ### Proceso:
    1. **Sanitización**: Se elimina información sensible del contenido
    2. **Análisis IA**: Se procesa con Google Gemini usando prompts especializados
    3. **Estructuración**: Se organizan las sugerencias en categorías
    4. **Observabilidad**: Se registra en Langfuse para monitoreo
    
    ### Tipos de Sugerencias:
    - **Clarity**: Mejoras en claridad y legibilidad
    - **Coverage**: Sugerencias para mejorar cobertura de pruebas
    - **Automation**: Optimizaciones para automatización
    - **Best Practice**: Mejores prácticas de testing
    
    ### Respuesta:
    - **suggestions**: Lista de sugerencias categorizadas
    - **confidence_score**: Puntuación de confianza (0-1)
    - **processing_time**: Tiempo de procesamiento en segundos
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

@app.post("/analyze-requirements", 
          response_model=RequirementsAnalysisResponse,
          summary="Analizar requerimientos y generar casos de prueba",
          description="Analiza un requerimiento y genera casos de prueba estructurados usando IA",
          tags=["Requerimientos"],
          responses={
              200: {
                  "description": "Análisis de requerimientos completado exitosamente",
                  "model": RequirementsAnalysisResponse
              },
              400: {
                  "description": "Datos de entrada inválidos",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Datos de entrada inválidos"}
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
async def analyze_requirements(
    request: RequirementsAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    ## Analizar Requerimientos y Generar Casos de Prueba
    
    Analiza un requerimiento de software y genera casos de prueba estructurados utilizando IA generativa.
    
    ### Proceso:
    1. **Análisis del Requerimiento**: Se procesa el contenido del requerimiento
    2. **Generación de Casos**: Se crean casos de prueba para diferentes tipos y niveles
    3. **Estructuración**: Se organizan los casos con pasos, datos y resultados esperados
    4. **Análisis de Cobertura**: Se evalúa la cobertura de pruebas generada
    
    ### Tipos de Pruebas Soportados:
    - **Functional**: Pruebas funcionales básicas
    - **Integration**: Pruebas de integración
    - **UI**: Pruebas de interfaz de usuario
    - **API**: Pruebas de API
    - **Security**: Pruebas de seguridad
    - **Performance**: Pruebas de rendimiento
    
    ### Niveles de Cobertura:
    - **Low**: Casos básicos esenciales
    - **Medium**: Casos estándar con casos edge
    - **High**: Cobertura completa con casos complejos
    - **Comprehensive**: Cobertura exhaustiva con todos los escenarios
    
    ### Respuesta:
    - **test_cases**: Lista de casos de prueba generados
    - **coverage_analysis**: Análisis de cobertura por tipo
    - **confidence_score**: Puntuación de confianza (0-1)
    - **processing_time**: Tiempo de procesamiento en segundos
    """
    start_time = datetime.utcnow()
    analysis_id = f"req_analysis_{request.requirement_id}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting requirements analysis",
            requirement_id=request.requirement_id,
            analysis_id=analysis_id,
            project_key=request.project_key
        )
        
        # Sanitizar contenido sensible
        sanitized_content = sanitizer.sanitize(request.requirement_content)
        
        # Generar prompt para análisis de requerimientos
        prompt = prompt_templates.get_requirements_analysis_prompt(
            requirement_content=sanitized_content,
            project_key=request.project_key,
            priority=request.priority,
            test_types=request.test_types,
            coverage_level=request.coverage_level
        )
        
        # Ejecutar análisis con LLM
        analysis_result = await llm_wrapper.analyze_requirements(
            prompt=prompt,
            requirement_id=request.requirement_id,
            analysis_id=analysis_id
        )
        
        # Procesar casos de prueba generados
        test_cases = []
        if analysis_result.get("test_cases"):
            for tc_data in analysis_result["test_cases"]:
                test_case = TestCase(
                    test_case_id=tc_data.get("test_case_id", f"TC-{request.requirement_id}-001"),
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
        response = RequirementsAnalysisResponse(
            requirement_id=request.requirement_id,
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
            log_requirements_analysis_completion,
            analysis_id,
            request.requirement_id,
            response
        )
        
        logger.info(
            "Requirements analysis completed",
            requirement_id=request.requirement_id,
            analysis_id=analysis_id,
            test_cases_count=len(test_cases),
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Requirements analysis failed",
            requirement_id=request.requirement_id,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing requirements: {str(e)}"
        )

@app.post("/analyze-jira-workitem", 
          response_model=JiraWorkItemResponse,
          summary="Analizar work item de Jira y generar casos de prueba",
          description="Obtiene un work item de Jira y genera casos de prueba estructurados usando IA",
          tags=["Integración Jira"],
          responses={
              200: {
                  "description": "Análisis de work item completado exitosamente",
                  "model": JiraWorkItemResponse
              },
              400: {
                  "description": "Datos de entrada inválidos o work item no encontrado",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Work item no encontrado en Jira"}
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
    request: JiraWorkItemRequest,
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
    
    ### Tipos de Pruebas Soportados:
    - **Functional**: Pruebas funcionales básicas
    - **Integration**: Pruebas de integración
    - **UI**: Pruebas de interfaz de usuario
    - **API**: Pruebas de API
    - **Security**: Pruebas de seguridad
    - **Performance**: Pruebas de rendimiento
    
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
            project_key=request.project_key,
            analysis_id=analysis_id
        )
        
        # Obtener datos del work item desde Jira
        jira_data = await tracker_client.get_work_item_details(
            work_item_id=request.work_item_id,
            project_key=request.project_key
        )
        
        if not jira_data:
            raise HTTPException(
                status_code=404,
                detail=f"Work item {request.work_item_id} not found in project {request.project_key}"
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
        if request.include_acceptance_criteria and jira_data.get('acceptance_criteria'):
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
            project_key=request.project_key,
            test_types=request.test_types,
            coverage_level=request.coverage_level
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
                    test_case_id=tc_data.get("test_case_id", f"TC-{request.project_key}-001"),
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
        response = JiraWorkItemResponse(
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

@app.post("/generate-istqb-tests", 
          response_model=ISTQBTestGenerationResponse,
          summary="Generar casos de prueba con técnicas ISTQB",
          description="Genera casos de prueba aplicando técnicas de diseño ISTQB Foundation Level",
          tags=["ISTQB", "Generación Avanzada"],
          responses={
              200: {
                  "description": "Generación de casos ISTQB completada exitosamente",
                  "model": ISTQBTestGenerationResponse
              },
              400: {
                  "description": "Datos de entrada inválidos",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Datos de entrada inválidos"}
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
async def generate_istqb_test_cases(
    request: ISTQBTestGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    ## Generar Casos de Prueba con Técnicas ISTQB
    
    Genera casos de prueba aplicando técnicas de diseño ISTQB Foundation Level con observabilidad completa.
    
    ### Proceso:
    1. **Análisis de Configuración**: Se procesa la configuración JSON del sistema
    2. **Aplicación de Técnicas**: Se aplican las técnicas ISTQB especificadas
    3. **Generación Estructurada**: Se crean casos en formato CSV, fichas y artefactos técnicos
    4. **Plan de Ejecución**: Se genera plan de ejecución automatizado (opcional)
    5. **Observabilidad**: Se registra en Langfuse para monitoreo y análisis
    
    ### Técnicas ISTQB Soportadas:
    - **Equivalencia**: Partición de clases de equivalencia válidas/inválidas
    - **Valores Límite**: Casos min-1, min, min+1, max-1, max, max+1
    - **Tabla de Decisión**: Matriz de condiciones y acciones
    - **Transición de Estados**: Estados y transiciones del sistema
    - **Árbol de Clasificación**: Clases y restricciones entre factores
    - **Pairwise**: Combinaciones mínimas que cubren todas las parejas
    - **Casos de Uso**: Flujos principales y alternos
    - **Error Guessing**: Hipótesis de fallos del dominio
    - **Checklist**: Verificación genérica de calidad
    
    ### Formato de Salida:
    - **Sección A**: CSV con casos de prueba (CP - NNN - PROGRAMA - MODULO - CONDICION - ESCENARIO)
    - **Sección B**: Fichas detalladas con precondiciones y resultados esperados
    - **Sección C**: Artefactos técnicos según técnicas seleccionadas
    - **Sección D**: Plan de ejecución automatizado (opcional)
    
    ### Respuesta:
    - **csv_cases**: Lista de casos en formato CSV
    - **fichas**: Fichas detalladas de cada caso
    - **artefactos_tecnicos**: Artefactos generados por las técnicas
    - **plan_ejecucion**: Plan de ejecución automatizado
    - **confidence_score**: Puntuación de confianza (0-1)
    - **processing_time**: Tiempo de procesamiento en segundos
    """
    start_time = datetime.utcnow()
    generation_id = f"istqb_{request.programa}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting ISTQB test case generation",
            programa=request.programa,
            generation_id=generation_id,
            modulos_count=len(request.modulos),
            tecnicas_count=sum(1 for v in request.tecnicas.values() if v)
        )
        
        # Generar prompt ISTQB
        prompt = prompt_templates.get_istqb_test_generation_prompt(
            programa=request.programa,
            dominio=request.dominio,
            modulos=request.modulos,
            factores=request.factores,
            limites=request.limites,
            reglas=request.reglas,
            tecnicas=request.tecnicas,
            priorizacion=request.priorizacion,
            cantidad_max=request.cantidad_max,
            salida_plan_ejecucion=request.salida_plan_ejecucion
        )
        
        # Ejecutar generación con LLM
        generation_result = await llm_wrapper.generate_istqb_test_cases(
            prompt=prompt,
            programa=request.programa,
            generation_id=generation_id
        )
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = ISTQBTestGenerationResponse(
            programa=request.programa,
            generation_id=generation_id,
            status="completed",
            csv_cases=generation_result.get("csv_cases", []),
            fichas=generation_result.get("fichas", []),
            artefactos_tecnicos=generation_result.get("artefactos_tecnicos", {}),
            plan_ejecucion=generation_result.get("plan_ejecucion", {}),
            confidence_score=generation_result.get("confidence_score", 0.8),
            processing_time=processing_time,
            created_at=start_time
        )
        
        # Registrar en background task para tracking
        background_tasks.add_task(
            log_istqb_generation_completion,
            generation_id,
            request.programa,
            response
        )
        
        logger.info(
            "ISTQB test case generation completed",
            programa=request.programa,
            generation_id=generation_id,
            csv_cases_count=len(response.csv_cases),
            fichas_count=len(response.fichas),
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "ISTQB test case generation failed",
            programa=request.programa,
            generation_id=generation_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error generating ISTQB test cases: {str(e)}"
        )

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

async def log_requirements_analysis_completion(
    analysis_id: str,
    requirement_id: str,
    response: RequirementsAnalysisResponse
):
    """Background task para registrar la finalización del análisis de requerimientos"""
    try:
        # Aquí podrías implementar lógica adicional como:
        # - Guardar en base de datos
        # - Enviar notificaciones
        # - Actualizar métricas
        logger.info(
            "Requirements analysis completion logged",
            analysis_id=analysis_id,
            requirement_id=requirement_id,
            test_cases_count=len(response.test_cases)
        )
    except Exception as e:
        logger.error(
            "Failed to log requirements analysis completion",
            analysis_id=analysis_id,
            error=str(e)
        )

async def log_jira_workitem_analysis_completion(
    analysis_id: str,
    work_item_id: str,
    response: JiraWorkItemResponse
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
    response: ISTQBTestGenerationResponse
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
            "ISTQB test generation completion logged",
            generation_id=generation_id,
            programa=programa,
            csv_cases_count=len(response.csv_cases),
            fichas_count=len(response.fichas),
            artefactos_count=len(response.artefactos_tecnicos)
        )
    except Exception as e:
        logger.error(
            "Failed to log ISTQB generation completion",
            generation_id=generation_id,
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
