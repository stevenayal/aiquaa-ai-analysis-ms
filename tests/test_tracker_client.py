"""
Tests unitarios para tracker_client.py
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import httpx
from tracker_client import TrackerClient

class TestTrackerClient:
    """Tests para TrackerClient"""
    
    def setup_method(self):
        """Setup para cada test"""
        with patch.dict('os.environ', {
            'JIRA_BASE_URL': 'https://test.atlassian.net',
            'JIRA_TOKEN': 'test_token',
            'JIRA_ORG_ID': 'test_org_id'
        }):
            self.client = TrackerClient()
    
    @patch('httpx.AsyncClient')
    def test_health_check_success(self, mock_client_class):
        """Test health check exitoso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        async def run_test():
            result = await self.client.health_check()
            assert result is True
        
        asyncio.run(run_test())
    
    @patch('httpx.AsyncClient')
    def test_health_check_failure(self, mock_client_class):
        """Test health check con fallo"""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPError("Connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        async def run_test():
            result = await self.client.health_check()
            assert result is False
        
        asyncio.run(run_test())
    
    @patch('httpx.AsyncClient')
    def test_get_issue_success(self, mock_client_class):
        """Test obtener issue exitoso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "TEST-123",
            "fields": {
                "summary": "Test Issue",
                "description": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Test description"}]}]},
                "status": {"name": "To Do"},
                "priority": {"name": "High"},
                "assignee": {"displayName": "Test User"},
                "reporter": {"displayName": "Reporter"},
                "labels": ["test", "bug"],
                "created": "2023-01-01T00:00:00.000Z",
                "updated": "2023-01-01T00:00:00.000Z",
                "project": {"key": "TEST"},
                "issuetype": {"name": "Bug"}
            }
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        async def run_test():
            result = await self.client.get_issue("TEST-123")
            assert result is not None
            assert result["key"] == "TEST-123"
            assert result["summary"] == "Test Issue"
            assert result["status"] == "To Do"
        
        asyncio.run(run_test())
    
    @patch('httpx.AsyncClient')
    def test_get_issue_not_found(self, mock_client_class):
        """Test obtener issue no encontrado"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Not found", request=Mock(), response=mock_response)
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        async def run_test():
            result = await self.client.get_issue("NON-EXISTENT")
            assert result is None
        
        asyncio.run(run_test())
    
    @patch('httpx.AsyncClient')
    def test_create_issue_success(self, mock_client_class):
        """Test crear issue exitoso"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "TEST-123", "id": "12345"}
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        issue_data = {
            "fields": {
                "project": {"key": "TEST"},
                "summary": "Test Issue",
                "issuetype": {"name": "Bug"}
            }
        }
        
        async def run_test():
            result = await self.client.create_issue(issue_data)
            assert result is not None
            assert result["key"] == "TEST-123"
        
        asyncio.run(run_test())
    
    @patch('httpx.AsyncClient')
    def test_search_issues_success(self, mock_client_class):
        """Test buscar issues exitoso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test Issue 1",
                        "status": {"name": "To Do"},
                        "priority": {"name": "High"},
                        "assignee": {"displayName": "User 1"},
                        "created": "2023-01-01T00:00:00.000Z",
                        "updated": "2023-01-01T00:00:00.000Z"
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        async def run_test():
            result = await self.client.search_issues("project = TEST")
            assert len(result) == 1
            assert result[0]["key"] == "TEST-123"
            assert result[0]["summary"] == "Test Issue 1"
        
        asyncio.run(run_test())
    
    @patch('httpx.AsyncClient')
    def test_get_test_cases_success(self, mock_client_class):
        """Test obtener casos de prueba exitoso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "key": "TC-001",
                    "fields": {
                        "summary": "Test Case 1",
                        "description": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Test description"}]}]},
                        "status": {"name": "To Do"},
                        "priority": {"name": "High"},
                        "labels": ["test-case", "qa"],
                        "created": "2023-01-01T00:00:00.000Z",
                        "updated": "2023-01-01T00:00:00.000Z"
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        async def run_test():
            result = await self.client.get_test_cases("TEST")
            assert len(result) == 1
            assert result[0]["id"] == "TC-001"
            assert result[0]["title"] == "Test Case 1"
            assert "test-case" in result[0]["labels"]
        
        asyncio.run(run_test())
    
    def test_parse_jira_issue(self):
        """Test parsear issue de Jira"""
        issue_data = {
            "key": "TEST-123",
            "fields": {
                "summary": "Test Issue",
                "description": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Test description"}]}]},
                "status": {"name": "To Do"},
                "priority": {"name": "High"},
                "assignee": {"displayName": "Test User"},
                "reporter": {"displayName": "Reporter"},
                "labels": ["test", "bug"],
                "created": "2023-01-01T00:00:00.000Z",
                "updated": "2023-01-01T00:00:00.000Z",
                "project": {"key": "TEST"},
                "issuetype": {"name": "Bug"}
            }
        }
        
        result = self.client._parse_jira_issue(issue_data)
        assert result is not None
        assert result["key"] == "TEST-123"
        assert result["summary"] == "Test Issue"
        assert result["description"] == "Test description"
        assert result["status"] == "To Do"
        assert result["priority"] == "High"
        assert result["assignee"] == "Test User"
        assert result["labels"] == ["test", "bug"]
    
    def test_extract_text_from_jira_content_string(self):
        """Test extraer texto de contenido string"""
        content = "Simple text content"
        result = self.client._extract_text_from_jira_content(content)
        assert result == "Simple text content"
    
    def test_extract_text_from_jira_content_doc(self):
        """Test extraer texto de documento Jira"""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Test description"}
                    ]
                }
            ]
        }
        result = self.client._extract_text_from_jira_content(content)
        assert result == "Test description"
    
    def test_extract_text_from_doc(self):
        """Test extraer texto de documento"""
        doc = {
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "First paragraph"},
                        {"type": "text", "text": " second part"}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Second paragraph"}
                    ]
                }
            ]
        }
        result = self.client._extract_text_from_doc(doc)
        assert result == "First paragraph second part Second paragraph"
