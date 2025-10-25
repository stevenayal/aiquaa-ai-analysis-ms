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
from fastapi.responses import RedirectResponse
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
    
    Análisis inteligente de contenido usando IA generativa y técnicas avanzadas de testing.
    
    ### Características:
    - 🤖 Análisis automatizado con Google Gemini
    - 📊 Observabilidad con Langfuse
    - 🔗 Integración con Jira
    - 📝 Generación de casos estructurados
    - 🎯 Técnicas avanzadas de testing
    
    ### Endpoints:
    - `/analizar` - Análisis unificado de contenido
    - `/analizar-jira` - Análisis de work items de Jira
    - `/analizar-jira-confluence` - Análisis de Jira y diseño de planes de prueba para Confluence
    - `/generar-pruebas-avanzadas` - Generación con técnicas avanzadas
    - `/analisis/requisitos/verificacion-istqb` - Análisis estático de requisitos ISTQB
    - `/salud` - Estado del servicio
    
    ### Tipos de Contenido:
    - **test_case** - Casos de prueba existentes
    - **requirement** - Requerimientos
    - **user_story** - Historias de usuario
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "deepLinking": True,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
        "requestSnippetsEnabled": True,
        "syntaxHighlight.theme": "agate",
        "theme": "dark"
    },
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
        },
        {
            "url": "https://ia-analisis-production.up.railway.app",
            "description": "Servidor de producción (Railway)"
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
    id_contenido: str = Field(
        ..., 
        description="ID único del contenido a analizar",
        example="TC-001",
        min_length=1,
        max_length=50
    )
    contenido: str = Field(
        ..., 
        description="Contenido a analizar (caso de prueba, requerimiento, historia de usuario)",
        example="Verificar que el usuario pueda iniciar sesión con credenciales válidas",
        min_length=10,
        max_length=10000
    )
    tipo_contenido: str = Field(
        "test_case",
        description="Tipo de contenido a analizar",
        example="test_case",
        pattern="^(test_case|requirement|user_story)$"
    )
    nivel_analisis: Optional[str] = Field(
        "medium",
        description="Nivel de análisis y cobertura",
        example="high",
        pattern="^(low|medium|high|comprehensive)$"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "id_contenido": "TC-001",
                "contenido": "Verificar que el usuario pueda iniciar sesión con credenciales válidas. Pasos: 1) Abrir la página de login, 2) Ingresar usuario válido, 3) Ingresar contraseña válida, 4) Hacer clic en 'Iniciar Sesión'. Resultado esperado: Usuario logueado exitosamente y redirigido al dashboard.",
                "tipo_contenido": "test_case",
                "nivel_analisis": "high"
            }
        }

class Suggestion(BaseModel):
    """Sugerencia de mejora para un caso de prueba"""
    tipo: str = Field(..., description="Tipo de sugerencia", example="clarity")
    titulo: str = Field(..., description="Título de la sugerencia", example="Definir datos de prueba específicos")
    descripcion: str = Field(..., description="Descripción detallada", example="El caso de prueba debe incluir datos específicos de usuario y contraseña")
    prioridad: str = Field(..., description="Prioridad de la sugerencia", example="high")
    categoria: str = Field(..., description="Categoría de la mejora", example="improvement")

class TestCase(BaseModel):
    """Caso de prueba generado con estructura estandarizada"""
    id_caso_prueba: str = Field(..., description="ID del caso de prueba", example="CP-001-APLICACION-MODULO-DATO-CONDICION-RESULTADO")
    titulo: str = Field(..., description="Título del caso de prueba en formato CP - 001 - Aplicacion - Modulo - Dato - Condicion - Resultado", example="CP - 001 - Aplicacion - Modulo - Dato - Condicion - Resultado")
    descripcion: str = Field(..., description="Descripción detallada del caso de prueba")
    tipo_prueba: str = Field(..., description="Tipo de prueba", example="functional")
    prioridad: str = Field(..., description="Prioridad del caso de prueba", example="high")
    pasos: List[str] = Field(..., description="Pasos detallados del caso de prueba")
    resultado_esperado: str = Field(..., description="Resultado esperado en formato 'Resultado Esperado: [descripción]'", example="Resultado Esperado: Usuario autenticado exitosamente y redirigido al dashboard")
    precondiciones: List[str] = Field(default_factory=list, description="Precondiciones en formato 'Precondicion: [descripción]'", example=["Precondicion: Usuario existe en la base de datos", "Precondicion: Sistema de autenticación activo"])
    datos_prueba: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Datos de prueba específicos")
    potencial_automatizacion: str = Field(..., description="Potencial de automatización", example="high")
    duracion_estimada: str = Field(..., description="Duración estimada", example="5-10 minutes")

class AnalysisResponse(BaseModel):
    """Respuesta unificada del análisis de contenido"""
    id_contenido: str = Field(..., description="ID del contenido analizado", example="TC-001")
    id_analisis: str = Field(..., description="ID único del análisis", example="analysis_TC001_1760825804")
    estado: str = Field(..., description="Estado del análisis", example="completed")
    casos_prueba: List[TestCase] = Field(default_factory=list, description="Lista de casos de prueba generados")
    sugerencias: List[Suggestion] = Field(default_factory=list, description="Lista de sugerencias de mejora")
    analisis_cobertura: Dict[str, Any] = Field(default_factory=dict, description="Análisis de cobertura de pruebas")
    puntuacion_confianza: float = Field(..., description="Puntuación de confianza del análisis (0-1)", example=0.85)
    tiempo_procesamiento: float = Field(..., description="Tiempo de procesamiento en segundos", example=8.81)
    fecha_creacion: datetime = Field(..., description="Timestamp de creación del análisis")
    
    class Config:
        schema_extra = {
            "example": {
                "id_contenido": "TC-001",
                "id_analisis": "analysis_TC001_1760825804",
                "estado": "completed",
                "casos_prueba": [
                    {
                        "id_caso_prueba": "CP-001-AUTH-LOGIN-CREDENCIALES_VALIDAS-AUTENTICACION_EXITOSA",
                        "titulo": "CP - 001 - AUTH - LOGIN - CREDENCIALES_VALIDAS - AUTENTICACION_EXITOSA",
                        "descripcion": "Caso de prueba para verificar autenticación exitosa",
                        "tipo_prueba": "functional",
                        "prioridad": "high",
                        "pasos": ["Navegar a login", "Ingresar credenciales", "Hacer clic en login"],
                        "resultado_esperado": "Resultado Esperado: Usuario autenticado exitosamente y redirigido al dashboard",
                        "precondiciones": ["Precondicion: Usuario existe en la base de datos", "Precondicion: Sistema de autenticación activo"],
                        "datos_prueba": {"email": "test@example.com", "password": "Test123!"},
                        "potencial_automatizacion": "high",
                        "duracion_estimada": "5-10 minutes"
                    }
                ],
                "sugerencias": [
                    {
                        "tipo": "clarity",
                        "titulo": "Definir datos de prueba específicos",
                        "descripcion": "El caso de prueba debe incluir datos específicos de usuario y contraseña",
                        "prioridad": "high",
                        "categoria": "improvement"
                    }
                ],
                "analisis_cobertura": {
                    "functional_coverage": "90%",
                    "edge_case_coverage": "75%",
                    "integration_coverage": "80%"
                },
                "puntuacion_confianza": 0.85,
                "tiempo_procesamiento": 8.81,
                "fecha_creacion": "2025-10-18T19:16:44.520862"
            }
        }

class JiraAnalysisRequest(BaseModel):
    """Solicitud simplificada de análisis de work item de Jira"""
    id_work_item: str = Field(
        ..., 
        description="ID del work item en Jira (ej: PROJ-123)",
        example="AUTH-123",
        min_length=1,
        max_length=50
    )
    nivel_analisis: Optional[str] = Field(
        "medium",
        description="Nivel de análisis y cobertura",
        example="high",
        pattern="^(low|medium|high|comprehensive)$"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_work_item": "AUTH-123",
                "nivel_analisis": "high"
            }
        }

class JiraAnalysisResponse(BaseModel):
    """Respuesta del análisis de work item de Jira"""
    id_work_item: str = Field(..., description="ID del work item analizado", example="AUTH-123")
    datos_jira: Dict[str, Any] = Field(..., description="Datos obtenidos de Jira")
    id_analisis: str = Field(..., description="ID único del análisis", example="jira_analysis_AUTH123_1760825804")
    estado: str = Field(..., description="Estado del análisis", example="completed")
    casos_prueba: List[TestCase] = Field(..., description="Lista de casos de prueba generados")
    analisis_cobertura: Dict[str, Any] = Field(..., description="Análisis de cobertura de pruebas")
    puntuacion_confianza: float = Field(..., description="Puntuación de confianza del análisis (0-1)", example=0.85)
    tiempo_procesamiento: float = Field(..., description="Tiempo de procesamiento en segundos", example=15.5)
    fecha_creacion: datetime = Field(..., description="Timestamp de creación del análisis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_work_item": "AUTH-123",
                "datos_jira": {
                    "summary": "Implementar autenticación de usuarios",
                    "description": "El sistema debe permitir a los usuarios autenticarse...",
                    "issue_type": "Story",
                    "priority": "High",
                    "status": "In Progress"
                },
                "id_analisis": "jira_analysis_AUTH123_1760825804",
                "estado": "completed",
                "casos_prueba": [
                    {
                        "id_caso_prueba": "CP-001-AUTH-LOGIN-CREDENCIALES_VALIDAS-AUTENTICACION_EXITOSA",
                        "titulo": "CP - 001 - AUTH - LOGIN - CREDENCIALES_VALIDAS - AUTENTICACION_EXITOSA",
                        "descripcion": "Caso de prueba para verificar autenticación exitosa",
                        "tipo_prueba": "functional",
                        "prioridad": "high",
                        "pasos": ["Navegar a login", "Ingresar credenciales", "Hacer clic en login"],
                        "resultado_esperado": "Resultado Esperado: Usuario autenticado exitosamente y redirigido al dashboard",
                        "precondiciones": ["Precondicion: Usuario existe en la base de datos", "Precondicion: Sistema de autenticación activo"],
                        "datos_prueba": {"email": "test@example.com", "password": "Test123!"},
                        "potencial_automatizacion": "high",
                        "duracion_estimada": "5-10 minutes"
                    }
                ],
                "analisis_cobertura": {
                    "functional_coverage": "90%",
                    "edge_case_coverage": "75%",
                    "integration_coverage": "80%"
                },
                "puntuacion_confianza": 0.85,
                "tiempo_procesamiento": 15.5,
                "fecha_creacion": "2025-10-18T19:16:44.520862"
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "requerimiento": "El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado.",
                "aplicacion": "SISTEMA_AUTH"
            }
        }

class AdvancedTestGenerationResponse(BaseModel):
    """Respuesta de la generación de casos de prueba avanzados"""
    aplicacion: str = Field(..., description="Nombre de la aplicación", example="SISTEMA_AUTH")
    id_generacion: str = Field(..., description="ID único de la generación", example="advanced_SISTEMA_AUTH_1760825804")
    estado: str = Field(..., description="Estado de la generación", example="completed")
    casos_prueba: List[TestCase] = Field(..., description="Lista de casos de prueba generados")
    analisis_cobertura: Dict[str, Any] = Field(..., description="Análisis de cobertura de pruebas")
    puntuacion_confianza: float = Field(..., description="Puntuación de confianza (0-1)", example=0.85)
    tiempo_procesamiento: float = Field(..., description="Tiempo de procesamiento en segundos", example=25.3)
    fecha_creacion: datetime = Field(..., description="Timestamp de creación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "aplicacion": "SISTEMA_AUTH",
                "id_generacion": "advanced_SISTEMA_AUTH_1760825804",
                "estado": "completed",
                "casos_prueba": [
                    {
                        "id_caso_prueba": "CP-001-AUTH-LOGIN-CREDENCIALES_VALIDAS-AUTENTICACION_EXITOSA",
                        "titulo": "CP - 001 - AUTH - LOGIN - CREDENCIALES_VALIDAS - AUTENTICACION_EXITOSA",
                        "descripcion": "Caso de prueba para verificar autenticación exitosa",
                        "tipo_prueba": "functional",
                        "prioridad": "high",
                        "pasos": ["Navegar a login", "Ingresar credenciales", "Hacer clic en login"],
                        "resultado_esperado": "Resultado Esperado: Usuario autenticado exitosamente y redirigido al dashboard",
                        "precondiciones": ["Precondicion: Usuario existe en la base de datos", "Precondicion: Sistema de autenticación activo"],
                        "datos_prueba": {"email": "test@example.com", "password": "Test123!"},
                        "potencial_automatizacion": "high",
                        "duracion_estimada": "5-10 minutes"
                    }
                ],
                "analisis_cobertura": {
                    "functional_coverage": "90%",
                    "edge_case_coverage": "75%",
                    "integration_coverage": "80%"
                },
                "puntuacion_confianza": 0.85,
                "tiempo_procesamiento": 25.3,
                "fecha_creacion": "2025-10-18T19:16:44.520862"
            }
        }

class HealthResponse(BaseModel):
    """Respuesta de salud del servicio"""
    estado: str
    timestamp: datetime
    version: str
    componentes: Dict[str, str]

# Modelos para análisis ISTQB de requisitos
class RequirementContext(BaseModel):
    """Contexto del requerimiento"""
    producto: str = Field(..., description="Producto o sistema", example="Sistema de Autenticación")
    modulo: str = Field(..., description="Módulo o componente", example="Login")
    stakeholders: List[str] = Field(default_factory=list, description="Stakeholders involucrados", example=["PO", "QA", "Dev"])
    restricciones: List[str] = Field(default_factory=list, description="Restricciones o estándares", example=["PCI DSS", "LGPD", "SLA 200ms p95"])
    dependencias: List[str] = Field(default_factory=list, description="Dependencias", example=["API Clientes v2"])

class RequirementGlossary(BaseModel):
    """Glosario de términos del requerimiento"""
    pass  # Se implementará como Dict[str, str] en el modelo principal

class RequirementInput(BaseModel):
    """Estructura de entrada para análisis ISTQB de requisitos"""
    requirement_id: str = Field(..., description="ID único del requerimiento", example="REQ-123")
    requirement_text: str = Field(..., description="Texto completo del requerimiento", min_length=30, max_length=10000)
    context: RequirementContext = Field(..., description="Contexto del requerimiento")
    glossary: Dict[str, str] = Field(default_factory=dict, description="Glosario de términos", example={"NroDoc": "Número de documento nacional", "ClienteVIP": "Cliente con score >= 800"})
    acceptance_template: str = Field(default="Dado/Cuando/Entonces", description="Template para criterios de aceptación")
    non_functional_expectations: List[str] = Field(default_factory=list, description="Expectativas no funcionales", example=["p95<=300ms", "TLS1.3", "a11y WCAG AA"])

class QualityScore(BaseModel):
    """Puntuación de calidad del requerimiento"""
    overall: int = Field(..., description="Puntuación general (0-100)", ge=0, le=100)
    clarity: int = Field(..., description="Claridad (0-100)", ge=0, le=100)
    completeness: int = Field(..., description="Completitud (0-100)", ge=0, le=100)
    consistency: int = Field(..., description="Consistencia (0-100)", ge=0, le=100)
    feasibility: int = Field(..., description="Factibilidad (0-100)", ge=0, le=100)
    testability: int = Field(..., description="Testabilidad (0-100)", ge=0, le=100)

class IssueRisk(BaseModel):
    """Evaluación de riesgo de un issue"""
    severity: str = Field(..., description="Severidad del issue", pattern="^(Low|Medium|High|Critical)$")
    likelihood: str = Field(..., description="Probabilidad del issue", pattern="^(Low|Medium|High)$")
    rpn: int = Field(..., description="Risk Priority Number (1-27)", ge=1, le=27)

class RequirementIssue(BaseModel):
    """Issue detectado en el requerimiento"""
    id: str = Field(..., description="ID único del issue", example="ISS-001")
    type: str = Field(..., description="Tipo de issue", pattern="^(Ambiguity|Omission|Inconsistency|NFRGap|DataSpecGap|ResponsibilityGap|RuleConflict)$")
    heuristic: str = Field(..., description="Heurística aplicada", pattern="^(VagueTerm|FuzzyQuantifier|OpenRange|PronounWithoutAntecedent|PassiveVoice|TemporalDeixis|MissingInputOutput|MissingErrorHandling|UndefinedRole|ImplicitBusinessRule)$")
    excerpt: str = Field(..., description="Fragmento exacto del texto problemático")
    explanation: str = Field(..., description="Explicación del problema según ISTQB")
    impact_area: List[str] = Field(..., description="Áreas de impacto", example=["Value", "Compliance", "Security"])
    risk: IssueRisk = Field(..., description="Evaluación de riesgo")
    fix_suggestion: str = Field(..., description="Sugerencia de corrección")
    proposed_rewrite: str = Field(..., description="Versión reescrita del fragmento")

class CoverageAnalysis(BaseModel):
    """Análisis de cobertura del requerimiento"""
    inputs_defined: bool = Field(..., description="Entradas definidas")
    outputs_defined: bool = Field(..., description="Salidas definidas")
    business_rules: List[str] = Field(default_factory=list, description="Reglas de negocio identificadas")
    error_handling_defined: bool = Field(..., description="Manejo de errores definido")
    roles_responsibilities_defined: bool = Field(..., description="Roles y responsabilidades definidos")
    data_contracts_defined: bool = Field(..., description="Contratos de datos definidos")
    nfr_defined: List[str] = Field(default_factory=list, description="NFRs definidos", example=["performance", "security", "usability"])

class AcceptanceCriterion(BaseModel):
    """Criterio de aceptación"""
    id: str = Field(..., description="ID del criterio", example="AC-1")
    format: str = Field(..., description="Formato del criterio", pattern="^(GWT|Checklist)$")
    criterion: str = Field(..., description="Criterio en formato Dado/Cuando/Entonces")
    measurable: bool = Field(..., description="Es medible")
    test_oracle: str = Field(..., description="Oráculo de prueba")
    example_data: Dict[str, Any] = Field(default_factory=dict, description="Datos de ejemplo")

class TraceabilityAnalysis(BaseModel):
    """Análisis de trazabilidad"""
    glossary_terms_used: List[str] = Field(default_factory=list, description="Términos del glosario utilizados")
    external_refs_needed: List[str] = Field(default_factory=list, description="Referencias externas necesarias")
    dependencies_touched: List[str] = Field(default_factory=list, description="Dependencias tocadas")

class ISTQBAnalysisResponse(BaseModel):
    """Respuesta del análisis ISTQB de requisitos"""
    id_requerimiento: str = Field(..., description="ID del requerimiento analizado")
    puntuacion_calidad: QualityScore = Field(..., description="Puntuación de calidad")
    issues: List[RequirementIssue] = Field(default_factory=list, description="Issues detectados")
    cobertura: CoverageAnalysis = Field(..., description="Análisis de cobertura")
    criterios_aceptacion: List[AcceptanceCriterion] = Field(default_factory=list, description="Criterios de aceptación")
    trazabilidad: TraceabilityAnalysis = Field(..., description="Análisis de trazabilidad")
    resumen: str = Field(..., description="Resumen ejecutivo")
    version_limpia_propuesta: str = Field(..., description="Versión limpia propuesta del requerimiento")
    id_analisis: str = Field(..., description="ID único del análisis")
    tiempo_procesamiento: float = Field(..., description="Tiempo de procesamiento en segundos")
    fecha_creacion: datetime = Field(..., description="Timestamp de creación")

# Modelos para análisis de Jira y diseño de planes de prueba en Confluence
class ConfluenceTestPlanRequest(BaseModel):
    """Solicitud simplificada de análisis de Jira y diseño de plan de pruebas para Confluence"""
    id_issue_jira: str = Field(
        ..., 
        description="ID del issue de Jira a analizar",
        example="PROJ-123",
        min_length=1,
        max_length=50
    )
    espacio_confluence: str = Field(
        ..., 
        description="Clave del espacio de Confluence donde crear el plan",
        example="QA",
        min_length=1,
        max_length=20
    )
    titulo_plan_pruebas: Optional[str] = Field(
        None,
        description="Título del plan de pruebas (opcional, se genera automáticamente si no se proporciona)",
        example="Plan de Pruebas - Autenticación de Usuarios",
        max_length=200
    )
    
    class Config:
        schema_extra = {
            "example": {
                "id_issue_jira": "PROJ-123",
                "espacio_confluence": "QA",
                "titulo_plan_pruebas": "Plan de Pruebas - Autenticación de Usuarios"
            }
        }

class TestPlanSection(BaseModel):
    """Sección del plan de pruebas"""
    id_seccion: str = Field(..., description="ID de la sección", example="overview")
    titulo: str = Field(..., description="Título de la sección", example="Resumen Ejecutivo")
    contenido: str = Field(..., description="Contenido de la sección en formato Confluence")
    orden: int = Field(..., description="Orden de la sección", example=1)

class TestExecutionPhase(BaseModel):
    """Fase de ejecución de pruebas"""
    nombre_fase: str = Field(..., description="Nombre de la fase", example="Fase 1: Pruebas Unitarias")
    duracion: str = Field(..., description="Duración estimada", example="2-3 días")
    cantidad_casos_prueba: int = Field(..., description="Número de casos de prueba", example=15)
    responsable: str = Field(..., description="Responsable de la fase", example="Equipo de Desarrollo")
    dependencias: List[str] = Field(default_factory=list, description="Dependencias de la fase")

class ConfluenceTestPlanResponse(BaseModel):
    """Respuesta del análisis de Jira y diseño de plan de pruebas para Confluence"""
    id_issue_jira: str = Field(..., description="ID del issue de Jira analizado")
    espacio_confluence: str = Field(..., description="Clave del espacio de Confluence")
    titulo_plan_pruebas: str = Field(..., description="Título del plan de pruebas")
    id_analisis: str = Field(..., description="ID único del análisis")
    estado: str = Field(..., description="Estado del análisis", example="completed")
    
    # Datos del issue de Jira
    datos_jira: Dict[str, Any] = Field(..., description="Datos obtenidos de Jira")
    
    # Plan de pruebas estructurado
    secciones_plan_pruebas: List[TestPlanSection] = Field(..., description="Secciones del plan de pruebas")
    fases_ejecucion: List[TestExecutionPhase] = Field(..., description="Fases de ejecución")
    casos_prueba: List[TestCase] = Field(..., description="Casos de prueba generados")
    
    # Metadatos del plan
    total_casos_prueba: int = Field(..., description="Total de casos de prueba generados")
    duracion_estimada: str = Field(..., description="Duración total estimada", example="1-2 semanas")
    nivel_riesgo: str = Field(..., description="Nivel de riesgo del plan", example="medium")
    puntuacion_confianza: float = Field(..., description="Puntuación de confianza (0-1)", example=0.85)
    
    # Contenido para Confluence
    contenido_confluence: str = Field(..., description="Contenido completo del plan en formato Confluence")
    markup_confluence: str = Field(..., description="Markup de Confluence para crear la página")
    
    # Métricas y análisis
    analisis_cobertura: Dict[str, Any] = Field(..., description="Análisis de cobertura de pruebas")
    potencial_automatizacion: Dict[str, Any] = Field(..., description="Análisis de potencial de automatización")
    
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos")
    created_at: datetime = Field(..., description="Timestamp de creación")
    
    class Config:
        schema_extra = {
            "example": {
                "jira_issue_id": "PROJ-123",
                "confluence_space_key": "QA",
                "test_plan_title": "Plan de Pruebas - Autenticación de Usuarios",
                "analysis_id": "confluence_plan_PROJ123_1760825804",
                "status": "completed",
                "jira_data": {
                    "summary": "Implementar autenticación de usuarios",
                    "description": "El sistema debe permitir...",
                    "issue_type": "Story",
                    "priority": "High"
                },
                "total_test_cases": 25,
                "estimated_duration": "1-2 semanas",
                "risk_level": "medium",
                "confidence_score": 0.85,
                "processing_time": 45.2,
                "created_at": "2025-10-18T19:16:44.520862"
            }
        }


@app.get("/", include_in_schema=False)
async def root():
    """Redirigir a la documentación de Swagger"""
    return RedirectResponse(url="/docs")

@app.get("/docs-dark", include_in_schema=False)
async def docs_dark():
    """Documentación de Swagger en modo oscuro"""
    return RedirectResponse(url="/docs?theme=dark")

@app.get("/docs-light", include_in_schema=False)
async def docs_light():
    """Documentación de Swagger en modo claro"""
    return RedirectResponse(url="/docs?theme=light")


@app.get("/salud", response_model=HealthResponse)
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
        estado=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        componentes=components
    )

@app.get("/config", include_in_schema=False)
async def config_check():
    """Verificar configuración del servicio (solo para diagnóstico)"""
    config_status = {
        "google_api_key": "configured" if os.getenv("GOOGLE_API_KEY") else "missing",
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-pro"),
        "langfuse_public_key": "configured" if os.getenv("LANGFUSE_PUBLIC_KEY") else "missing",
        "langfuse_secret_key": "configured" if os.getenv("LANGFUSE_SECRET_KEY") else "missing",
        "jira_base_url": "configured" if os.getenv("JIRA_BASE_URL") else "missing",
        "jira_token": "configured" if os.getenv("JIRA_TOKEN") else "missing",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "port": os.getenv("PORT", "8000")
    }
    
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "configuration": config_status
    }

@app.get("/models", include_in_schema=False)
async def list_available_models():
    """Listar modelos disponibles de Gemini"""
    try:
        if not llm_wrapper.google_api_key:
            return {
                "error": "Google API key not configured",
                "available_models": []
            }
        
        import google.generativeai as genai
        genai.configure(api_key=llm_wrapper.google_api_key)
        
        models = genai.list_models()
        available_models = []
        
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append({
                    "name": model.name,
                    "display_name": model.display_name,
                    "description": model.description,
                    "supported_methods": list(model.supported_generation_methods)
                })
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "available_models": available_models,
            "current_model": llm_wrapper.gemini_model
        }
        
    except Exception as e:
        logger.error("Error listing models", error=str(e))
        return {
            "error": f"Error listing models: {str(e)}",
            "available_models": []
        }

@app.get("/jira-test/{work_item_id}", include_in_schema=False)
async def test_jira_connection(work_item_id: str):
    """Probar conexión con Jira y buscar un work item específico"""
    try:
        # Verificar configuración
        config_status = {
            "jira_base_url": "configured" if os.getenv("JIRA_BASE_URL") else "missing",
            "jira_token": "configured" if os.getenv("JIRA_TOKEN") else "missing",
            "jira_email": "configured" if os.getenv("JIRA_EMAIL") else "missing",
            "jira_org_id": "configured" if os.getenv("JIRA_ORG_ID") else "missing"
        }
        
        # Probar conexión
        health_status = await tracker_client.health_check()
        
        # Buscar work item
        work_item_data = await tracker_client.get_work_item_details(work_item_id)
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "work_item_id": work_item_id,
            "configuration": config_status,
            "health_check": "healthy" if health_status else "unhealthy",
            "work_item_found": work_item_data is not None,
            "work_item_data": work_item_data
        }
        
    except Exception as e:
        logger.error("Error testing Jira connection", error=str(e))
        return {
            "error": f"Error testing Jira: {str(e)}",
            "work_item_id": work_item_id,
            "configuration": {
                "jira_base_url": "configured" if os.getenv("JIRA_BASE_URL") else "missing",
                "jira_token": "configured" if os.getenv("JIRA_TOKEN") else "missing",
                "jira_email": "configured" if os.getenv("JIRA_EMAIL") else "missing"
            }
        }

@app.get("/diagnostico-llm", include_in_schema=False)
async def diagnostico_llm():
    """Diagnóstico del LLM para verificar conectividad"""
    try:
        # Probar conexión con LLM
        start_time = datetime.utcnow()
        await llm_wrapper.test_connection()
        end_time = datetime.utcnow()
        
        return {
            "status": "ok",
            "llm_connection": "healthy",
            "response_time": (end_time - start_time).total_seconds(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "llm_connection": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/analizar-jira-confluence-simple", 
          response_model=ConfluenceTestPlanResponse,
          summary="Análisis simplificado de Jira y diseño de plan de pruebas para Confluence",
          description="Versión simplificada del análisis de Jira-Confluence con prompt más corto para evitar timeouts",
          tags=["Integración Confluence"],
          responses={
              200: {
                  "description": "Análisis simplificado completado exitosamente",
                  "model": ConfluenceTestPlanResponse
              },
              404: {
                  "description": "Issue de Jira no encontrado",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Issue de Jira no encontrado"}
                      }
                  }
              },
              408: {
                  "description": "Timeout en el análisis",
                  "content": {
                      "application/json": {
                          "example": {"detail": "El análisis está tardando más de lo esperado"}
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
async def analyze_jira_confluence_simple(
    request: ConfluenceTestPlanRequest,
    background_tasks: BackgroundTasks
):
    """
    ## Análisis Simplificado de Jira y Diseño de Plan de Pruebas para Confluence
    
    Versión simplificada que usa un prompt más corto para evitar timeouts en producción.
    
    ### Características:
    - Prompt simplificado para análisis más rápido
    - Timeout de 2 minutos en lugar de 5
    - Generación básica de casos de prueba
    - Menos detalle en el plan de pruebas
    """
    start_time = datetime.utcnow()
    analysis_id = f"confluence_simple_{request.id_issue_jira.replace('-', '')}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting simplified Jira-Confluence test plan analysis",
            jira_issue_id=request.id_issue_jira,
            confluence_space_key=request.espacio_confluence,
            test_plan_title=request.titulo_plan_pruebas,
            analysis_id=analysis_id
        )
        
        # Obtener datos del issue desde Jira
        jira_data = await tracker_client.get_work_item_details(
            work_item_id=request.id_issue_jira,
            project_key=""
        )
        
        if not jira_data:
            raise HTTPException(
                status_code=404,
                detail=f"Issue de Jira {request.id_issue_jira} not found"
            )
        
        # Generar título del plan si no se proporciona
        if not request.titulo_plan_pruebas:
            request.titulo_plan_pruebas = f"Plan de Pruebas - {jira_data.get('summary', request.id_issue_jira)}"
        
        # Sanitizar contenido sensible
        sanitized_jira_data = sanitizer.sanitize_dict(jira_data)
        
        # Generar prompt simplificado
        prompt_simple = f"""
        Analiza el siguiente issue de Jira y genera un plan de pruebas básico para Confluence:

        ISSUE: {sanitized_jira_data.get('summary', '')}
        DESCRIPCIÓN: {sanitized_jira_data.get('description', '')[:500]}...
        TIPO: {sanitized_jira_data.get('issue_type', '')}
        PRIORIDAD: {sanitized_jira_data.get('priority', '')}

        Genera:
        1. 3-5 casos de prueba básicos
        2. Plan de ejecución simple
        3. Contenido para Confluence

        Responde en formato JSON con: test_cases, execution_plan, confluence_content
        """
        
        # Ejecutar análisis con LLM con timeout reducido
        try:
            analysis_result = await asyncio.wait_for(
                llm_wrapper.analyze_requirements(
                    prompt=prompt_simple,
                    requirement_id=request.id_issue_jira,
                    analysis_id=analysis_id
                ),
                timeout=120.0  # 2 minutos de timeout
            )
        except asyncio.TimeoutError:
            logger.error(
                "LLM analysis timeout (simplified)",
                jira_issue_id=request.id_issue_jira,
                analysis_id=analysis_id
            )
            raise HTTPException(
                status_code=408,
                detail="El análisis simplificado está tardando más de lo esperado. Por favor, intenta con un issue más simple."
            )
        
        # Procesar casos de prueba básicos
        test_cases = []
        if analysis_result.get("test_cases"):
            for i, tc_data in enumerate(analysis_result["test_cases"][:5], 1):  # Máximo 5 casos
                test_case = TestCase(
                    id_caso_prueba=tc_data.get("test_case_id", f"TC-{request.id_issue_jira}-{i:03d}"),
                    titulo=tc_data.get("title", f"Caso de Prueba {i}"),
                    descripcion=tc_data.get("description", ""),
                    pasos=tc_data.get("steps", []),
                    resultado_esperado=tc_data.get("expected_result", ""),
                    datos_prueba=tc_data.get("test_data", {}),
                    tipo_prueba=tc_data.get("test_type", "funcional"),
                    prioridad=tc_data.get("priority", "media"),
                    precondiciones=tc_data.get("preconditions", []),
                    potencial_automatizacion=tc_data.get("automation_potential", "media"),
                    duracion_estimada=tc_data.get("estimated_duration", "5-10 minutos")
                )
                test_cases.append(test_case)
        
        # Crear secciones básicas del plan
        test_plan_sections = [
            TestPlanSection(
                id_seccion="resumen",
                titulo="Resumen del Plan",
                contenido=f"Plan de pruebas básico para {request.titulo_plan_pruebas}",
                orden=1
            ),
            TestPlanSection(
                id_seccion="casos",
                titulo="Casos de Prueba",
                contenido=f"Se han generado {len(test_cases)} casos de prueba básicos",
                orden=2
            )
        ]
        
        # Crear fases básicas
        test_execution_phases = [
            TestExecutionPhase(
                nombre_fase="Fase 1: Ejecución Básica",
                duracion="1-2 días",
                cantidad_casos_prueba=len(test_cases),
                responsable="Equipo QA",
                dependencias=[]
            )
        ]
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta simplificada
        response = ConfluenceTestPlanResponse(
            id_issue_jira=request.id_issue_jira,
            espacio_confluence=request.espacio_confluence,
            titulo_plan_pruebas=request.titulo_plan_pruebas,
            id_analisis=analysis_id,
            estado="completed",
            datos_jira=jira_data,
            secciones_plan_pruebas=test_plan_sections,
            fases_ejecucion=test_execution_phases,
            casos_prueba=test_cases,
            total_casos_prueba=len(test_cases),
            duracion_estimada="1-2 días",
            nivel_riesgo="bajo",
            puntuacion_confianza=0.7,
            contenido_confluence=analysis_result.get("confluence_content", "Contenido básico generado"),
            markup_confluence=analysis_result.get("confluence_content", "Contenido básico generado"),
            analisis_cobertura={"funcional": "80%"},
            potencial_automatizacion={"total_casos": len(test_cases), "automatizables": len(test_cases)//2, "porcentaje": "50%"},
            processing_time=processing_time,
            created_at=start_time
        )
        
        # Registrar en background task para tracking
        background_tasks.add_task(
            log_confluence_test_plan_completion,
            analysis_id,
            request.id_issue_jira,
            response
        )
        
        logger.info(
            "Simplified Jira-Confluence test plan analysis completed",
            jira_issue_id=request.id_issue_jira,
            analysis_id=analysis_id,
            test_cases_count=len(test_cases),
            processing_time=processing_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Simplified Jira-Confluence test plan analysis failed",
            jira_issue_id=request.id_issue_jira,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis simplificado: {str(e)}"
        )

@app.post("/analizar", 
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
    analysis_id = f"analysis_{request.id_contenido}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting content analysis",
            content_id=request.id_contenido,
            content_type=request.tipo_contenido,
            analysis_level=request.nivel_analisis,
            analysis_id=analysis_id
        )
        
        # Sanitizar contenido sensible
        sanitized_content = sanitizer.sanitize(request.contenido)
        
        # Obtener prompt según el tipo de contenido
        if request.tipo_contenido == "test_case":
            prompt = prompt_templates.get_analysis_prompt(
                test_case_content=sanitized_content,
                project_key="",  # Ya no requerido
                priority="",     # Ya no requerido
                labels=[]        # Ya no requerido
            )
        elif request.tipo_contenido == "requirement":
            prompt = prompt_templates.get_requirements_analysis_prompt(
                requirement_content=sanitized_content,
                project_key="",  # Ya no requerido
                priority="",     # Ya no requerido
                test_types=["functional", "integration"],  # Valores por defecto
                coverage_level=request.nivel_analisis
            )
        else:  # user_story
            prompt = prompt_templates.get_requirements_analysis_prompt(
                requirement_content=sanitized_content,
                project_key="",  # Ya no requerido
                priority="",     # Ya no requerido
                test_types=["functional", "integration"],  # Valores por defecto
                coverage_level=request.nivel_analisis
            )
        
        # Ejecutar análisis con LLM
        if request.tipo_contenido == "test_case":
            analysis_result = await llm_wrapper.analyze_test_case(
                prompt=prompt,
                test_case_id=request.id_contenido,
                analysis_id=analysis_id
            )
        else:
            analysis_result = await llm_wrapper.analyze_requirements(
                prompt=prompt,
                requirement_id=request.id_contenido,
                analysis_id=analysis_id
            )
        
        # Procesar casos de prueba generados
        test_cases = []
        if analysis_result.get("test_cases"):
            for tc_data in analysis_result["test_cases"]:
                test_case = TestCase(
                    id_caso_prueba=tc_data.get("test_case_id", f"TC-{request.id_contenido}-001"),
                    titulo=tc_data.get("title", ""),
                    descripcion=tc_data.get("description", ""),
                    tipo_prueba=tc_data.get("test_type", "functional"),
                    prioridad=tc_data.get("priority", "medium"),
                    pasos=tc_data.get("steps", []),
                    resultado_esperado=tc_data.get("expected_result", ""),
                    precondiciones=tc_data.get("preconditions", []),
                    datos_prueba=tc_data.get("test_data", {}),
                    potencial_automatizacion=tc_data.get("automation_potential", "medium"),
                    duracion_estimada=tc_data.get("estimated_duration", "5-10 minutes")
                )
                test_cases.append(test_case)
        
        # Procesar sugerencias (solo para casos de prueba existentes)
        suggestions = []
        if request.tipo_contenido == "test_case" and analysis_result.get("suggestions"):
            for suggestion in analysis_result["suggestions"]:
                suggestions.append({
                    "tipo": suggestion.get("type", "general"),
                    "titulo": suggestion.get("title", ""),
                    "descripcion": suggestion.get("description", ""),
                    "prioridad": suggestion.get("priority", "medium"),
                    "categoria": suggestion.get("category", "improvement")
                })
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = AnalysisResponse(
            id_contenido=request.id_contenido,
            id_analisis=analysis_id,
            estado="completed",
            casos_prueba=test_cases,
            sugerencias=suggestions,
            analisis_cobertura=analysis_result.get("coverage_analysis", {}),
            puntuacion_confianza=analysis_result.get("confidence_score", 0.8),
            tiempo_procesamiento=processing_time,
            fecha_creacion=start_time
        )
        
        # Registrar en background task para tracking
        background_tasks.add_task(
            log_analysis_completion,
            analysis_id,
            request.id_contenido,
            response
        )
        
        logger.info(
            "Content analysis completed",
            content_id=request.id_contenido,
            content_type=request.tipo_contenido,
            analysis_id=analysis_id,
            test_cases_count=len(test_cases),
            suggestions_count=len(suggestions),
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Content analysis failed",
            content_id=request.id_contenido,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing content: {str(e)}"
        )

@app.post("/analizar-jira", 
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
    analysis_id = f"jira_analysis_{request.id_work_item.replace('-', '')}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting Jira work item analysis",
            work_item_id=request.id_work_item,
            analysis_level=request.nivel_analisis,
            analysis_id=analysis_id
        )
        
        # Obtener datos del work item desde Jira (sin project_key requerido)
        jira_data = await tracker_client.get_work_item_details(
            work_item_id=request.id_work_item,
            project_key=""  # Se detecta automáticamente del id_work_item
        )
        
        if not jira_data:
            raise HTTPException(
                status_code=404,
                detail=f"Work item {request.id_work_item} not found"
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
            coverage_level=request.nivel_analisis
        )
        
        # Ejecutar análisis con LLM
        analysis_result = await llm_wrapper.analyze_jira_workitem(
            prompt=prompt,
            work_item_id=request.id_work_item,
            analysis_id=analysis_id
        )
        
        # Procesar casos de prueba generados
        test_cases = []
        if analysis_result.get("test_cases"):
            for tc_data in analysis_result["test_cases"]:
                test_case = TestCase(
                    id_caso_prueba=tc_data.get("test_case_id", f"TC-{request.id_work_item}-001"),
                    titulo=tc_data.get("title", ""),
                    descripcion=tc_data.get("description", ""),
                    tipo_prueba=tc_data.get("test_type", "functional"),
                    prioridad=tc_data.get("priority", "medium"),
                    pasos=tc_data.get("steps", []),
                    resultado_esperado=tc_data.get("expected_result", ""),
                    precondiciones=tc_data.get("preconditions", []),
                    datos_prueba=tc_data.get("test_data", {}),
                    potencial_automatizacion=tc_data.get("automation_potential", "medium"),
                    duracion_estimada=tc_data.get("estimated_duration", "5-10 minutes")
                )
                test_cases.append(test_case)
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = JiraAnalysisResponse(
            id_work_item=request.id_work_item,
            datos_jira=jira_data,
            id_analisis=analysis_id,
            estado="completed",
            casos_prueba=test_cases,
            analisis_cobertura=analysis_result.get("coverage_analysis", {}),
            puntuacion_confianza=analysis_result.get("confidence_score", 0.8),
            tiempo_procesamiento=processing_time,
            fecha_creacion=start_time
        )
        
        # Registrar en background task para tracking
        background_tasks.add_task(
            log_jira_workitem_analysis_completion,
            analysis_id,
            request.id_work_item,
            response
        )
        
        logger.info(
            "Jira work item analysis completed",
            work_item_id=request.id_work_item,
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
            work_item_id=request.id_work_item,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing Jira work item: {str(e)}"
        )

@app.post("/generar-pruebas-avanzadas", 
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
    
    ### Formato de Salida:
    - **test_cases**: Lista de casos de prueba con estructura estandarizada
    - **coverage_analysis**: Análisis de cobertura por tipo de prueba
    - **confidence_score**: Puntuación de confianza (0-1)
    - **processing_time**: Tiempo de procesamiento en segundos
    
    ### Respuesta:
    - **test_cases**: Lista de casos de prueba generados
    - **coverage_analysis**: Análisis de cobertura de pruebas
    - **confidence_score**: Puntuación de confianza (0-1)
    - **processing_time**: Tiempo de procesamiento en segundos
    """
    start_time = datetime.utcnow()
    generation_id = f"advanced_{request.aplicacion}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting advanced test case generation",
            aplicacion=request.aplicacion,
            generation_id=generation_id
        )
        
        # Verificar que el modelo esté configurado
        if not llm_wrapper.model:
            raise HTTPException(
                status_code=503,
                detail="AI model not configured. Please check GOOGLE_API_KEY environment variable."
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
            for tc_data in analysis_result["test_cases"]:
                test_case = TestCase(
                    id_caso_prueba=tc_data.get("test_case_id", f"CP-001-{request.aplicacion}-MODULO-DATO-CONDICION-RESULTADO"),
                    titulo=tc_data.get("title", f"CP - 001 - {request.aplicacion} - MODULO - DATO - CONDICION - RESULTADO"),
                    descripcion=tc_data.get("description", ""),
                    tipo_prueba=tc_data.get("test_type", "functional"),
                    prioridad=tc_data.get("priority", "high"),
                    pasos=tc_data.get("steps", []),
                    resultado_esperado=tc_data.get("expected_result", "Resultado Esperado: [Descripción específica]"),
                    precondiciones=tc_data.get("preconditions", ["Precondicion: [Descripción específica]"]),
                    datos_prueba=tc_data.get("test_data", {}),
                    potencial_automatizacion=tc_data.get("automation_potential", "high"),
                    duracion_estimada=tc_data.get("estimated_duration", "5-10 minutes")
                )
                test_cases.append(test_case)
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = AdvancedTestGenerationResponse(
            aplicacion=request.aplicacion,
            id_generacion=generation_id,
            estado="completed",
            casos_prueba=test_cases,
            analisis_cobertura=analysis_result.get("coverage_analysis", {}),
            puntuacion_confianza=analysis_result.get("confidence_score", 0.8),
            tiempo_procesamiento=processing_time,
            fecha_creacion=start_time
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

@app.post("/analisis/requisitos/verificacion-istqb", 
          response_model=ISTQBAnalysisResponse,
          summary="Análisis estático de requisitos ISTQB",
          description="Evalúa la calidad de un requerimiento siguiendo estándares ISTQB Foundation Level v4.0",
          tags=["Análisis ISTQB"],
          responses={
              200: {
                  "description": "Análisis ISTQB completado exitosamente",
                  "model": ISTQBAnalysisResponse
              },
              400: {
                  "description": "JSON inválido o requirement_text vacío",
                  "content": {
                      "application/json": {
                          "example": {"detail": "requirement_text debe tener al menos 30 caracteres"}
                      }
                  }
              },
              422: {
                  "description": "Texto ilegible (idioma no soportado)",
                  "content": {
                      "application/json": {
                          "example": {"detail": "El texto del requerimiento no es legible o está en un idioma no soportado"}
                      }
                  }
              },
              500: {
                  "description": "Error interno del analizador",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Error interno del servidor"}
                      }
                  }
              }
          })
async def analyze_requirement_istqb(
    request: RequirementInput,
    background_tasks: BackgroundTasks
):
    """
    ## Análisis Estático de Requisitos ISTQB
    
    Evalúa la calidad de un requerimiento siguiendo estándares ISTQB Foundation Level v4.0.
    Detecta ambigüedades, malas prácticas y riesgos en requerimientos escritos en lenguaje natural.
    
    ### Proceso de Análisis:
    1. **Validación Automática**: Se aplican criterios automáticos de calidad
    2. **Análisis IA**: Se procesa con Google Gemini usando prompts especializados ISTQB
    3. **Detección de Issues**: Se identifican problemas según heurísticas ISTQB
    4. **Evaluación de Riesgo**: Se asigna severidad y probabilidad a cada hallazgo
    5. **Generación de Criterios**: Se crean criterios de aceptación SMART
    6. **Propuesta de Mejora**: Se genera versión limpia del requerimiento
    
    ### Criterios de Evaluación:
    - **Claridad**: No ambiguo, términos específicos
    - **Completitud**: Entradas, salidas, reglas, restricciones, NFR
    - **Consistencia**: Sin contradicciones internas/externas
    - **Factibilidad**: Técnica y operativamente viable
    - **Testabilidad**: Criterios de aceptación medibles
    
    ### Heurísticas de Ambigüedad Detectadas:
    - Términos vagos: rápido, fácil, robusto, óptimo
    - Cuantificadores difusos: algunos, varios, suficiente
    - Rangos abiertos: <, >, alrededor de, aproximadamente
    - Pronombres sin antecedente: esto, eso, ellos
    - Voz pasiva sin responsable: se realizará, será procesado
    - Deixis temporal/espacial: pronto, en breve, más adelante
    
    ### Respuesta:
    - **quality_score**: Puntuación de calidad por dimensión (0-100)
    - **issues**: Lista de issues detectados con riesgo y correcciones
    - **coverage**: Análisis de cobertura de elementos del requerimiento
    - **acceptance_criteria**: Criterios de aceptación SMART generados
    - **proposed_clean_version**: Versión limpia y testeable del requerimiento
    """
    start_time = datetime.utcnow()
    analysis_id = f"istqb_{request.requirement_id}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting ISTQB requirement analysis",
            requirement_id=request.requirement_id,
            analysis_id=analysis_id
        )
        
        # Validaciones automáticas según criterios ISTQB
        validation_issues = _validate_requirement_automatically(request.requirement_text)
        
        # Sanitizar contenido sensible
        sanitized_content = sanitizer.sanitize(request.requirement_text)
        
        # Generar prompt para análisis ISTQB
        prompt = _generate_istqb_analysis_prompt(
            requirement_text=sanitized_content,
            context=request.context,
            glossary=request.glossary,
            acceptance_template=request.acceptance_template,
            non_functional_expectations=request.non_functional_expectations
        )
        
        # Ejecutar análisis con LLM
        analysis_result = await llm_wrapper.analyze_requirements(
            prompt=prompt,
            requirement_id=request.requirement_id,
            analysis_id=analysis_id
        )
        
        # Procesar respuesta del LLM y crear estructura ISTQB
        response = _process_istqb_analysis_result(
            analysis_result=analysis_result,
            requirement_id=request.requirement_id,
            analysis_id=analysis_id,
            validation_issues=validation_issues,
            processing_time=(datetime.utcnow() - start_time).total_seconds(),
            created_at=start_time
        )
        
        # Registrar en background task para tracking
        background_tasks.add_task(
            log_istqb_analysis_completion,
            analysis_id,
            request.requirement_id,
            response
        )
        
        logger.info(
            "ISTQB requirement analysis completed",
            requirement_id=request.requirement_id,
            analysis_id=analysis_id,
            issues_count=len(response.issues),
            quality_score=response.quality_score.overall,
            processing_time=response.processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "ISTQB requirement analysis failed",
            requirement_id=request.requirement_id,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing requirement with ISTQB: {str(e)}"
        )

@app.post("/analizar-jira-confluence",
          response_model=ConfluenceTestPlanResponse,
          summary="Analizar issue de Jira y diseñar plan de pruebas para Confluence",
          description="Analiza un issue de Jira y genera un plan de pruebas completo y estructurado para documentar en Confluence",
          tags=["Integración Confluence"],
          responses={
              200: {
                  "description": "Análisis de Jira y diseño de plan de pruebas completado exitosamente",
                  "model": ConfluenceTestPlanResponse
              },
              404: {
                  "description": "Issue de Jira no encontrado",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Issue de Jira no encontrado"}
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
async def analyze_jira_confluence_test_plan(
    request: ConfluenceTestPlanRequest,
    background_tasks: BackgroundTasks
):
    """
    ## Analizar Issue de Jira y Diseñar Plan de Pruebas para Confluence
    
    Analiza un issue específico de Jira y genera un plan de pruebas completo y estructurado para documentar en Confluence.
    
    ### Proceso:
    1. **Obtención de Jira**: Se recupera el issue desde Jira API
    2. **Análisis del Issue**: Se analiza el contenido, criterios de aceptación y contexto
    3. **Diseño del Plan**: Se diseña un plan de pruebas estructurado usando IA
    4. **Formato Confluence**: Se genera contenido optimizado para Confluence
    5. **Casos de Prueba**: Se crean casos de prueba detallados y ejecutables
    
    ### Parámetros Simplificados:
    - **jira_issue_id** (requerido): ID del issue de Jira a analizar
    - **confluence_space_key** (requerido): Espacio de Confluence donde crear el plan
    - **test_plan_title** (opcional): Título personalizado del plan (se genera automáticamente si no se proporciona)
    
    ### Valores por Defecto Inteligentes:
    - **Estrategia**: comprehensive (plan completo con todos los tipos de pruebas)
    - **Automatización**: habilitada (incluye casos de automatización)
    - **Rendimiento**: deshabilitado (no incluye casos de rendimiento por defecto)
    - **Seguridad**: habilitada (incluye casos de seguridad)
    - **Título**: se genera automáticamente basado en el summary del issue de Jira
    
    ### Características del Plan:
    - **Secciones Estructuradas**: Resumen, alcance, estrategia, ejecución, casos, criterios, riesgos, recursos
    - **Fases de Ejecución**: Plan detallado por fases con duraciones y responsables
    - **Casos de Prueba**: Casos estructurados con pasos, resultados esperados y datos de prueba
    - **Formato Confluence**: Contenido optimizado con macros, tablas y elementos visuales
    - **Análisis de Cobertura**: Métricas de cobertura por tipo de prueba
    - **Potencial de Automatización**: Evaluación de casos automatizables
    
    ### Respuesta:
    - **test_plan_sections**: Secciones del plan de pruebas
    - **test_execution_phases**: Fases de ejecución con cronograma
    - **test_cases**: Casos de prueba generados
    - **confluence_content**: Contenido completo en formato Confluence
    - **confluence_markup**: Markup específico para crear la página
    - **coverage_analysis**: Análisis de cobertura de pruebas
    - **automation_potential**: Análisis de potencial de automatización
    """
    start_time = datetime.utcnow()
    analysis_id = f"confluence_plan_{request.id_issue_jira.replace('-', '')}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting Jira-Confluence test plan analysis",
            jira_issue_id=request.id_issue_jira,
            confluence_space_key=request.espacio_confluence,
            test_plan_title=request.titulo_plan_pruebas,
            analysis_id=analysis_id
        )
        
        # Obtener datos del issue desde Jira
        jira_data = await tracker_client.get_work_item_details(
            work_item_id=request.id_issue_jira,
            project_key=""  # Se detecta automáticamente del id_issue_jira
        )
        
        if not jira_data:
            raise HTTPException(
                status_code=404,
                detail=f"Issue de Jira {request.id_issue_jira} not found"
            )
        
        # Generar título del plan si no se proporciona
        if not request.titulo_plan_pruebas:
            request.titulo_plan_pruebas = f"Plan de Pruebas - {jira_data.get('summary', request.id_issue_jira)}"
        
        # Sanitizar contenido sensible
        sanitized_jira_data = sanitizer.sanitize_dict(jira_data)
        
        # Generar prompt para análisis de Jira y diseño de plan de pruebas con valores por defecto inteligentes
        prompt = prompt_templates.get_confluence_test_plan_prompt(
            jira_data=sanitized_jira_data,
            test_plan_title=request.titulo_plan_pruebas,
            test_strategy="comprehensive",  # Valor por defecto
            include_automation=True,  # Valor por defecto
            include_performance=False,  # Valor por defecto
            include_security=True,  # Valor por defecto
            confluence_space_key=request.espacio_confluence
        )
        
        # Ejecutar análisis con LLM con timeout extendido
        try:
            analysis_result = await asyncio.wait_for(
                llm_wrapper.analyze_requirements(
                    prompt=prompt,
                    requirement_id=request.id_issue_jira,
                    analysis_id=analysis_id
                ),
                timeout=300.0  # 5 minutos de timeout
            )
        except asyncio.TimeoutError:
            logger.error(
                "LLM analysis timeout",
                jira_issue_id=request.id_issue_jira,
                analysis_id=analysis_id
            )
            raise HTTPException(
                status_code=408,
                detail="El análisis está tardando más de lo esperado. Por favor, intenta con un issue más simple o contacta al administrador."
            )
        
        # Procesar secciones del plan de pruebas
        test_plan_sections = []
        if analysis_result.get("test_plan_sections"):
            for section_data in analysis_result["test_plan_sections"]:
                section = TestPlanSection(
                    id_seccion=section_data.get("section_id", "section"),
                    titulo=section_data.get("title", ""),
                    contenido=section_data.get("content", ""),
                    orden=section_data.get("order", 1)
                )
                test_plan_sections.append(section)
        
        # Procesar fases de ejecución
        test_execution_phases = []
        if analysis_result.get("test_execution_phases"):
            for phase_data in analysis_result["test_execution_phases"]:
                phase = TestExecutionPhase(
                    nombre_fase=phase_data.get("phase_name", ""),
                    duracion=phase_data.get("duration", ""),
                    cantidad_casos_prueba=phase_data.get("test_cases_count", 0),
                    responsable=phase_data.get("responsible", ""),
                    dependencias=phase_data.get("dependencies", [])
                )
                test_execution_phases.append(phase)
        
        # Procesar casos de prueba generados
        test_cases = []
        if analysis_result.get("test_cases"):
            for tc_data in analysis_result["test_cases"]:
                test_case = TestCase(
                    test_case_id=tc_data.get("test_case_id", f"CP-001-{request.jira_issue_id}-001"),
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
        response = ConfluenceTestPlanResponse(
            id_issue_jira=request.id_issue_jira,
            espacio_confluence=request.espacio_confluence,
            titulo_plan_pruebas=request.titulo_plan_pruebas,
            id_analisis=analysis_id,
            estado="completed",
            datos_jira=jira_data,
            secciones_plan_pruebas=test_plan_sections,
            fases_ejecucion=test_execution_phases,
            casos_prueba=test_cases,
            total_casos_prueba=len(test_cases),
            duracion_estimada=analysis_result.get("estimated_duration", "1-2 semanas"),
            nivel_riesgo=analysis_result.get("risk_level", "medium"),
            puntuacion_confianza=analysis_result.get("confidence_score", 0.8),
            contenido_confluence=analysis_result.get("confluence_content", ""),
            markup_confluence=analysis_result.get("confluence_markup", ""),
            analisis_cobertura=analysis_result.get("coverage_analysis", {}),
            potencial_automatizacion=analysis_result.get("automation_potential", {}),
            processing_time=processing_time,
            created_at=start_time
        )
        
        # Registrar en background task para tracking
        background_tasks.add_task(
            log_confluence_test_plan_completion,
            analysis_id,
            request.id_issue_jira,
            response
        )
        
        logger.info(
            "Jira-Confluence test plan analysis completed",
            jira_issue_id=request.id_issue_jira,
            analysis_id=analysis_id,
            test_plan_sections_count=len(test_plan_sections),
            test_execution_phases_count=len(test_execution_phases),
            test_cases_count=len(test_cases),
            processing_time=processing_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Jira-Confluence test plan analysis failed",
            jira_issue_id=request.id_issue_jira,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing Jira issue and designing Confluence test plan: {str(e)}"
        )

# Funciones auxiliares para análisis ISTQB
def _validate_requirement_automatically(requirement_text: str) -> List[Dict[str, Any]]:
    """Validaciones automáticas según criterios ISTQB"""
    issues = []
    
    # Validación de longitud mínima
    if len(requirement_text) < 30:
        issues.append({
            "type": "Omission",
            "heuristic": "MissingInputOutput",
            "excerpt": requirement_text[:50] + "..." if len(requirement_text) > 50 else requirement_text,
            "explanation": "El requerimiento es demasiado corto para ser completo según ISTQB",
            "severity": "High",
            "likelihood": "High",
            "rpn": 15
        })
    
    # Detectar términos vagos
    vague_terms = ["rápido", "fácil", "óptimo", "adecuado", "aprox", "algunos", "varios", "lo antes posible"]
    for term in vague_terms:
        if term.lower() in requirement_text.lower():
            issues.append({
                "type": "Ambiguity",
                "heuristic": "VagueTerm",
                "excerpt": f"término vago: '{term}'",
                "explanation": f"El término '{term}' es ambiguo según ISTQB - debe ser cuantificado",
                "severity": "Medium",
                "likelihood": "High",
                "rpn": 12
            })
    
    # Detectar falta de números en rendimiento
    performance_keywords = ["rendimiento", "capacidad", "tiempo", "velocidad", "procesamiento"]
    has_performance = any(keyword in requirement_text.lower() for keyword in performance_keywords)
    has_numbers = any(char.isdigit() for char in requirement_text)
    
    if has_performance and not has_numbers:
        issues.append({
            "type": "NFRGap",
            "heuristic": "MissingInputOutput",
            "excerpt": "menciona rendimiento sin métricas",
            "explanation": "Se menciona rendimiento pero no se especifican métricas cuantificables",
            "severity": "Medium",
            "likelihood": "Medium",
            "rpn": 9
        })
    
    return issues

def _generate_istqb_analysis_prompt(
    requirement_text: str,
    context: RequirementContext,
    glossary: Dict[str, str],
    acceptance_template: str,
    non_functional_expectations: List[str]
) -> str:
    """Generar prompt especializado para análisis ISTQB"""
    
    glossary_text = ""
    if glossary:
        glossary_text = "\nGlosario de términos:\n"
        for term, definition in glossary.items():
            glossary_text += f"- {term}: {definition}\n"
    
    constraints_text = ""
    if context.constraints:
        constraints_text = "\nRestricciones aplicables:\n"
        for constraint in context.constraints:
            constraints_text += f"- {constraint}\n"
    
    nfr_text = ""
    if non_functional_expectations:
        nfr_text = "\nExpectativas no funcionales:\n"
        for nfr in non_functional_expectations:
            nfr_text += f"- {nfr}\n"
    
    prompt = f"""
Eres un analista de calidad siguiendo ISTQB Foundation Level (v4.0). Tu tarea es evaluar la calidad de un requerimiento escrito en lenguaje natural y detectar ambigüedades, malas prácticas y riesgos. Responde exclusivamente en JSON válido con el esquema indicado.

CONTEXTO DEL REQUERIMIENTO:
- Producto: {context.product}
- Módulo: {context.module}
- Stakeholders: {', '.join(context.stakeholders)}
- Dependencias: {', '.join(context.dependencies)}
{constraints_text}{nfr_text}{glossary_text}

REQUERIMIENTO A ANALIZAR:
{requirement_text}

OBJETIVO:
Determinar si el requerimiento es:
- Claro (no ambiguo)
- Completo (entradas, salidas, reglas, restricciones, NFR)
- Consistente (sin contradicciones internas/externas)
- Factible (técnica y operativamente)
- Verificable/Testeable (criterios de aceptación medibles)

GUÍAS ISTQB A APLICAR:
1. Revisiones estáticas: checklist de defectos de requisitos (ambigüedad, omisiones, inconsistencias, redundancias)
2. Testabilidad: cada criterio debe ser observable, medible y con oráculos definidos
3. Atributos de buena especificación: claro, completo, consistente, correcto, verificable, necesario, rastreable
4. Gestión de riesgo: asigna severidad y probabilidad a cada hallazgo; prioriza lo que afecta a valor, conformidad o seguridad
5. Especificación de datos: define formatos, rangos, unidades, precisión, codificaciones, reglas de negocio
6. NFR (desempeño, seguridad, usabilidad, compatibilidad, confiabilidad, mantenibilidad, portabilidad): identificar si faltan o son vagos

HEURÍSTICAS DE AMBIGÜEDAD (marcar si aparecen):
- Términos vagos: rápido, fácil, robusto, óptimo, adecuado, pronto
- Cuantificadores difusos: algunos, varios, suficiente, mínimo necesario
- Rango abierto o sin umbrales: <, >, alrededor de, aproximadamente
- Pronombres sin antecedente: esto, eso, ellos
- Pasiva sin responsable: se realizará, será procesado
- Deixis temporal/espacial: pronto, en breve, más adelante
- Omisiones: entradas/salidas, errores, estados, roles/responsables
- Reglas de negocio implícitas o externas no citadas
- Criterios de aceptación no SMART

RESPONDE EN JSON CON ESTA ESTRUCTURA EXACTA:
{{
  "requirement_id": "REQ-123",
  "quality_score": {{
    "overall": 0-100,
    "clarity": 0-100,
    "completeness": 0-100,
    "consistency": 0-100,
    "feasibility": 0-100,
    "testability": 0-100
  }},
  "issues": [
    {{
      "id": "ISS-001",
      "type": "Ambiguity|Omission|Inconsistency|NFRGap|DataSpecGap|ResponsibilityGap|RuleConflict",
      "heuristic": "VagueTerm|FuzzyQuantifier|OpenRange|PronounWithoutAntecedent|PassiveVoice|TemporalDeixis|MissingInputOutput|MissingErrorHandling|UndefinedRole|ImplicitBusinessRule",
      "excerpt": "texto exacto/fragmento",
      "explanation": "por qué es un problema según ISTQB",
      "impact_area": ["Value","Compliance","Security","Performance","UX","Operability","Testability"],
      "risk": {{
        "severity": "Low|Medium|High|Critical",
        "likelihood": "Low|Medium|High",
        "rpn": 1-27
      }},
      "fix_suggestion": "recomendación concreta",
      "proposed_rewrite": "versión reescrita, clara y testeable"
    }}
  ],
  "coverage": {{
    "inputs_defined": true/false,
    "outputs_defined": true/false,
    "business_rules": ["BR-..."],
    "error_handling_defined": true/false,
    "roles_responsibilities_defined": true/false,
    "data_contracts_defined": true/false,
    "nfr_defined": ["performance","security","usability", "..."]
  }},
  "acceptance_criteria": [
    {{
      "id": "AC-1",
      "format": "GWT|Checklist",
      "criterion": "Dado ... Cuando ... Entonces ...",
      "measurable": true/false,
      "test_oracle": "cómo verificar/medir",
      "example_data": {{"input":"...","expected":"..."}}
    }}
  ],
  "traceability": {{
    "glossary_terms_used": ["..."],
    "external_refs_needed": ["norma/regla/código"],
    "dependencies_touched": ["API Clientes v2"]
  }},
  "summary": "resumen ejecutivo en 3-4 líneas con prioridad de corrección",
  "proposed_clean_version": "Requerimiento completo, claro, consistente y testeable (versión final sugerida)."
}}

REGLAS DE EVALUACIÓN Y REESCRITURA:
- Si detectas un término vago, sustitúyelo por un umbral/valor/SLI (p.ej., "rápido" → "p95 ≤ 300 ms en 24h")
- Toda condición debe tener datos de ejemplo, precondiciones y oráculo
- Explicita roles/responsables (quién ejecuta/consume/autoriza)
- Define formatos y rangos (ej.: monto: decimal(12,2), moneda=PYG, rango 0–50,000,000)
- Añade manejo de errores y mensajes (códigos, causas, acciones)
- Criterios de aceptación SMART; si faltan, propón 2–5 AC
- Marca contradicciones internas/externas con explicación y resolución
- Prioriza correcciones según riesgo (RPN)

NOTAS DE ESTILO:
- No incluyas texto fuera del JSON
- Usa excerpt literalmente del requerimiento original
- proposed_rewrite debe quedar lista para pasar a diseño y pruebas
"""
    
    return prompt

def _process_istqb_analysis_result(
    analysis_result: Dict[str, Any],
    requirement_id: str,
    analysis_id: str,
    validation_issues: List[Dict[str, Any]],
    processing_time: float,
    created_at: datetime
) -> ISTQBAnalysisResponse:
    """Procesar resultado del análisis ISTQB y crear respuesta estructurada"""
    
    # Extraer datos del resultado del LLM
    quality_score_data = analysis_result.get("quality_score", {})
    issues_data = analysis_result.get("issues", [])
    coverage_data = analysis_result.get("coverage", {})
    acceptance_criteria_data = analysis_result.get("acceptance_criteria", [])
    traceability_data = analysis_result.get("traceability", {})
    
    # Crear QualityScore
    quality_score = QualityScore(
        overall=quality_score_data.get("overall", 50),
        clarity=quality_score_data.get("clarity", 50),
        completeness=quality_score_data.get("completeness", 50),
        consistency=quality_score_data.get("consistency", 50),
        feasibility=quality_score_data.get("feasibility", 50),
        testability=quality_score_data.get("testability", 50)
    )
    
    # Procesar issues (combinar con validaciones automáticas)
    all_issues = []
    
    # Agregar issues de validación automática
    for i, issue in enumerate(validation_issues):
        all_issues.append(RequirementIssue(
            id=f"ISS-AUTO-{i+1:03d}",
            type=issue["type"],
            heuristic=issue["heuristic"],
            excerpt=issue["excerpt"],
            explanation=issue["explanation"],
            impact_area=["Testability"],
            risk=IssueRisk(
                severity=issue["severity"],
                likelihood=issue["likelihood"],
                rpn=issue["rpn"]
            ),
            fix_suggestion="Revisar y completar el requerimiento según estándares ISTQB",
            proposed_rewrite="[Requiere reescritura completa del requerimiento]"
        ))
    
    # Agregar issues del LLM
    for issue_data in issues_data:
        all_issues.append(RequirementIssue(
            id=issue_data.get("id", f"ISS-{len(all_issues)+1:03d}"),
            type=issue_data.get("type", "Ambiguity"),
            heuristic=issue_data.get("heuristic", "VagueTerm"),
            excerpt=issue_data.get("excerpt", ""),
            explanation=issue_data.get("explanation", ""),
            impact_area=issue_data.get("impact_area", ["Testability"]),
            risk=IssueRisk(
                severity=issue_data.get("risk", {}).get("severity", "Medium"),
                likelihood=issue_data.get("risk", {}).get("likelihood", "Medium"),
                rpn=issue_data.get("risk", {}).get("rpn", 9)
            ),
            fix_suggestion=issue_data.get("fix_suggestion", ""),
            proposed_rewrite=issue_data.get("proposed_rewrite", "")
        ))
    
    # Crear CoverageAnalysis
    coverage = CoverageAnalysis(
        inputs_defined=coverage_data.get("inputs_defined", False),
        outputs_defined=coverage_data.get("outputs_defined", False),
        business_rules=coverage_data.get("business_rules", []),
        error_handling_defined=coverage_data.get("error_handling_defined", False),
        roles_responsibilities_defined=coverage_data.get("roles_responsibilities_defined", False),
        data_contracts_defined=coverage_data.get("data_contracts_defined", False),
        nfr_defined=coverage_data.get("nfr_defined", [])
    )
    
    # Procesar criterios de aceptación
    acceptance_criteria = []
    for ac_data in acceptance_criteria_data:
        acceptance_criteria.append(AcceptanceCriterion(
            id=ac_data.get("id", f"AC-{len(acceptance_criteria)+1}"),
            format=ac_data.get("format", "GWT"),
            criterion=ac_data.get("criterion", ""),
            measurable=ac_data.get("measurable", False),
            test_oracle=ac_data.get("test_oracle", ""),
            example_data=ac_data.get("example_data", {})
        ))
    
    # Crear TraceabilityAnalysis
    traceability = TraceabilityAnalysis(
        glossary_terms_used=traceability_data.get("glossary_terms_used", []),
        external_refs_needed=traceability_data.get("external_refs_needed", []),
        dependencies_touched=traceability_data.get("dependencies_touched", [])
    )
    
    # Crear respuesta final
    return ISTQBAnalysisResponse(
        requirement_id=requirement_id,
        quality_score=quality_score,
        issues=all_issues,
        coverage=coverage,
        acceptance_criteria=acceptance_criteria,
        traceability=traceability,
        summary=analysis_result.get("summary", "Análisis completado según estándares ISTQB"),
        proposed_clean_version=analysis_result.get("proposed_clean_version", ""),
        analysis_id=analysis_id,
        processing_time=processing_time,
        created_at=created_at
    )

async def log_istqb_analysis_completion(
    analysis_id: str,
    requirement_id: str,
    response: ISTQBAnalysisResponse
):
    """Background task para registrar la finalización del análisis ISTQB"""
    try:
        logger.info(
            "ISTQB analysis completion logged",
            analysis_id=analysis_id,
            requirement_id=requirement_id,
            issues_count=len(response.issues),
            quality_score=response.quality_score.overall,
            processing_time=response.processing_time
        )
    except Exception as e:
        logger.error(
            "Failed to log ISTQB analysis completion",
            analysis_id=analysis_id,
            error=str(e)
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

async def log_confluence_test_plan_completion(
    analysis_id: str,
    jira_issue_id: str,
    response: ConfluenceTestPlanResponse
):
    """Background task para registrar la finalización del análisis de Confluence"""
    try:
        # Aquí podrías implementar lógica adicional como:
        # - Guardar en base de datos
        # - Enviar notificaciones
        # - Actualizar métricas
        # - Crear página en Confluence
        # - Enviar notificaciones a stakeholders
        logger.info(
            "Confluence test plan analysis completion logged",
            analysis_id=analysis_id,
            jira_issue_id=jira_issue_id,
            test_plan_sections_count=len(response.test_plan_sections),
            test_execution_phases_count=len(response.test_execution_phases),
            test_cases_count=len(response.test_cases),
            confluence_space_key=response.confluence_space_key,
            processing_time=response.processing_time
        )
    except Exception as e:
        logger.error(
            "Failed to log Confluence test plan analysis completion",
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
