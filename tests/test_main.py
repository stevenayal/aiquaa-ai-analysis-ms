"""
Tests unitarios para main.py
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from main import app, TestCaseAnalysisRequest, TestCaseAnalysisResponse

client = TestClient(app)

class TestMainEndpoints:
    """Tests para endpoints principales"""
    
    def test_root_endpoint(self):
        """Test endpoint raíz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    @patch('main.llm_wrapper.health_check', new_callable=AsyncMock)
    @patch('main.tracker_client.health_check', new_callable=AsyncMock)
    @patch('main.llm_wrapper.test_connection', new_callable=AsyncMock)
    def test_health_check_all_healthy(self, mock_llm_test, mock_tracker_health, mock_llm_health):
        """Test health check con todos los servicios saludables"""
        mock_llm_health.return_value = True
        mock_tracker_health.return_value = True
        mock_llm_test.return_value = True
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
        assert data["components"]["langfuse"] == "healthy"
        assert data["components"]["jira"] == "healthy"
        assert data["components"]["llm"] == "healthy"
    
    @patch('main.llm_wrapper.health_check', new_callable=AsyncMock)
    @patch('main.tracker_client.health_check', new_callable=AsyncMock)
    @patch('main.llm_wrapper.test_connection', new_callable=AsyncMock)
    def test_health_check_degraded(self, mock_llm_test, mock_tracker_health, mock_llm_health):
        """Test health check con servicios degradados"""
        mock_llm_health.return_value = False
        mock_tracker_health.return_value = True
        mock_llm_test.return_value = True
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["langfuse"] == "unhealthy"
    
    @patch('main.llm_wrapper.analyze_test_case', new_callable=AsyncMock)
    @patch('main.sanitizer.sanitize')
    @patch('main.prompt_templates.get_analysis_prompt')
    def test_analyze_test_case_success(self, mock_get_prompt, mock_sanitize, mock_analyze):
        """Test análisis exitoso de caso de prueba"""
        # Setup mocks
        mock_sanitize.return_value = "sanitized content"
        mock_get_prompt.return_value = "test prompt"
        mock_analyze.return_value = {
            "suggestions": [
                {
                    "type": "clarity",
                    "title": "Test suggestion",
                    "description": "Test description",
                    "priority": "high",
                    "category": "improvement"
                }
            ],
            "confidence_score": 0.85
        }
        
        # Test data
        request_data = {
            "test_case_id": "TC-001",
            "test_case_content": "Test case content",
            "project_key": "TEST",
            "priority": "High",
            "labels": ["test", "qa"]
        }
        
        response = client.post("/analyze", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["test_case_id"] == "TC-001"
        assert data["status"] == "completed"
        assert len(data["suggestions"]) == 1
        assert data["confidence_score"] == 0.85
    
    def test_analyze_test_case_invalid_data(self):
        """Test análisis con datos inválidos"""
        request_data = {
            "test_case_id": "TC-001",
            # Missing required fields
        }
        
        response = client.post("/analyze", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @patch('main.llm_wrapper.analyze_test_case', new_callable=AsyncMock)
    def test_analyze_test_case_error(self, mock_analyze):
        """Test análisis con error"""
        mock_analyze.side_effect = Exception("LLM error")
        
        request_data = {
            "test_case_id": "TC-001",
            "test_case_content": "Test case content",
            "project_key": "TEST"
        }
        
        response = client.post("/analyze", json=request_data)
        assert response.status_code == 500
        assert "Error analyzing test case" in response.json()["detail"]
    
    def test_batch_analyze_empty_list(self):
        """Test análisis en lote con lista vacía"""
        response = client.post("/batch-analyze", json=[])
        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 0
        assert data["successful"] == 0
        assert data["failed"] == 0
    
    def test_get_analysis_result_not_found(self):
        """Test obtener resultado de análisis no encontrado"""
        response = client.get("/analysis/non-existent-id")
        assert response.status_code == 200  # Por ahora retorna placeholder
        data = response.json()
        assert "analysis_id" in data

class TestModels:
    """Tests para modelos Pydantic"""
    
    def test_test_case_analysis_request(self):
        """Test modelo TestCaseAnalysisRequest"""
        data = {
            "test_case_id": "TC-001",
            "test_case_content": "Test content",
            "project_key": "TEST",
            "priority": "High",
            "labels": ["test", "qa"]
        }
        
        request = TestCaseAnalysisRequest(**data)
        assert request.test_case_id == "TC-001"
        assert request.test_case_content == "Test content"
        assert request.project_key == "TEST"
        assert request.priority == "High"
        assert request.labels == ["test", "qa"]
    
    def test_test_case_analysis_request_defaults(self):
        """Test modelo con valores por defecto"""
        data = {
            "test_case_id": "TC-001",
            "test_case_content": "Test content",
            "project_key": "TEST"
        }
        
        request = TestCaseAnalysisRequest(**data)
        assert request.priority == "Medium"
        assert request.labels == []
    
    def test_test_case_analysis_response(self):
        """Test modelo TestCaseAnalysisResponse"""
        from datetime import datetime
        
        data = {
            "test_case_id": "TC-001",
            "analysis_id": "analysis_123",
            "status": "completed",
            "suggestions": [{"type": "test", "title": "Test"}],
            "confidence_score": 0.85,
            "processing_time": 1.5,
            "created_at": datetime.utcnow()
        }
        
        response = TestCaseAnalysisResponse(**data)
        assert response.test_case_id == "TC-001"
        assert response.analysis_id == "analysis_123"
        assert response.status == "completed"
        assert response.confidence_score == 0.85

@pytest.mark.asyncio
class TestAsyncFunctions:
    """Tests para funciones asíncronas"""
    
    async def test_log_analysis_completion(self):
        """Test función de logging de análisis"""
        from main import log_analysis_completion
        from datetime import datetime
        
        # Mock response
        response = TestCaseAnalysisResponse(
            test_case_id="TC-001",
            analysis_id="analysis_123",
            status="completed",
            suggestions=[],
            confidence_score=0.85,
            processing_time=1.0,
            created_at=datetime.utcnow()
        )
        
        # No debería lanzar excepción
        await log_analysis_completion("analysis_123", "TC-001", response)
