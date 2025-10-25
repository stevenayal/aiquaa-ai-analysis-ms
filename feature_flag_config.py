"""
Configuración del Feature Flag
Maneja la configuración de parámetros en inglés/español
"""

import os
from typing import Dict, Any

class FeatureFlagConfig:
    """Configuración de feature flags"""
    
    def __init__(self):
        self.use_spanish_params = os.getenv("USE_SPANISH_PARAMS", "false").lower() == "true"
        self.jira_enabled = os.getenv("JIRA_ENABLED", "true").lower() == "true"
        self.confluence_enabled = os.getenv("CONFLUENCE_ENABLED", "true").lower() == "true"
        self.llm_enabled = os.getenv("LLM_ENABLED", "true").lower() == "true"
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado de todos los feature flags"""
        return {
            "USE_SPANISH_PARAMS": self.use_spanish_params,
            "JIRA_ENABLED": self.jira_enabled,
            "CONFLUENCE_ENABLED": self.confluence_enabled,
            "LLM_ENABLED": self.llm_enabled
        }
    
    def is_spanish_mode(self) -> bool:
        """Verifica si está en modo español"""
        return self.use_spanish_params
    
    def is_english_mode(self) -> bool:
        """Verifica si está en modo inglés"""
        return not self.use_spanish_params
    
    def get_parameter_mapping(self) -> Dict[str, str]:
        """Obtiene el mapeo de parámetros según el feature flag"""
        if self.use_spanish_params:
            return {
                # Jira parameters
                "work_item_id": "id_work_item",
                "analysis_level": "nivel_analisis",
                
                # Confluence parameters
                "jira_issue_id": "id_issue_jira",
                "confluence_space_key": "espacio_confluence",
                "test_plan_title": "titulo_plan_pruebas",
                
                # Basic parameters
                "content": "contenido",
                "content_type": "tipo_contenido",
                "analysis_level": "nivel_analisis"
            }
        else:
            return {
                # Jira parameters
                "id_work_item": "work_item_id",
                "nivel_analisis": "analysis_level",
                
                # Confluence parameters
                "id_issue_jira": "jira_issue_id",
                "espacio_confluence": "confluence_space_key",
                "titulo_plan_pruebas": "test_plan_title",
                
                # Basic parameters
                "contenido": "content",
                "tipo_contenido": "content_type",
                "nivel_analisis": "analysis_level"
            }
    
    def get_parameter_names(self, endpoint_type: str) -> Dict[str, str]:
        """Obtiene los nombres de parámetros para un tipo de endpoint"""
        if self.use_spanish_params:
            if endpoint_type == "jira":
                return {
                    "work_item_id": "id_work_item",
                    "analysis_level": "nivel_analisis"
                }
            elif endpoint_type == "confluence":
                return {
                    "jira_issue_id": "id_issue_jira",
                    "confluence_space_key": "espacio_confluence",
                    "test_plan_title": "titulo_plan_pruebas"
                }
            elif endpoint_type == "basic":
                return {
                    "content": "contenido",
                    "content_type": "tipo_contenido",
                    "analysis_level": "nivel_analisis"
                }
        else:
            if endpoint_type == "jira":
                return {
                    "id_work_item": "work_item_id",
                    "nivel_analisis": "analysis_level"
                }
            elif endpoint_type == "confluence":
                return {
                    "id_issue_jira": "jira_issue_id",
                    "espacio_confluence": "confluence_space_key",
                    "titulo_plan_pruebas": "test_plan_title"
                }
            elif endpoint_type == "basic":
                return {
                    "contenido": "content",
                    "tipo_contenido": "content_type",
                    "nivel_analisis": "analysis_level"
                }
        
        return {}

# Instancia global de configuración
feature_config = FeatureFlagConfig()

def get_feature_config() -> FeatureFlagConfig:
    """Obtiene la configuración de feature flags"""
    return feature_config

def is_spanish_mode() -> bool:
    """Verifica si está en modo español"""
    return feature_config.is_spanish_mode()

def is_english_mode() -> bool:
    """Verifica si está en modo inglés"""
    return feature_config.is_english_mode()

def get_parameter_mapping() -> Dict[str, str]:
    """Obtiene el mapeo de parámetros"""
    return feature_config.get_parameter_mapping()

def get_parameter_names(endpoint_type: str) -> Dict[str, str]:
    """Obtiene los nombres de parámetros para un tipo de endpoint"""
    return feature_config.get_parameter_names(endpoint_type)
