"""
Endpoints Básicos - Versión Simplificada
Maneja tanto parámetros en inglés como en español con feature flag
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog
from fastapi import HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Feature flags
USE_SPANISH_PARAMS = os.getenv("USE_SPANISH_PARAMS", "false").lower() == "true"

logger = structlog.get_logger()

# Modelo unificado que soporta ambos tipos de parámetros
class AnalysisRequest(BaseModel):
    """Request unificado que soporta parámetros en inglés y español"""
    
    # Parámetros en inglés (por defecto)
    content: Optional[str] = Field(None, description="Content to analyze")
    content_type: Optional[str] = Field("requirement", description="Type of content")
    analysis_level: Optional[str] = Field("medium", description="Analysis level")
    
    # Parámetros en español (alternativos)
    contenido: Optional[str] = Field(None, description="Contenido a analizar")
    tipo_contenido: Optional[str] = Field(None, description="Tipo de contenido")
    nivel_analisis: Optional[str] = Field(None, description="Nivel de análisis")
    
    def get_content(self) -> str:
        """Obtiene el content según el feature flag"""
        if USE_SPANISH_PARAMS and self.contenido:
            return self.contenido
        return self.content or ""
    
    def get_content_type(self) -> str:
        """Obtiene el content_type según el feature flag"""
        if USE_SPANISH_PARAMS and self.tipo_contenido:
            return self.tipo_contenido
        return self.content_type or "requirement"
    
    def get_analysis_level(self) -> str:
        """Obtiene el analysis_level según el feature flag"""
        if USE_SPANISH_PARAMS and self.nivel_analisis:
            return self.nivel_analisis
        return self.analysis_level or "medium"
    
    def validate(self):
        """Valida que al menos un conjunto de parámetros esté presente"""
        content = self.get_content()
        if not content:
            raise ValueError("content or contenido is required")
        return True

# Función helper para extraer parámetros
def get_analysis_params(request: AnalysisRequest) -> tuple[str, str, str]:
    """Extrae parámetros de análisis según el feature flag"""
    request.validate()
    return (
        request.get_content(),
        request.get_content_type(),
        request.get_analysis_level()
    )

# Función principal de análisis básico
async def analyze_content(
    request: AnalysisRequest,
    llm_wrapper,
    prompt_templates,
    sanitizer,
    background_tasks
):
    """
    Análisis principal de contenido
    Soporta tanto parámetros en inglés como en español
    """
    # Extraer parámetros según feature flag
    content, content_type, analysis_level = get_analysis_params(request)
    
    start_time = datetime.utcnow()
    analysis_id = f"analysis_{content_type}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting content analysis",
            content_type=content_type,
            analysis_level=analysis_level,
            analysis_id=analysis_id,
            use_spanish_params=USE_SPANISH_PARAMS
        )
        
        # Sanitizar contenido sensible
        sanitized_content = sanitizer.sanitize(content)
        
        # Generar prompt según el tipo de contenido
        if content_type == "requirement":
            prompt = prompt_templates.get_requirement_analysis_prompt(
                requirement_content=sanitized_content,
                analysis_level=analysis_level
            )
        elif content_type == "test_case":
            prompt = prompt_templates.get_test_case_analysis_prompt(
                test_case_content=sanitized_content,
                analysis_level=analysis_level
            )
        elif content_type == "user_story":
            prompt = prompt_templates.get_user_story_analysis_prompt(
                user_story_content=sanitized_content,
                analysis_level=analysis_level
            )
        else:
            prompt = prompt_templates.get_general_analysis_prompt(
                content=sanitized_content,
                content_type=content_type,
                analysis_level=analysis_level
            )
        
        # Ejecutar análisis con LLM
        try:
            analysis_result = await asyncio.wait_for(
                llm_wrapper.analyze_requirements(
                    prompt=prompt,
                    requirement_id=analysis_id,
                    analysis_id=analysis_id
                ),
                timeout=300.0  # 5 minutos de timeout
            )
        except asyncio.TimeoutError:
            logger.error(
                "LLM analysis timeout",
                analysis_id=analysis_id
            )
            raise HTTPException(
                status_code=408,
                detail="El análisis está tardando más de lo esperado. Por favor, intenta con contenido más simple."
            )
        
        # Procesar casos de prueba generados
        test_cases = []
        if analysis_result.get("test_cases"):
            for i, tc_data in enumerate(analysis_result["test_cases"], 1):
                test_case = {
                    "id_caso_prueba": tc_data.get("test_case_id", f"TC-{analysis_id}-{i:03d}"),
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
        
        # Procesar sugerencias
        suggestions = []
        if analysis_result.get("suggestions"):
            for i, sug_data in enumerate(analysis_result["suggestions"], 1):
                suggestion = {
                    "id_sugerencia": sug_data.get("suggestion_id", f"SUG-{analysis_id}-{i:03d}"),
                    "titulo": sug_data.get("title", f"Sugerencia {i}"),
                    "descripcion": sug_data.get("description", ""),
                    "tipo": sug_data.get("type", "mejora"),
                    "prioridad": sug_data.get("priority", "media"),
                    "impacto": sug_data.get("impact", "medio")
                }
                suggestions.append(suggestion)
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = {
            "id_contenido": analysis_id,
            "tipo_contenido": content_type,
            "estado": "completed",
            "casos_prueba": test_cases,
            "sugerencias": suggestions,
            "analisis_cobertura": analysis_result.get("coverage_analysis", {}),
            "puntuacion_confianza": analysis_result.get("confidence_score", 0.8),
            "tiempo_procesamiento": processing_time,
            "fecha_creacion": start_time.isoformat()
        }
        
        logger.info(
            "Content analysis completed",
            analysis_id=analysis_id,
            test_cases_count=len(test_cases),
            suggestions_count=len(suggestions),
            processing_time=processing_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Content analysis failed",
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing content: {str(e)}"
        )

# Función para análisis avanzado
async def generate_advanced_tests(
    request: AnalysisRequest,
    llm_wrapper,
    prompt_templates,
    sanitizer,
    background_tasks
):
    """
    Generación avanzada de casos de prueba
    Soporta tanto parámetros en inglés como en español
    """
    # Extraer parámetros según feature flag
    content, content_type, analysis_level = get_analysis_params(request)
    
    start_time = datetime.utcnow()
    analysis_id = f"advanced_{content_type}_{int(start_time.timestamp())}"
    
    try:
        logger.info(
            "Starting advanced test generation",
            content_type=content_type,
            analysis_level=analysis_level,
            analysis_id=analysis_id,
            use_spanish_params=USE_SPANISH_PARAMS
        )
        
        # Sanitizar contenido sensible
        sanitized_content = sanitizer.sanitize(content)
        
        # Generar prompt avanzado
        prompt = prompt_templates.get_advanced_test_generation_prompt(
            content=sanitized_content,
            content_type=content_type,
            analysis_level=analysis_level
        )
        
        # Ejecutar análisis con LLM
        try:
            analysis_result = await asyncio.wait_for(
                llm_wrapper.analyze_requirements(
                    prompt=prompt,
                    requirement_id=analysis_id,
                    analysis_id=analysis_id
                ),
                timeout=300.0  # 5 minutos de timeout
            )
        except asyncio.TimeoutError:
            logger.error(
                "LLM analysis timeout",
                analysis_id=analysis_id
            )
            raise HTTPException(
                status_code=408,
                detail="La generación avanzada está tardando más de lo esperado. Por favor, intenta con contenido más simple."
            )
        
        # Procesar casos de prueba avanzados
        test_cases = []
        if analysis_result.get("test_cases"):
            for i, tc_data in enumerate(analysis_result["test_cases"], 1):
                test_case = {
                    "id_caso_prueba": tc_data.get("test_case_id", f"TC-{analysis_id}-{i:03d}"),
                    "titulo": tc_data.get("title", f"Caso de Prueba Avanzado {i}"),
                    "descripcion": tc_data.get("description", ""),
                    "pasos": tc_data.get("steps", []),
                    "resultado_esperado": tc_data.get("expected_result", ""),
                    "datos_prueba": tc_data.get("test_data", {}),
                    "tipo_prueba": tc_data.get("test_type", "funcional"),
                    "prioridad": tc_data.get("priority", "alta"),
                    "precondiciones": tc_data.get("preconditions", []),
                    "potencial_automatizacion": tc_data.get("automation_potential", "alto"),
                    "duracion_estimada": tc_data.get("estimated_duration", "10-15 minutos")
                }
                test_cases.append(test_case)
        
        # Procesar estrategias de prueba
        test_strategies = []
        if analysis_result.get("test_strategies"):
            for i, strat_data in enumerate(analysis_result["test_strategies"], 1):
                strategy = {
                    "id_estrategia": strat_data.get("strategy_id", f"STRAT-{analysis_id}-{i:03d}"),
                    "nombre": strat_data.get("name", f"Estrategia {i}"),
                    "descripcion": strat_data.get("description", ""),
                    "tipo": strat_data.get("type", "funcional"),
                    "prioridad": strat_data.get("priority", "alta"),
                    "casos_prueba": strat_data.get("test_cases", [])
                }
                test_strategies.append(strategy)
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Crear respuesta
        response = {
            "id_contenido": analysis_id,
            "tipo_contenido": content_type,
            "estado": "completed",
            "casos_prueba": test_cases,
            "estrategias_prueba": test_strategies,
            "analisis_cobertura": analysis_result.get("coverage_analysis", {}),
            "puntuacion_confianza": analysis_result.get("confidence_score", 0.9),
            "tiempo_procesamiento": processing_time,
            "fecha_creacion": start_time.isoformat()
        }
        
        logger.info(
            "Advanced test generation completed",
            analysis_id=analysis_id,
            test_cases_count=len(test_cases),
            strategies_count=len(test_strategies),
            processing_time=processing_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Advanced test generation failed",
            analysis_id=analysis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error generating advanced tests: {str(e)}"
        )
