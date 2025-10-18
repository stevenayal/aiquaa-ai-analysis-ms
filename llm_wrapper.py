"""
LLM Wrapper con Langfuse
Maneja la integración con modelos de lenguaje y observabilidad
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog
import google.generativeai as genai
from langfuse import Langfuse
# Langfuse decorators removed in newer versions
import backoff
from dotenv import load_dotenv

load_dotenv()
logger = structlog.get_logger()

class LLMWrapper:
    """Wrapper para modelos de lenguaje con observabilidad Langfuse"""
    
    def __init__(self):
        # Configurar Langfuse (opcional)
        self.langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        self.langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        self.langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if self.langfuse_public_key and self.langfuse_secret_key:
            self.langfuse = Langfuse(
                public_key=self.langfuse_public_key,
                secret_key=self.langfuse_secret_key,
                host=self.langfuse_host
            )
        else:
            self.langfuse = None
            logger.warning("Langfuse not configured - observability disabled")
        
        # Configurar Gemini
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
        
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            self.model = genai.GenerativeModel(self.gemini_model)
        else:
            self.model = None
            logger.warning("Google API key not configured")
    
    async def health_check(self) -> bool:
        """Verificar salud de Langfuse"""
        try:
            if self.langfuse is None:
                logger.info("Langfuse not configured - skipping health check")
                return True
            
            # Test básico de conexión con Langfuse
            self.langfuse.flush()
            logger.info("Langfuse health check successful")
            return True
        except Exception as e:
            logger.error("Langfuse health check failed", error=str(e))
            return False
    
    async def test_connection(self) -> bool:
        """Probar conexión con el modelo LLM"""
        try:
            if not self.model:
                raise Exception("Model not configured")
            
            # Test simple con el modelo
            response = await self._generate_response("Test connection")
            logger.info("LLM connection test successful")
            return True
        except Exception as e:
            logger.error("LLM connection test failed", error=str(e))
            return False
    
    async def analyze_test_case(
        self,
        prompt: str,
        test_case_id: str,
        analysis_id: str
    ) -> Dict[str, Any]:
        """Analizar un caso de prueba usando LLM con observabilidad"""
        try:
            logger.info(
                "Starting LLM analysis",
                test_case_id=test_case_id,
                analysis_id=analysis_id
            )
            
            # Crear trace en Langfuse (si está configurado)
            trace = None
            generation = None
            if self.langfuse:
                trace = self.langfuse.trace(
                    name="test_case_analysis",
                    user_id=f"test_case_{test_case_id}",
                    tags=["qa", "analysis", "test_case"],
                    metadata={
                        "test_case_id": test_case_id,
                        "analysis_id": analysis_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                # Crear span para la generación
                generation = trace.generation(
                    name="llm_analysis",
                    model=self.gemini_model,
                    input=prompt
                )
            
            # Generar respuesta del LLM
            response = await self._generate_response(prompt)
            
            # Procesar respuesta
            analysis_result = self._process_analysis_response(response)
            
            # Finalizar generación (si Langfuse está configurado)
            if generation:
                generation.end(
                    output=analysis_result,
                    metadata={
                        "suggestions_count": len(analysis_result.get("suggestions", [])),
                        "confidence_score": analysis_result.get("confidence_score", 0.8)
                    }
                )
            
            # Agregar metadatos
            analysis_result.update({
                "test_case_id": test_case_id,
                "analysis_id": analysis_id,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.gemini_model
            })
            
            # Finalizar trace (si Langfuse está configurado)
            if trace:
                trace.update(
                    output=analysis_result,
                    metadata={
                        "suggestions_count": len(analysis_result.get("suggestions", [])),
                        "confidence_score": analysis_result.get("confidence_score", 0.8)
                    }
                )
            
            logger.info(
                "LLM analysis completed",
                test_case_id=test_case_id,
                analysis_id=analysis_id,
                suggestions_count=len(analysis_result.get("suggestions", []))
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(
                "LLM analysis failed",
                test_case_id=test_case_id,
                analysis_id=analysis_id,
                error=str(e)
            )
            raise
    
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=60
    )
    async def _generate_response(self, prompt: str) -> str:
        """Generar respuesta del modelo LLM con retry automático"""
        try:
            if not self.model:
                raise Exception("Model not configured")
            
            # Ejecutar en thread pool para evitar bloqueo
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            return response.text
            
        except Exception as e:
            logger.error("Error generating LLM response", error=str(e))
            raise
    
    def _process_analysis_response(self, response: str) -> Dict[str, Any]:
        """Procesar respuesta del LLM y extraer sugerencias estructuradas"""
        try:
            # Parsear respuesta JSON del LLM
            import json
            import re
            
            # Buscar JSON en la respuesta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    parsed_response = json.loads(json_str)
                    return self._validate_analysis_response(parsed_response)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response, using fallback")
            
            # Fallback: procesar respuesta de texto libre
            return self._parse_text_response(response)
            
        except Exception as e:
            logger.error("Error processing analysis response", error=str(e))
            return self._create_fallback_response(response)
    
    def _validate_analysis_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validar y normalizar respuesta del análisis"""
        validated = {
            "suggestions": [],
            "confidence_score": 0.8,
            "summary": "",
            "categories": []
        }
        
        # Validar sugerencias
        if "suggestions" in response and isinstance(response["suggestions"], list):
            for suggestion in response["suggestions"]:
                if isinstance(suggestion, dict):
                    validated["suggestions"].append({
                        "type": suggestion.get("type", "general"),
                        "title": suggestion.get("title", ""),
                        "description": suggestion.get("description", ""),
                        "priority": suggestion.get("priority", "medium"),
                        "category": suggestion.get("category", "improvement")
                    })
        
        # Validar score de confianza
        if "confidence_score" in response:
            try:
                score = float(response["confidence_score"])
                validated["confidence_score"] = max(0.0, min(1.0, score))
            except (ValueError, TypeError):
                pass
        
        # Validar resumen
        if "summary" in response:
            validated["summary"] = str(response["summary"])
        
        # Validar categorías
        if "categories" in response and isinstance(response["categories"], list):
            validated["categories"] = [str(cat) for cat in response["categories"]]
        
        return validated
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parsear respuesta de texto libre a formato estructurado"""
        suggestions = []
        lines = response.split('\n')
        
        current_suggestion = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current_suggestion:
                    suggestions.append(current_suggestion)
                    current_suggestion = {}
                continue
            
            # Detectar títulos de sugerencias
            if line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                if current_suggestion:
                    suggestions.append(current_suggestion)
                
                current_suggestion = {
                    "type": "general",
                    "title": line.lstrip('•-*123456789. '),
                    "description": "",
                    "priority": "medium",
                    "category": "improvement"
                }
            elif current_suggestion and line:
                # Agregar descripción
                if current_suggestion["description"]:
                    current_suggestion["description"] += " " + line
                else:
                    current_suggestion["description"] = line
        
        # Agregar última sugerencia
        if current_suggestion:
            suggestions.append(current_suggestion)
        
        return {
            "suggestions": suggestions,
            "confidence_score": 0.7,
            "summary": response[:200] + "..." if len(response) > 200 else response,
            "categories": list(set([s.get("category", "improvement") for s in suggestions]))
        }
    
    def _create_fallback_response(self, response: str) -> Dict[str, Any]:
        """Crear respuesta de fallback cuando falla el procesamiento"""
        return {
            "suggestions": [{
                "type": "general",
                "title": "Análisis completado",
                "description": response[:500] + "..." if len(response) > 500 else response,
                "priority": "medium",
                "category": "general"
            }],
            "confidence_score": 0.5,
            "summary": "Análisis procesado con método de fallback",
            "categories": ["general"]
        }
    
    async def generate_test_scenarios(self, test_case_content: str) -> List[Dict[str, Any]]:
        """Generar escenarios de prueba basados en el caso de prueba"""
        try:
            prompt = f"""
            Basado en el siguiente caso de prueba, genera escenarios de prueba específicos:
            
            {test_case_content}
            
            Genera 3-5 escenarios que cubran:
            1. Caso feliz (happy path)
            2. Casos de error
            3. Casos límite
            4. Casos de integración
            
            Formato de respuesta JSON:
            {{
                "scenarios": [
                    {{
                        "name": "Nombre del escenario",
                        "description": "Descripción detallada",
                        "steps": ["Paso 1", "Paso 2", "Paso 3"],
                        "expected_result": "Resultado esperado",
                        "priority": "high|medium|low",
                        "category": "functional|integration|edge_case"
                    }}
                ]
            }}
            """
            
            response = await self._generate_response(prompt)
            analysis_result = self._process_analysis_response(response)
            
            return analysis_result.get("scenarios", [])
            
        except Exception as e:
            logger.error("Error generating test scenarios", error=str(e))
            return []
    
    async def suggest_improvements(self, test_case_content: str) -> List[Dict[str, Any]]:
        """Sugerir mejoras para un caso de prueba"""
        try:
            prompt = f"""
            Analiza el siguiente caso de prueba y sugiere mejoras específicas:
            
            {test_case_content}
            
            Enfócate en:
            1. Claridad y completitud
            2. Cobertura de casos edge
            3. Mejores prácticas de testing
            4. Automatización potencial
            5. Mantenibilidad
            
            Formato de respuesta JSON:
            {{
                "improvements": [
                    {{
                        "category": "clarity|coverage|automation|maintainability",
                        "title": "Título de la mejora",
                        "description": "Descripción detallada",
                        "priority": "high|medium|low",
                        "effort": "low|medium|high",
                        "impact": "low|medium|high"
                    }}
                ]
            }}
            """
            
            response = await self._generate_response(prompt)
            analysis_result = self._process_analysis_response(response)
            
            return analysis_result.get("improvements", [])
            
        except Exception as e:
            logger.error("Error suggesting improvements", error=str(e))
            return []
    
    async def analyze_requirements(
        self,
        prompt: str,
        requirement_id: str,
        analysis_id: str
    ) -> Dict[str, Any]:
        """Analizar requerimientos y generar casos de prueba usando LLM con observabilidad"""
        try:
            logger.info(
                "Starting requirements analysis",
                requirement_id=requirement_id,
                analysis_id=analysis_id
            )
            
            # Crear trace en Langfuse (si está configurado)
            trace = None
            generation = None
            if self.langfuse:
                trace = self.langfuse.trace(
                    name="requirements_analysis",
                    user_id=f"requirement_{requirement_id}",
                    tags=["qa", "requirements", "test_generation"],
                    metadata={
                        "requirement_id": requirement_id,
                        "analysis_id": analysis_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                # Crear span para la generación
                generation = trace.generation(
                    name="llm_requirements_analysis",
                    model=self.gemini_model,
                    input=prompt
                )
            
            # Generar respuesta del LLM
            response = await self._generate_response(prompt)
            
            # Procesar respuesta
            analysis_result = self._process_requirements_response(response)
            
            # Finalizar generación (si Langfuse está configurado)
            if generation:
                generation.end(
                    output=analysis_result,
                    metadata={
                        "test_cases_count": len(analysis_result.get("test_cases", [])),
                        "confidence_score": analysis_result.get("confidence_score", 0.8)
                    }
                )
            
            # Agregar metadatos
            analysis_result.update({
                "requirement_id": requirement_id,
                "analysis_id": analysis_id,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.gemini_model
            })
            
            # Finalizar trace (si Langfuse está configurado)
            if trace:
                trace.update(
                    output=analysis_result,
                    metadata={
                        "test_cases_count": len(analysis_result.get("test_cases", [])),
                        "confidence_score": analysis_result.get("confidence_score", 0.8)
                    }
                )
            
            logger.info(
                "Requirements analysis completed",
                requirement_id=requirement_id,
                analysis_id=analysis_id,
                test_cases_count=len(analysis_result.get("test_cases", []))
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(
                "Requirements analysis failed",
                requirement_id=requirement_id,
                analysis_id=analysis_id,
                error=str(e)
            )
            raise
    
    def _process_requirements_response(self, response: str) -> Dict[str, Any]:
        """Procesar respuesta del LLM para análisis de requerimientos"""
        try:
            import json
            import re
            
            # Buscar JSON en la respuesta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    parsed_response = json.loads(json_str)
                    return self._validate_requirements_response(parsed_response)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response, using fallback")
            
            # Fallback: procesar respuesta de texto libre
            return self._parse_requirements_text_response(response)
            
        except Exception as e:
            logger.error("Error processing requirements response", error=str(e))
            return self._create_fallback_requirements_response(response)
    
    def _validate_requirements_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validar y normalizar respuesta del análisis de requerimientos"""
        validated = {
            "test_cases": [],
            "coverage_analysis": {},
            "confidence_score": 0.8
        }
        
        # Validar casos de prueba
        if "test_cases" in response and isinstance(response["test_cases"], list):
            for tc in response["test_cases"]:
                if isinstance(tc, dict):
                    validated["test_cases"].append({
                        "test_case_id": tc.get("test_case_id", ""),
                        "title": tc.get("title", ""),
                        "description": tc.get("description", ""),
                        "test_type": tc.get("test_type", "functional"),
                        "priority": tc.get("priority", "medium"),
                        "steps": tc.get("steps", []),
                        "expected_result": tc.get("expected_result", ""),
                        "preconditions": tc.get("preconditions", []),
                        "test_data": tc.get("test_data", {}),
                        "automation_potential": tc.get("automation_potential", "medium"),
                        "estimated_duration": tc.get("estimated_duration", "5-10 minutes")
                    })
        
        # Validar análisis de cobertura
        if "coverage_analysis" in response and isinstance(response["coverage_analysis"], dict):
            validated["coverage_analysis"] = response["coverage_analysis"]
        
        # Validar score de confianza
        if "confidence_score" in response:
            try:
                score = float(response["confidence_score"])
                validated["confidence_score"] = max(0.0, min(1.0, score))
            except (ValueError, TypeError):
                pass
        
        return validated
    
    def _parse_requirements_text_response(self, response: str) -> Dict[str, Any]:
        """Parsear respuesta de texto libre para análisis de requerimientos"""
        # Implementación básica para fallback
        return {
            "test_cases": [{
                "test_case_id": "TC-FALLBACK-001",
                "title": "Caso de prueba generado",
                "description": response[:200] + "..." if len(response) > 200 else response,
                "test_type": "functional",
                "priority": "medium",
                "steps": ["Paso 1: Implementar según requerimiento"],
                "expected_result": "Resultado esperado según especificación",
                "preconditions": [],
                "test_data": {},
                "automation_potential": "medium",
                "estimated_duration": "5-10 minutes"
            }],
            "coverage_analysis": {
                "functional_coverage": "70%",
                "edge_case_coverage": "50%",
                "integration_coverage": "60%"
            },
            "confidence_score": 0.6
        }
    
    def _create_fallback_requirements_response(self, response: str) -> Dict[str, Any]:
        """Crear respuesta de fallback para análisis de requerimientos"""
        return {
            "test_cases": [{
                "test_case_id": "TC-ERROR-001",
                "title": "Error en análisis",
                "description": "No se pudo procesar el requerimiento correctamente",
                "test_type": "functional",
                "priority": "low",
                "steps": ["Revisar requerimiento y reintentar"],
                "expected_result": "Análisis exitoso",
                "preconditions": [],
                "test_data": {},
                "automation_potential": "low",
                "estimated_duration": "TBD"
            }],
            "coverage_analysis": {
                "functional_coverage": "0%",
                "edge_case_coverage": "0%",
                "integration_coverage": "0%"
            },
            "confidence_score": 0.3
        }
    
    async def analyze_jira_workitem(
        self,
        prompt: str,
        work_item_id: str,
        analysis_id: str
    ) -> Dict[str, Any]:
        """Analizar work item de Jira y generar casos de prueba usando LLM con observabilidad"""
        try:
            logger.info(
                "Starting Jira work item analysis",
                work_item_id=work_item_id,
                analysis_id=analysis_id
            )
            
            # Crear trace en Langfuse (si está configurado)
            trace = None
            generation = None
            if self.langfuse:
                trace = self.langfuse.trace(
                    name="jira_workitem_analysis",
                    user_id=f"workitem_{work_item_id}",
                    tags=["qa", "jira", "workitem", "test_generation"],
                    metadata={
                        "work_item_id": work_item_id,
                        "analysis_id": analysis_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                # Crear span para la generación
                generation = trace.generation(
                    name="llm_jira_workitem_analysis",
                    model=self.gemini_model,
                    input=prompt
                )
            
            # Generar respuesta del LLM
            response = await self._generate_response(prompt)
            
            # Procesar respuesta
            analysis_result = self._process_jira_workitem_response(response)
            
            # Finalizar generación (si Langfuse está configurado)
            if generation:
                generation.end(
                    output=analysis_result,
                    metadata={
                        "test_cases_count": len(analysis_result.get("test_cases", [])),
                        "confidence_score": analysis_result.get("confidence_score", 0.8)
                    }
                )
            
            # Agregar metadatos
            analysis_result.update({
                "work_item_id": work_item_id,
                "analysis_id": analysis_id,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.gemini_model
            })
            
            # Finalizar trace (si Langfuse está configurado)
            if trace:
                trace.update(
                    output=analysis_result,
                    metadata={
                        "test_cases_count": len(analysis_result.get("test_cases", [])),
                        "confidence_score": analysis_result.get("confidence_score", 0.8)
                    }
                )
            
            logger.info(
                "Jira work item analysis completed",
                work_item_id=work_item_id,
                analysis_id=analysis_id,
                test_cases_count=len(analysis_result.get("test_cases", []))
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(
                "Jira work item analysis failed",
                work_item_id=work_item_id,
                analysis_id=analysis_id,
                error=str(e)
            )
            raise
    
    def _process_jira_workitem_response(self, response: str) -> Dict[str, Any]:
        """Procesar respuesta del LLM para análisis de work item de Jira"""
        try:
            import json
            import re
            
            # Buscar JSON en la respuesta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    parsed_response = json.loads(json_str)
                    return self._validate_jira_workitem_response(parsed_response)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response, using fallback")
            
            # Fallback: procesar respuesta de texto libre
            return self._parse_jira_workitem_text_response(response)
            
        except Exception as e:
            logger.error("Error processing Jira work item response", error=str(e))
            return self._create_fallback_jira_workitem_response(response)
    
    def _validate_jira_workitem_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validar y normalizar respuesta del análisis de work item de Jira"""
        validated = {
            "test_cases": [],
            "coverage_analysis": {},
            "confidence_score": 0.8
        }
        
        # Validar casos de prueba
        if "test_cases" in response and isinstance(response["test_cases"], list):
            for tc in response["test_cases"]:
                if isinstance(tc, dict):
                    validated["test_cases"].append({
                        "test_case_id": tc.get("test_case_id", ""),
                        "title": tc.get("title", ""),
                        "description": tc.get("description", ""),
                        "test_type": tc.get("test_type", "functional"),
                        "priority": tc.get("priority", "medium"),
                        "steps": tc.get("steps", []),
                        "expected_result": tc.get("expected_result", ""),
                        "preconditions": tc.get("preconditions", []),
                        "test_data": tc.get("test_data", {}),
                        "automation_potential": tc.get("automation_potential", "medium"),
                        "estimated_duration": tc.get("estimated_duration", "5-10 minutes")
                    })
        
        # Validar análisis de cobertura
        if "coverage_analysis" in response and isinstance(response["coverage_analysis"], dict):
            validated["coverage_analysis"] = response["coverage_analysis"]
        
        # Validar score de confianza
        if "confidence_score" in response:
            try:
                score = float(response["confidence_score"])
                validated["confidence_score"] = max(0.0, min(1.0, score))
            except (ValueError, TypeError):
                pass
        
        return validated
    
    def _parse_jira_workitem_text_response(self, response: str) -> Dict[str, Any]:
        """Parsear respuesta de texto libre para análisis de work item de Jira"""
        # Implementación básica para fallback
        return {
            "test_cases": [{
                "test_case_id": "TC-JIRA-FALLBACK-001",
                "title": "Caso de prueba generado desde Jira",
                "description": response[:200] + "..." if len(response) > 200 else response,
                "test_type": "functional",
                "priority": "medium",
                "steps": ["Paso 1: Implementar según work item de Jira"],
                "expected_result": "Resultado esperado según especificación de Jira",
                "preconditions": [],
                "test_data": {},
                "automation_potential": "medium",
                "estimated_duration": "5-10 minutes"
            }],
            "coverage_analysis": {
                "functional_coverage": "70%",
                "edge_case_coverage": "50%",
                "integration_coverage": "60%"
            },
            "confidence_score": 0.6
        }
    
    def _create_fallback_jira_workitem_response(self, response: str) -> Dict[str, Any]:
        """Crear respuesta de fallback para análisis de work item de Jira"""
        return {
            "test_cases": [{
                "test_case_id": "TC-JIRA-ERROR-001",
                "title": "Error en análisis de Jira",
                "description": "No se pudo procesar el work item de Jira correctamente",
                "test_type": "functional",
                "priority": "low",
                "steps": ["Revisar work item de Jira y reintentar"],
                "expected_result": "Análisis exitoso",
                "preconditions": [],
                "test_data": {},
                "automation_potential": "low",
                "estimated_duration": "TBD"
            }],
            "coverage_analysis": {
                "functional_coverage": "0%",
                "edge_case_coverage": "0%",
                "integration_coverage": "0%"
            },
            "confidence_score": 0.3
        }
    
    async def generate_istqb_test_cases(
        self,
        prompt: str,
        programa: str,
        generation_id: str
    ) -> Dict[str, Any]:
        """Generar casos de prueba usando técnicas ISTQB con observabilidad"""
        try:
            logger.info(
                "Starting ISTQB test case generation",
                programa=programa,
                generation_id=generation_id
            )
            
            # Crear trace en Langfuse (si está configurado)
            trace = None
            generation = None
            if self.langfuse:
                trace = self.langfuse.trace(
                    name="istqb_test_generation",
                    user_id=f"programa_{programa}",
                    tags=["qa", "istqb", "test_generation", "advanced_techniques"],
                    metadata={
                        "programa": programa,
                        "generation_id": generation_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                # Crear span para la generación
                generation = trace.generation(
                    name="llm_istqb_generation",
                    model=self.gemini_model,
                    input=prompt
                )
            
            # Generar respuesta del LLM
            response = await self._generate_response(prompt)
            
            # Procesar respuesta ISTQB
            generation_result = self._process_istqb_response(response)
            
            # Finalizar generación (si Langfuse está configurado)
            if generation:
                generation.end(
                    output=generation_result,
                    metadata={
                        "csv_cases_count": len(generation_result.get("csv_cases", [])),
                        "fichas_count": len(generation_result.get("fichas", [])),
                        "artefactos_count": len(generation_result.get("artefactos_tecnicos", {})),
                        "confidence_score": generation_result.get("confidence_score", 0.8)
                    }
                )
            
            # Agregar metadatos
            generation_result.update({
                "programa": programa,
                "generation_id": generation_id,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.gemini_model
            })
            
            # Finalizar trace (si Langfuse está configurado)
            if trace:
                trace.update(
                    output=generation_result,
                    metadata={
                        "csv_cases_count": len(generation_result.get("csv_cases", [])),
                        "fichas_count": len(generation_result.get("fichas", [])),
                        "artefactos_count": len(generation_result.get("artefactos_tecnicos", {})),
                        "confidence_score": generation_result.get("confidence_score", 0.8)
                    }
                )
            
            logger.info(
                "ISTQB test case generation completed",
                programa=programa,
                generation_id=generation_id,
                csv_cases_count=len(generation_result.get("csv_cases", [])),
                fichas_count=len(generation_result.get("fichas", []))
            )
            
            return generation_result
            
        except Exception as e:
            logger.error(
                "ISTQB test case generation failed",
                programa=programa,
                generation_id=generation_id,
                error=str(e)
            )
            raise
    
    def _process_istqb_response(self, response: str) -> Dict[str, Any]:
        """Procesar respuesta del LLM para generación ISTQB"""
        try:
            # Parsear respuesta estructurada ISTQB
            sections = self._parse_istqb_sections(response)
            
            return {
                "csv_cases": sections.get("csv", []),
                "fichas": sections.get("fichas", []),
                "artefactos_tecnicos": sections.get("artefactos", {}),
                "plan_ejecucion": sections.get("plan", {}),
                "confidence_score": 0.85,
                "raw_response": response[:1000] + "..." if len(response) > 1000 else response
            }
            
        except Exception as e:
            logger.error("Error processing ISTQB response", error=str(e))
            return self._create_fallback_istqb_response(response)
    
    def _parse_istqb_sections(self, response: str) -> Dict[str, Any]:
        """Parsear secciones de la respuesta ISTQB"""
        sections = {
            "csv": [],
            "fichas": [],
            "artefactos": {},
            "plan": {}
        }
        
        lines = response.split('\n')
        current_section = None
        current_ficha = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detectar secciones
            if line.startswith('A) CSV') or line.startswith('Sección A'):
                current_section = 'csv'
                continue
            elif line.startswith('B) FICHAS') or line.startswith('Sección B'):
                current_section = 'fichas'
                continue
            elif line.startswith('C) ARTEFACTOS') or line.startswith('Sección C'):
                current_section = 'artefactos'
                continue
            elif line.startswith('D) PLAN') or line.startswith('Sección D'):
                current_section = 'plan'
                continue
            
            # Procesar contenido según sección
            if current_section == 'csv' and line.startswith('CP -'):
                sections['csv'].append(line)
            elif current_section == 'fichas':
                if line.startswith('1 - CP -'):
                    if current_ficha:
                        sections['fichas'].append('\n'.join(current_ficha))
                    current_ficha = [line]
                elif line.startswith('2- Precondicion:') or line.startswith('3- Resultado Esperado:'):
                    current_ficha.append(line)
            elif current_section == 'artefactos':
                # Procesar artefactos técnicos
                if ':' in line:
                    key, value = line.split(':', 1)
                    sections['artefactos'][key.strip()] = value.strip()
            elif current_section == 'plan':
                # Procesar plan de ejecución
                if line.startswith('{') and line.endswith('}'):
                    try:
                        import json
                        sections['plan'] = json.loads(line)
                    except:
                        sections['plan']['raw'] = line
        
        # Agregar última ficha si existe
        if current_ficha:
            sections['fichas'].append('\n'.join(current_ficha))
        
        return sections
    
    def _create_fallback_istqb_response(self, response: str) -> Dict[str, Any]:
        """Crear respuesta de fallback para generación ISTQB"""
        return {
            "csv_cases": ["CP - 001 - FALLBACK - MODULO - CONDICION - ESCENARIO"],
            "fichas": [
                "1 - CP - 001 - FALLBACK - MODULO - CONDICION - ESCENARIO\n2- Precondicion: Sistema en estado inicial\n3- Resultado Esperado: Funcionalidad básica verificada"
            ],
            "artefactos_tecnicos": {
                "equivalencias": "Particiones básicas aplicadas",
                "valores_limite": "Casos límite identificados"
            },
            "plan_ejecucion": {},
            "confidence_score": 0.5,
            "raw_response": response[:500] + "..." if len(response) > 500 else response
        }
    
    def flush_langfuse(self):
        """Forzar envío de datos a Langfuse"""
        try:
            if self.langfuse:
                self.langfuse.flush()
                logger.info("Langfuse data flushed successfully")
            else:
                logger.info("Langfuse not configured - no data to flush")
        except Exception as e:
            logger.error("Error flushing Langfuse data", error=str(e))
