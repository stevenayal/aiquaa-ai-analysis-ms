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
    
    Esta API proporciona análisis inteligente de contenido (casos de prueba, requerimientos, historias de usuario) utilizando IA generativa y técnicas de diseño ISTQB Foundation Level.
    
    ### Características:
    - 🤖 Análisis automatizado con Google Gemini
    - 📊 Observabilidad completa con Langfuse
    - 🔗 Integración simplificada con Jira
    - 📝 Generación de casos de prueba estructurados
    - 🎯 **NUEVO**: Generación de casos con técnicas ISTQB avanzadas
    - 🔬 **NUEVO**: Aplicación de 9 técnicas de diseño de pruebas
    - 📋 **NUEVO**: Formato estructurado con CSV, fichas y artefactos técnicos
    - ⚡ **OPTIMIZADO**: Endpoints unificados y parámetros simplificados
    
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
    
    ### Uso Simplificado:
    1. **Análisis unificado**: Usa `/analyze` para cualquier tipo de contenido
    2. **Integración Jira**: Usa `/analyze-jira` para work items (solo ID requerido)
    3. **Generación ISTQB**: Usa `/generate-istqb-tests` para casos avanzados
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
