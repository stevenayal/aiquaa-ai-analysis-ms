"""
Tracker Client para Jira y Redmine
Maneja la integración con sistemas de gestión de proyectos
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = structlog.get_logger()

class TrackerClient:
    """Cliente para integración con sistemas de tracking (Jira, Redmine)"""
    
    def __init__(self):
        self.jira_base_url = os.getenv("JIRA_BASE_URL")
        self.jira_token = os.getenv("JIRA_TOKEN")
        self.jira_org_id = os.getenv("JIRA_ORG_ID")
        self.timeout = 30.0
        
        # Configurar headers para Jira
        # Para Jira, necesitamos usar Basic Auth con email y API token
        # El token que proporcionaste es un API token, necesitamos tu email de Jira
        self.jira_email = os.getenv("JIRA_EMAIL", "")
        if self.jira_email and self.jira_token:
            import base64
            credentials = f"{self.jira_email}:{self.jira_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            self.jira_headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        else:
            # Fallback a Bearer si no hay email configurado
            self.jira_headers = {
                "Authorization": f"Bearer {self.jira_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
    
    async def health_check(self) -> bool:
        """Verificar salud de la conexión con Jira"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.jira_base_url}/rest/api/3/myself",
                    headers=self.jira_headers
                )
                response.raise_for_status()
                logger.info("Jira health check successful")
                return True
        except Exception as e:
            logger.error("Jira health check failed", error=str(e))
            return False
    
    async def get_work_item_details(self, work_item_id: str, project_key: str = "") -> Optional[Dict[str, Any]]:
        """Obtener detalles de un work item específico de Jira"""
        try:
            # Extraer project key del work_item_id si no se proporciona
            if not project_key and work_item_id:
                # Formato típico: PROJECT-123, extraer "PROJECT"
                if '-' in work_item_id:
                    project_key = work_item_id.split('-')[0]
                else:
                    project_key = work_item_id
            
            logger.info("Fetching work item details", work_item_id=work_item_id, project_key=project_key)
            
            # Construir JQL query para buscar el work item
            jql_query = f"key = {work_item_id}"
            
            # Hacer la búsqueda usando el endpoint correcto
            search_url = f"{self.jira_base_url}/rest/api/3/search/jql"
            search_params = {
                "jql": jql_query,
                "fields": [
                    "summary",
                    "description", 
                    "issuetype",
                    "priority",
                    "status",
                    "customfield_10014",  # Acceptance Criteria (común en Jira)
                    "customfield_10015",  # Story Points (común en Jira)
                    "labels",
                    "components",
                    "fixVersions",
                    "assignee",
                    "reporter",
                    "created",
                    "updated"
                ],
                "maxResults": 1
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(search_url, params=search_params, headers=self.jira_headers)
                
                logger.info("Jira API response", 
                           status_code=response.status_code, 
                           url=search_url,
                           jql_query=jql_query)
                
                if response.status_code == 200:
                    data = response.json()
                    issues = data.get("issues", [])
                    total = data.get("total", 0)
                    
                    logger.info("Jira search results", 
                               total_issues=total, 
                               issues_found=len(issues))
                    
                    if not issues:
                        logger.warning("Work item not found", 
                                     work_item_id=work_item_id, 
                                     project_key=project_key,
                                     jql_query=jql_query,
                                     total_issues=total)
                        return None
                    
                    issue = issues[0]
                    fields = issue.get("fields", {})
                    
                    # Extraer información relevante
                    work_item_data = {
                        "key": issue.get("key"),
                        "summary": fields.get("summary", ""),
                        "description": self._extract_text_from_jira_content(fields.get("description", "")),
                        "issue_type": fields.get("issuetype", {}).get("name", ""),
                        "priority": fields.get("priority", {}).get("name", "") if fields.get("priority") else "",
                        "status": fields.get("status", {}).get("name", ""),
                        "acceptance_criteria": self._extract_text_from_jira_content(fields.get("customfield_10014", "")),
                        "story_points": fields.get("customfield_10015"),
                        "labels": fields.get("labels", []),
                        "components": [comp.get("name", "") for comp in fields.get("components", [])],
                        "fix_versions": [version.get("name", "") for version in fields.get("fixVersions", [])],
                        "assignee": fields.get("assignee", {}).get("displayName", "") if fields.get("assignee") else "",
                        "reporter": fields.get("reporter", {}).get("displayName", "") if fields.get("reporter") else "",
                        "created": fields.get("created", ""),
                        "updated": fields.get("updated", ""),
                        "url": f"{self.jira_base_url}/browse/{issue.get('key')}"
                    }
                    
                    logger.info("Work item details retrieved successfully", 
                               work_item_id=work_item_id, 
                               issue_type=work_item_data.get("issue_type"))
                    
                    return work_item_data
                    
                else:
                    logger.error("Failed to fetch work item", 
                               work_item_id=work_item_id, 
                               status_code=response.status_code,
                               response=response.text)
                    return None
                
        except Exception as e:
            logger.error("Error fetching work item details", 
                        work_item_id=work_item_id, 
                        error=str(e))
            return None
    
    async def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Obtener un issue de Jira por su clave"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.jira_base_url}/rest/api/3/issue/{issue_key}",
                    headers=self.jira_headers
                )
                response.raise_for_status()
                
                issue_data = response.json()
                return self._parse_jira_issue(issue_data)
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Issue not found", issue_key=issue_key)
                return None
            else:
                logger.error("HTTP error getting issue", issue_key=issue_key, status_code=e.response.status_code)
                raise
        except Exception as e:
            logger.error("Error getting issue", issue_key=issue_key, error=str(e))
            raise
    
    async def create_issue(self, issue_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crear un nuevo issue en Jira"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.jira_base_url}/rest/api/3/issue",
                    headers=self.jira_headers,
                    json=issue_data
                )
                response.raise_for_status()
                
                created_issue = response.json()
                logger.info("Issue created successfully", issue_key=created_issue.get("key"))
                return created_issue
                
        except Exception as e:
            logger.error("Error creating issue", error=str(e))
            raise
    
    async def update_issue(self, issue_key: str, update_data: Dict[str, Any]) -> bool:
        """Actualizar un issue existente en Jira"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    f"{self.jira_base_url}/rest/api/3/issue/{issue_key}",
                    headers=self.jira_headers,
                    json=update_data
                )
                response.raise_for_status()
                
                logger.info("Issue updated successfully", issue_key=issue_key)
                return True
                
        except Exception as e:
            logger.error("Error updating issue", issue_key=issue_key, error=str(e))
            return False
    
    async def search_issues(
        self,
        jql: str,
        fields: Optional[List[str]] = None,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """Buscar issues en Jira usando JQL"""
        try:
            search_payload = {
                "jql": jql,
                "maxResults": max_results,
                "fields": fields or ["key", "summary", "status", "priority", "assignee", "created", "updated"]
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.jira_base_url}/rest/api/3/search",
                    headers=self.jira_headers,
                    json=search_payload
                )
                response.raise_for_status()
                
                search_results = response.json()
                issues = []
                
                for issue in search_results.get("issues", []):
                    parsed_issue = self._parse_jira_issue(issue)
                    if parsed_issue:
                        issues.append(parsed_issue)
                
                logger.info("Issues found", count=len(issues), jql=jql)
                return issues
                
        except Exception as e:
            logger.error("Error searching issues", jql=jql, error=str(e))
            raise
    
    async def get_test_cases(self, project_key: str) -> List[Dict[str, Any]]:
        """Obtener casos de prueba de un proyecto"""
        try:
            # JQL para buscar casos de prueba (asumiendo que usan un tipo específico o etiquetas)
            jql = f"project = {project_key} AND (issuetype = 'Test Case' OR labels in ('test-case', 'qa', 'testing'))"
            
            issues = await self.search_issues(
                jql=jql,
                fields=["key", "summary", "description", "status", "priority", "labels", "created", "updated"]
            )
            
            # Filtrar y formatear casos de prueba
            test_cases = []
            for issue in issues:
                test_case = {
                    "id": issue["key"],
                    "title": issue.get("summary", ""),
                    "description": issue.get("description", ""),
                    "status": issue.get("status", {}).get("name", "Unknown"),
                    "priority": issue.get("priority", {}).get("name", "Medium"),
                    "labels": issue.get("labels", []),
                    "created": issue.get("created"),
                    "updated": issue.get("updated")
                }
                test_cases.append(test_case)
            
            logger.info("Test cases retrieved", project_key=project_key, count=len(test_cases))
            return test_cases
            
        except Exception as e:
            logger.error("Error getting test cases", project_key=project_key, error=str(e))
            raise
    
    async def create_test_case_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        priority: str = "Medium",
        labels: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Crear un issue de caso de prueba en Jira"""
        try:
            issue_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": description
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {"name": "Test Case"},
                    "priority": {"name": priority},
                    "labels": labels or ["test-case", "qa", "auto-generated"]
                }
            }
            
            created_issue = await self.create_issue(issue_data)
            logger.info("Test case issue created", project_key=project_key, issue_key=created_issue.get("key"))
            return created_issue
            
        except Exception as e:
            logger.error("Error creating test case issue", project_key=project_key, error=str(e))
            raise
    
    async def add_comment(self, issue_key: str, comment: str) -> bool:
        """Agregar comentario a un issue"""
        try:
            comment_data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment
                                }
                            ]
                        }
                    ]
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.jira_base_url}/rest/api/3/issue/{issue_key}/comment",
                    headers=self.jira_headers,
                    json=comment_data
                )
                response.raise_for_status()
                
                logger.info("Comment added successfully", issue_key=issue_key)
                return True
                
        except Exception as e:
            logger.error("Error adding comment", issue_key=issue_key, error=str(e))
            return False
    
    def _parse_jira_issue(self, issue_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parsear datos de issue de Jira a formato estándar"""
        try:
            fields = issue_data.get("fields", {})
            
            return {
                "key": issue_data.get("key"),
                "summary": fields.get("summary", ""),
                "description": self._extract_text_from_jira_content(fields.get("description")),
                "status": fields.get("status", {}).get("name", "Unknown"),
                "priority": fields.get("priority", {}).get("name", "Medium"),
                "assignee": fields.get("assignee", {}).get("displayName", "Unassigned"),
                "reporter": fields.get("reporter", {}).get("displayName", "Unknown"),
                "labels": fields.get("labels", []),
                "created": fields.get("created"),
                "updated": fields.get("updated"),
                "project": fields.get("project", {}).get("key", ""),
                "issue_type": fields.get("issuetype", {}).get("name", "Unknown")
            }
        except Exception as e:
            logger.error("Error parsing Jira issue", error=str(e))
            return None
    
    def _extract_text_from_jira_content(self, content: Any) -> str:
        """Extraer texto plano del contenido estructurado de Jira"""
        if not content:
            return ""
        
        if isinstance(content, str):
            return content
        
        if isinstance(content, dict):
            if content.get("type") == "doc":
                return self._extract_text_from_doc(content)
            elif "text" in content:
                return content["text"]
        
        return str(content)
    
    def _extract_text_from_doc(self, doc: Dict[str, Any]) -> str:
        """Extraer texto de un documento Jira"""
        text_parts = []
        
        if "content" in doc:
            for item in doc["content"]:
                if item.get("type") == "paragraph" and "content" in item:
                    for para_item in item["content"]:
                        if para_item.get("type") == "text":
                            text_parts.append(para_item.get("text", ""))
        
        return " ".join(text_parts)
    
    async def get_project_info(self, project_key: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un proyecto"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.jira_base_url}/rest/api/3/project/{project_key}",
                    headers=self.jira_headers
                )
                response.raise_for_status()
                
                project_data = response.json()
                return {
                    "key": project_data.get("key"),
                    "name": project_data.get("name"),
                    "description": project_data.get("description", ""),
                    "project_type": project_data.get("projectTypeKey"),
                    "lead": project_data.get("lead", {}).get("displayName", ""),
                    "url": project_data.get("self")
                }
                
        except Exception as e:
            logger.error("Error getting project info", project_key=project_key, error=str(e))
            return None
