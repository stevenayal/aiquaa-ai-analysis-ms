"""
PII Sanitization
Sanitizador de información personal identificable (PII)
"""

import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import structlog

logger = structlog.get_logger()

class PIISanitizer:
    """Sanitizador de información personal identificable"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.replacement_map = {}
        self.sanitization_log = []
    
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Inicializar patrones de detección de PII"""
        return {
            "email": {
                "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "replacement": "[EMAIL_REDACTED]",
                "category": "contact_info"
            },
            "phone": {
                "pattern": r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
                "replacement": "[PHONE_REDACTED]",
                "category": "contact_info"
            },
            "ssn": {
                "pattern": r'\b\d{3}-?\d{2}-?\d{4}\b',
                "replacement": "[SSN_REDACTED]",
                "category": "government_id"
            },
            "credit_card": {
                "pattern": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                "replacement": "[CARD_REDACTED]",
                "category": "financial"
            },
            "ip_address": {
                "pattern": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                "replacement": "[IP_REDACTED]",
                "category": "network"
            },
            "url": {
                "pattern": r'https?://[^\s<>"{}|\\^`\[\]]+',
                "replacement": "[URL_REDACTED]",
                "category": "network"
            },
            "api_key": {
                "pattern": r'\b[A-Za-z0-9]{20,}\b',
                "replacement": "[API_KEY_REDACTED]",
                "category": "credentials"
            },
            "password": {
                "pattern": r'(?i)(password|pwd|pass)\s*[:=]\s*[^\s\n]+',
                "replacement": "[PASSWORD_REDACTED]",
                "category": "credentials"
            },
            "jwt_token": {
                "pattern": r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
                "replacement": "[JWT_REDACTED]",
                "category": "credentials"
            },
            "name": {
                "pattern": r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
                "replacement": "[NAME_REDACTED]",
                "category": "personal_info"
            },
            "address": {
                "pattern": r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)',
                "replacement": "[ADDRESS_REDACTED]",
                "category": "personal_info"
            }
        }
    
    def sanitize(self, text: str, preserve_structure: bool = True) -> str:
        """
        Sanitizar texto removiendo o reemplazando PII
        
        Args:
            text: Texto a sanitizar
            preserve_structure: Si mantener la estructura del texto original
            
        Returns:
            Texto sanitizado
        """
        if not text or not isinstance(text, str):
            return text
        
        logger.info("Starting PII sanitization", text_length=len(text))
        
        sanitized_text = text
        detected_pii = []
        
        # Aplicar cada patrón de detección
        for pii_type, config in self.patterns.items():
            pattern = config["pattern"]
            replacement = config["replacement"]
            category = config["category"]
            
            # Buscar coincidencias
            matches = re.finditer(pattern, sanitized_text, re.IGNORECASE)
            
            for match in matches:
                original_text = match.group(0)
                start_pos = match.start()
                end_pos = match.end()
                
                # Crear hash para tracking
                text_hash = hashlib.md5(original_text.encode()).hexdigest()[:8]
                
                # Reemplazar con versión sanitizada
                if preserve_structure:
                    sanitized_replacement = f"{replacement}_{text_hash}"
                else:
                    sanitized_replacement = replacement
                
                sanitized_text = sanitized_text[:start_pos] + sanitized_replacement + sanitized_text[end_pos:]
                
                # Registrar detección
                detected_pii.append({
                    "type": pii_type,
                    "category": category,
                    "original_length": len(original_text),
                    "replacement": sanitized_replacement,
                    "position": start_pos,
                    "hash": text_hash,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Actualizar mapa de reemplazos
                self.replacement_map[text_hash] = {
                    "original": original_text,
                    "replacement": sanitized_replacement,
                    "type": pii_type,
                    "category": category
                }
        
        # Registrar en log de sanitización
        self.sanitization_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "original_length": len(text),
            "sanitized_length": len(sanitized_text),
            "pii_detected": len(detected_pii),
            "pii_types": list(set([pii["type"] for pii in detected_pii])),
            "categories": list(set([pii["category"] for pii in detected_pii]))
        })
        
        logger.info(
            "PII sanitization completed",
            original_length=len(text),
            sanitized_length=len(sanitized_text),
            pii_detected=len(detected_pii),
            pii_types=list(set([pii["type"] for pii in detected_pii]))
        )
        
        return sanitized_text
    
    def sanitize_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizar un caso de prueba completo
        
        Args:
            test_case: Diccionario con datos del caso de prueba
            
        Returns:
            Caso de prueba sanitizado
        """
        sanitized_case = test_case.copy()
        
        # Campos que pueden contener PII
        pii_fields = [
            "description", "summary", "title", "content", 
            "steps", "expected_result", "test_data", "comments"
        ]
        
        for field in pii_fields:
            if field in sanitized_case and isinstance(sanitized_case[field], str):
                sanitized_case[field] = self.sanitize(sanitized_case[field])
        
        # Sanitizar campos anidados
        if "metadata" in sanitized_case and isinstance(sanitized_case["metadata"], dict):
            for key, value in sanitized_case["metadata"].items():
                if isinstance(value, str):
                    sanitized_case["metadata"][key] = self.sanitize(value)
        
        # Agregar metadatos de sanitización
        sanitized_case["_sanitization_info"] = {
            "sanitized": True,
            "timestamp": datetime.utcnow().isoformat(),
            "pii_detected": len(self.replacement_map),
            "sanitizer_version": "1.0.0"
        }
        
        return sanitized_case
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detectar PII sin sanitizar
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de PII detectado
        """
        detected = []
        
        for pii_type, config in self.patterns.items():
            pattern = config["pattern"]
            category = config["category"]
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                detected.append({
                    "type": pii_type,
                    "category": category,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": self._calculate_confidence(pii_type, match.group(0))
                })
        
        return detected
    
    def _calculate_confidence(self, pii_type: str, text: str) -> float:
        """Calcular confianza en la detección de PII"""
        confidence_scores = {
            "email": 0.95,
            "phone": 0.90,
            "ssn": 0.98,
            "credit_card": 0.85,
            "ip_address": 0.80,
            "url": 0.90,
            "api_key": 0.70,
            "password": 0.85,
            "jwt_token": 0.95,
            "name": 0.60,
            "address": 0.75
        }
        
        base_confidence = confidence_scores.get(pii_type, 0.50)
        
        # Ajustar confianza basada en longitud y formato
        if len(text) > 20:
            base_confidence += 0.1
        if len(text) < 5:
            base_confidence -= 0.2
        
        return min(1.0, max(0.0, base_confidence))
    
    def get_sanitization_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de sanitización"""
        if not self.sanitization_log:
            return {"message": "No sanitization performed yet"}
        
        total_sanitizations = len(self.sanitization_log)
        total_pii_detected = sum(log["pii_detected"] for log in self.sanitization_log)
        
        # Contar tipos de PII más comunes
        pii_type_counts = {}
        for log in self.sanitization_log:
            for pii_type in log["pii_types"]:
                pii_type_counts[pii_type] = pii_type_counts.get(pii_type, 0) + 1
        
        return {
            "total_sanitizations": total_sanitizations,
            "total_pii_detected": total_pii_detected,
            "average_pii_per_text": total_pii_detected / total_sanitizations if total_sanitizations > 0 else 0,
            "most_common_pii_types": sorted(pii_type_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "replacement_map_size": len(self.replacement_map),
            "last_sanitization": self.sanitization_log[-1]["timestamp"] if self.sanitization_log else None
        }
    
    def restore_original(self, sanitized_text: str) -> str:
        """
        Restaurar texto original desde texto sanitizado
        
        Args:
            sanitized_text: Texto sanitizado
            
        Returns:
            Texto con PII restaurado (solo para testing/debugging)
        """
        restored_text = sanitized_text
        
        for hash_key, replacement_info in self.replacement_map.items():
            replacement = replacement_info["replacement"]
            original = replacement_info["original"]
            
            if replacement in restored_text:
                restored_text = restored_text.replace(replacement, original)
        
        return restored_text
    
    def clear_logs(self):
        """Limpiar logs de sanitización"""
        self.sanitization_log.clear()
        self.replacement_map.clear()
        logger.info("Sanitization logs cleared")
    
    def add_custom_pattern(self, name: str, pattern: str, replacement: str, category: str):
        """Agregar patrón personalizado de PII"""
        self.patterns[name] = {
            "pattern": pattern,
            "replacement": replacement,
            "category": category
        }
        logger.info("Custom PII pattern added", name=name, category=category)
    
    def remove_pattern(self, name: str):
        """Remover patrón de PII"""
        if name in self.patterns:
            del self.patterns[name]
            logger.info("PII pattern removed", name=name)
        else:
            logger.warning("PII pattern not found", name=name)
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizar un diccionario recursivamente
        
        Args:
            data: Diccionario a sanitizar
            
        Returns:
            Diccionario sanitizado
        """
        if not isinstance(data, dict):
            return data
        
        sanitized_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Sanitizar strings
                sanitized_data[key] = self.sanitize(value)
            elif isinstance(value, dict):
                # Recursivamente sanitizar diccionarios anidados
                sanitized_data[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                # Sanitizar listas
                sanitized_data[key] = self._sanitize_list(value)
            else:
                # Mantener otros tipos sin cambios
                sanitized_data[key] = value
        
        return sanitized_data
    
    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """Sanitizar una lista recursivamente"""
        sanitized_list = []
        
        for item in data:
            if isinstance(item, str):
                sanitized_list.append(self.sanitize(item))
            elif isinstance(item, dict):
                sanitized_list.append(self.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized_list.append(self._sanitize_list(item))
            else:
                sanitized_list.append(item)
        
        return sanitized_list