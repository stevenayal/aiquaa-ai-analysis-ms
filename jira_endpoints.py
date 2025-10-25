"""
Endpoints de Jira - Versión Simplificada
Maneja tanto parámetros en inglés como en español con feature flag
"""

import os
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import structlog
from fastapi import HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Feature flags
USE_SPANISH_PARAMS = os.getenv("USE_SPANISH_PARAMS", "false").lower() == "true"

logger = structlog.get_logger()

# Modelo unificado que soporta ambos tipos de parámetros
class JiraAnalysisRequest(BaseModel):
    """Request unificado que soporta parámetros en inglés y español"""
    
    # Parámetros en inglés (por defecto)
    work_item_id: Optional[str] = Field(None, description="ID of the work item in Jira")
    analysis_level: Optional[str] = Field("medium", description="Analysis level")
    
    # Parámetros en español (alternativos)
    id_work_item: Optional[str] = Field(None, description="ID del work item en Jira")
    nivel_analisis: Optional[str] = Field(None, description="Nivel de análisis")
    
    def get_work_item_id(self) -> str:
        """Obtiene el work_item_id según el feature flag"""
        if USE_SPANISH_PARAMS and self.id_work_item:
            return self.id_work_item
        return self.work_item_id or ""
    
    def get_analysis_level(self) -> str:
        """Obtiene el analysis_level según el feature flag"""
        if USE_SPANISH_PARAMS and self.nivel_analisis:
            return self.nivel_analisis
        return self.analysis_level or "medium"
    
    def validate(self):
        """Valida que al menos un conjunto de parámetros esté presente"""
        work_item_id = self.get_work_item_id()
        if not work_item_id:
            raise ValueError("work_item_id or id_work_item is required")
        return True

# Función helper para extraer parámetros
def get_jira_params(request: JiraAnalysisRequest) -> tuple[str, str]:
    """Extrae parámetros de Jira según el feature flag"""
    request.validate()
    return request.get_work_item_id(), request.get_analysis_level()

# Función principal de análisis de Jira
async def analyze_jira_workitem(
    request: JiraAnalysisRequest,
    tracker_client,
    llm_wrapper,
    prompt_templates,
    sanitizer,
    background_tasks
):
    """
    Análisis principal de work item de Jira
    Soporta tanto parámetros en inglés como en español
    """
    # Extraer parámetros según feature flag
    work_item_id, analysis_level = get_jira_params(request)
    
    start_time = datetime.utcnow()
    analysis_id = f"jira_analysis_{work_item_id.replace('-', '')}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting Jira work item analysis",
            work_item_id=work_item_id,
            analysis_level=analysis_level,
            analysis_id=analysis_id,
            use_spanish_params=USE_SPANISH_PARAMS
        )
        
        # Obtener datos del work item desde Jira
        jira_data = await tracker_client.get_work_item_details(
            work_item_id=work_item_id,
            project_key=""
        )
        
        if not jira_data:
            raise HTTPException(
                status_code=404,
                detail=f"Work item {work_item_id} not found"
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
            project_key="",
            test_types=["functional", "integration"],
            coverage_level=analysis_level
        )
        
        # Ejecutar análisis con LLM con timeout
        try:
            analysis_result = await asyncio.wait_for(
                llm_wrapper.analyze_jira_workitem(
                    prompt=prompt,
                    work_item_id=work_item_id,
                    analysis_id=analysis_id
                ),
                timeout=300.0  # 5 minutos de timeout
            )
        except asyncio.TimeoutError:
            logger.error(
                "LLM analysis timeout",
                work_item_id=work_item_id,
                analysis_id=analysis_id
            )
            raise HTTPException(
                status_code=408,
                detail="El análisis está tardando más de lo esperado. Por favor, intenta con un work item más simple o contacta al administrador."
            )
        
        # Procesar casos de prueba generados
        test_cases = []
        if analysis_result.get("test_cases"):
            for tc_data in analysis_result["test_cases"]:
                test_case = {
                    "id_caso_prueba": tc_data.get("test_case_id", f"TC-{work_item_id}-001"),
                    "titulo": tc_data.get("title", ""),
                    "descripcion": tc_data.get("description", ""),
                    "tipo_prueba": tc_data.get("test_type", "functional"),
                    "prioridad": tc_data.get("priority", "medium"),
                    "pasos": tc_data.get("steps", []),
                    "resultado_esperado": tc_data.get("expected_result", ""),
                    "precondiciones": tc_data.get("preconditions", []),
                    "datos_prueba": tc_data.get("test_data", {}),
                    "potencial_automatizacion": tc_data.get("automation_potential", "medium"),
                    "duracion_estimada": tc_data.get("estimated_duration", "5-10 minutes")
                }
                test_cases.append(test_case)
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = {
            "id_work_item": work_item_id,
            "datos_jira": jira_data,
            "id_analisis": analysis_id,
            "estado": "completed",
            "casos_prueba": test_cases,
            "analisis_cobertura": analysis_result.get("coverage_analysis", {}),
            "puntuacion_confianza": analysis_result.get("confidence_score", 0.8),
            "tiempo_procesamiento": processing_time,
            "fecha_creacion": start_time.isoformat()
        }
        
        logger.info(
            "Jira work item analysis completed",
            work_item_id=work_item_id,
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
            work_item_id=work_item_id,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing Jira work item: {str(e)}"
        )

# Función para análisis simplificado
async def analyze_jira_workitem_simple(
    request: JiraAnalysisRequest,
    tracker_client,
    llm_wrapper,
    sanitizer,
    background_tasks
):
    """
    Análisis simplificado de work item de Jira
    Versión más rápida con prompt simplificado
    """
    # Extraer parámetros según feature flag
    work_item_id, analysis_level = get_jira_params(request)
    
    start_time = datetime.utcnow()
    analysis_id = f"jira_simple_{work_item_id.replace('-', '')}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting simplified Jira work item analysis",
            work_item_id=work_item_id,
            analysis_level=analysis_level,
            analysis_id=analysis_id,
            use_spanish_params=USE_SPANISH_PARAMS
        )
        
        # Obtener datos del work item desde Jira
        jira_data = await tracker_client.get_work_item_details(
            work_item_id=work_item_id,
            project_key=""
        )
        
        if not jira_data:
            raise HTTPException(
                status_code=404,
                detail=f"Work item {work_item_id} not found"
            )
        
        # Sanitizar contenido sensible
        sanitized_jira_data = sanitizer.sanitize_dict(jira_data)
        
        # Generar prompt simplificado
        prompt_simple = f"""
        Analiza el siguiente work item de Jira y genera casos de prueba básicos:

        TÍTULO: {sanitized_jira_data.get('summary', '')}
        DESCRIPCIÓN: {sanitized_jira_data.get('description', '')[:300]}...
        TIPO: {sanitized_jira_data.get('issue_type', '')}
        PRIORIDAD: {sanitized_jira_data.get('priority', '')}

        Genera:
        1. 3-5 casos de prueba básicos
        2. Análisis de cobertura simple
        3. Puntuación de confianza

        Responde en formato JSON con: test_cases, coverage_analysis, confidence_score
        """
        
        # Ejecutar análisis con LLM con timeout reducido
        try:
            analysis_result = await asyncio.wait_for(
                llm_wrapper.analyze_jira_workitem(
                    prompt=prompt_simple,
                    work_item_id=work_item_id,
                    analysis_id=analysis_id
                ),
                timeout=120.0  # 2 minutos de timeout
            )
        except asyncio.TimeoutError:
            logger.error(
                "LLM analysis timeout (simplified)",
                work_item_id=work_item_id,
                analysis_id=analysis_id
            )
            raise HTTPException(
                status_code=408,
                detail="El análisis simplificado está tardando más de lo esperado. Por favor, intenta con un work item más simple."
            )
        
        # Procesar casos de prueba básicos
        test_cases = []
        if analysis_result.get("test_cases"):
            for i, tc_data in enumerate(analysis_result["test_cases"][:5], 1):  # Máximo 5 casos
                test_case = {
                    "id_caso_prueba": tc_data.get("test_case_id", f"TC-{work_item_id}-{i:03d}"),
                    "titulo": tc_data.get("title", f"Caso de Prueba {i}"),
                    "descripcion": tc_data.get("description", ""),
                    "pasos": tc_data.get("steps", []),
                    "resultado_esperado": tc_data.get("expected_result", ""),
                    "datos_prueba": tc_data.get("test_data", {}),
                    "tipo_prueba": tc_data.get("test_type", "funcional"),
                    "prioridad": tc_data.get("priority", "media"),
                    "precondiciones": tc_data.get("preconditions", []),
                    "potencial_automatizacion": tc_data.get("automation_potential", "media"),
                    "duracion_estimada": tc_data.get("estimated_duration", "5-10 minutos")
                }
                test_cases.append(test_case)
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta simplificada
        response = {
            "id_work_item": work_item_id,
            "datos_jira": jira_data,
            "id_analisis": analysis_id,
            "estado": "completed",
            "casos_prueba": test_cases,
            "analisis_cobertura": analysis_result.get("coverage_analysis", {"funcional": "80%"}),
            "puntuacion_confianza": analysis_result.get("confidence_score", 0.7),
            "tiempo_procesamiento": processing_time,
            "fecha_creacion": start_time.isoformat()
        }
        
        logger.info(
            "Simplified Jira work item analysis completed",
            work_item_id=work_item_id,
            analysis_id=analysis_id,
            test_cases_count=len(test_cases),
            processing_time=processing_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Simplified Jira work item analysis failed",
            work_item_id=work_item_id,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis simplificado: {str(e)}"
        )
