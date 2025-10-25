"""
Endpoints de Confluence - Versión Simplificada
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
class ConfluenceTestPlanRequest(BaseModel):
    """Request unificado que soporta parámetros en inglés y español"""
    
    # Parámetros en inglés (por defecto)
    jira_issue_id: Optional[str] = Field(None, description="ID of the Jira issue")
    confluence_space_key: Optional[str] = Field(None, description="Confluence space key")
    test_plan_title: Optional[str] = Field(None, description="Test plan title")
    
    # Parámetros en español (alternativos)
    id_issue_jira: Optional[str] = Field(None, description="ID del issue de Jira")
    espacio_confluence: Optional[str] = Field(None, description="Clave del espacio de Confluence")
    titulo_plan_pruebas: Optional[str] = Field(None, description="Título del plan de pruebas")
    
    def get_jira_issue_id(self) -> str:
        """Obtiene el jira_issue_id según el feature flag"""
        if USE_SPANISH_PARAMS and self.id_issue_jira:
            return self.id_issue_jira
        return self.jira_issue_id or ""
    
    def get_confluence_space_key(self) -> str:
        """Obtiene el confluence_space_key según el feature flag"""
        if USE_SPANISH_PARAMS and self.espacio_confluence:
            return self.espacio_confluence
        return self.confluence_space_key or ""
    
    def get_test_plan_title(self) -> str:
        """Obtiene el test_plan_title según el feature flag"""
        if USE_SPANISH_PARAMS and self.titulo_plan_pruebas:
            return self.titulo_plan_pruebas
        return self.test_plan_title or ""
    
    def validate(self):
        """Valida que al menos un conjunto de parámetros esté presente"""
        jira_issue_id = self.get_jira_issue_id()
        confluence_space_key = self.get_confluence_space_key()
        
        if not jira_issue_id:
            raise ValueError("jira_issue_id or id_issue_jira is required")
        if not confluence_space_key:
            raise ValueError("confluence_space_key or espacio_confluence is required")
        return True

# Función helper para extraer parámetros
def get_confluence_params(request: ConfluenceTestPlanRequest) -> tuple[str, str, str]:
    """Extrae parámetros de Confluence según el feature flag"""
    request.validate()
    return (
        request.get_jira_issue_id(),
        request.get_confluence_space_key(),
        request.get_test_plan_title()
    )

# Función principal de análisis de Jira-Confluence
async def analyze_jira_confluence(
    request: ConfluenceTestPlanRequest,
    tracker_client,
    llm_wrapper,
    prompt_templates,
    sanitizer,
    background_tasks
):
    """
    Análisis principal de Jira-Confluence
    Soporta tanto parámetros en inglés como en español
    """
    # Extraer parámetros según feature flag
    jira_issue_id, confluence_space_key, test_plan_title = get_confluence_params(request)
    
    start_time = datetime.utcnow()
    analysis_id = f"confluence_{jira_issue_id.replace('-', '')}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting Jira-Confluence test plan analysis",
            jira_issue_id=jira_issue_id,
            confluence_space_key=confluence_space_key,
            test_plan_title=test_plan_title,
            analysis_id=analysis_id,
            use_spanish_params=USE_SPANISH_PARAMS
        )
        
        # Obtener datos del issue desde Jira
        jira_data = await tracker_client.get_work_item_details(
            work_item_id=jira_issue_id,
            project_key=""
        )
        
        if not jira_data:
            raise HTTPException(
                status_code=404,
                detail=f"Issue de Jira {jira_issue_id} not found"
            )
        
        # Generar título del plan si no se proporciona
        if not test_plan_title:
            test_plan_title = f"Plan de Pruebas - {jira_data.get('summary', jira_issue_id)}"
        
        # Sanitizar contenido sensible
        sanitized_jira_data = sanitizer.sanitize_dict(jira_data)
        
        # Generar prompt para análisis de Confluence
        prompt = prompt_templates.get_confluence_test_plan_prompt(
            jira_data=sanitized_jira_data,
            confluence_space_key=confluence_space_key,
            test_plan_title=test_plan_title,
            test_strategy="comprehensive",
            include_automation=True,
            include_performance=False,
            include_security=True
        )
        
        # Ejecutar análisis con LLM con timeout
        try:
            analysis_result = await asyncio.wait_for(
                llm_wrapper.analyze_requirements(
                    prompt=prompt,
                    requirement_id=jira_issue_id,
                    analysis_id=analysis_id
                ),
                timeout=300.0  # 5 minutos de timeout
            )
        except asyncio.TimeoutError:
            logger.error(
                "LLM analysis timeout",
                jira_issue_id=jira_issue_id,
                analysis_id=analysis_id
            )
            raise HTTPException(
                status_code=408,
                detail="El análisis está tardando más de lo esperado. Por favor, intenta con un issue más simple o contacta al administrador."
            )
        
        # Procesar casos de prueba
        test_cases = []
        if analysis_result.get("test_cases"):
            for i, tc_data in enumerate(analysis_result["test_cases"], 1):
                test_case = {
                    "id_caso_prueba": tc_data.get("test_case_id", f"TC-{jira_issue_id}-{i:03d}"),
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
        
        # Crear secciones del plan
        test_plan_sections = [
            {
                "id_seccion": "resumen",
                "titulo": "Resumen del Plan",
                "contenido": f"Plan de pruebas para {test_plan_title}",
                "orden": 1
            },
            {
                "id_seccion": "casos",
                "titulo": "Casos de Prueba",
                "contenido": f"Se han generado {len(test_cases)} casos de prueba",
                "orden": 2
            }
        ]
        
        # Crear fases de ejecución
        test_execution_phases = [
            {
                "nombre_fase": "Fase 1: Ejecución Principal",
                "duracion": "2-3 días",
                "cantidad_casos_prueba": len(test_cases),
                "responsable": "Equipo QA",
                "dependencias": []
            }
        ]
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = {
            "id_issue_jira": jira_issue_id,
            "espacio_confluence": confluence_space_key,
            "titulo_plan_pruebas": test_plan_title,
            "id_analisis": analysis_id,
            "estado": "completed",
            "datos_jira": jira_data,
            "secciones_plan_pruebas": test_plan_sections,
            "fases_ejecucion": test_execution_phases,
            "casos_prueba": test_cases,
            "total_casos_prueba": len(test_cases),
            "duracion_estimada": "2-3 días",
            "nivel_riesgo": "medio",
            "puntuacion_confianza": analysis_result.get("confidence_score", 0.8),
            "contenido_confluence": analysis_result.get("confluence_content", "Contenido generado"),
            "markup_confluence": analysis_result.get("confluence_content", "Contenido generado"),
            "analisis_cobertura": analysis_result.get("coverage_analysis", {"funcional": "85%"}),
            "potencial_automatizacion": {
                "total_casos": len(test_cases),
                "automatizables": len(test_cases) // 2,
                "porcentaje": "50%"
            },
            "processing_time": processing_time,
            "created_at": start_time.isoformat()
        }
        
        logger.info(
            "Jira-Confluence test plan analysis completed",
            jira_issue_id=jira_issue_id,
            analysis_id=analysis_id,
            test_cases_count=len(test_cases),
            processing_time=processing_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Jira-Confluence test plan analysis failed",
            jira_issue_id=jira_issue_id,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing Jira issue and designing Confluence test plan: {str(e)}"
        )

# Función para análisis simplificado de Confluence
async def analyze_jira_confluence_simple(
    request: ConfluenceTestPlanRequest,
    tracker_client,
    llm_wrapper,
    sanitizer,
    background_tasks
):
    """
    Análisis simplificado de Jira-Confluence
    Versión más rápida con prompt simplificado
    """
    # Extraer parámetros según feature flag
    jira_issue_id, confluence_space_key, test_plan_title = get_confluence_params(request)
    
    start_time = datetime.utcnow()
    analysis_id = f"confluence_simple_{jira_issue_id.replace('-', '')}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting simplified Jira-Confluence test plan analysis",
            jira_issue_id=jira_issue_id,
            confluence_space_key=confluence_space_key,
            test_plan_title=test_plan_title,
            analysis_id=analysis_id,
            use_spanish_params=USE_SPANISH_PARAMS
        )
        
        # Obtener datos del issue desde Jira
        jira_data = await tracker_client.get_work_item_details(
            work_item_id=jira_issue_id,
            project_key=""
        )
        
        if not jira_data:
            raise HTTPException(
                status_code=404,
                detail=f"Issue de Jira {jira_issue_id} not found"
            )
        
        # Generar título del plan si no se proporciona
        if not test_plan_title:
            test_plan_title = f"Plan de Pruebas - {jira_data.get('summary', jira_issue_id)}"
        
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
                    requirement_id=jira_issue_id,
                    analysis_id=analysis_id
                ),
                timeout=120.0  # 2 minutos de timeout
            )
        except asyncio.TimeoutError:
            logger.error(
                "LLM analysis timeout (simplified)",
                jira_issue_id=jira_issue_id,
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
                test_case = {
                    "id_caso_prueba": tc_data.get("test_case_id", f"TC-{jira_issue_id}-{i:03d}"),
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
        
        # Crear secciones básicas del plan
        test_plan_sections = [
            {
                "id_seccion": "resumen",
                "titulo": "Resumen del Plan",
                "contenido": f"Plan de pruebas básico para {test_plan_title}",
                "orden": 1
            },
            {
                "id_seccion": "casos",
                "titulo": "Casos de Prueba",
                "contenido": f"Se han generado {len(test_cases)} casos de prueba básicos",
                "orden": 2
            }
        ]
        
        # Crear fases básicas
        test_execution_phases = [
            {
                "nombre_fase": "Fase 1: Ejecución Básica",
                "duracion": "1-2 días",
                "cantidad_casos_prueba": len(test_cases),
                "responsable": "Equipo QA",
                "dependencias": []
            }
        ]
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta simplificada
        response = {
            "id_issue_jira": jira_issue_id,
            "espacio_confluence": confluence_space_key,
            "titulo_plan_pruebas": test_plan_title,
            "id_analisis": analysis_id,
            "estado": "completed",
            "datos_jira": jira_data,
            "secciones_plan_pruebas": test_plan_sections,
            "fases_ejecucion": test_execution_phases,
            "casos_prueba": test_cases,
            "total_casos_prueba": len(test_cases),
            "duracion_estimada": "1-2 días",
            "nivel_riesgo": "bajo",
            "puntuacion_confianza": 0.7,
            "contenido_confluence": analysis_result.get("confluence_content", "Contenido básico generado"),
            "markup_confluence": analysis_result.get("confluence_content", "Contenido básico generado"),
            "analisis_cobertura": {"funcional": "80%"},
            "potencial_automatizacion": {
                "total_casos": len(test_cases),
                "automatizables": len(test_cases) // 2,
                "porcentaje": "50%"
            },
            "processing_time": processing_time,
            "created_at": start_time.isoformat()
        }
        
        logger.info(
            "Simplified Jira-Confluence test plan analysis completed",
            jira_issue_id=jira_issue_id,
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
            jira_issue_id=jira_issue_id,
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis simplificado: {str(e)}"
        )
