#!/usr/bin/env python3
"""
Script para listar issues de Jira
"""
import asyncio
import httpx
import os
import base64
from dotenv import load_dotenv

load_dotenv()

async def list_jira_issues():
    """Listar issues de Jira"""
    jira_url = os.getenv("JIRA_BASE_URL", "https://aiquaa.atlassian.net")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    print(f"=== LISTANDO ISSUES DE JIRA ===")
    print(f"URL: {jira_url}")
    print(f"Email: {jira_email}")
    print()
    
    if not jira_token or not jira_email:
        print("Error: Faltan credenciales")
        return
    
    # Configurar autenticación
    credentials = f"{jira_email}:{jira_token}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Buscar issues del proyecto usando el nuevo endpoint
            search_url = f"{jira_url}/rest/api/3/search/jql"
            search_params = {
                "jql": "project = AIQUAA ORDER BY created DESC",
                "fields": ["key", "summary", "issuetype", "status", "priority"],
                "maxResults": 10
            }
            
            response = await client.get(search_url, params=search_params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get("issues", [])
                
                print(f"Encontrados {len(issues)} issues:")
                print()
                
                for issue in issues:
                    key = issue.get("key", "")
                    fields = issue.get("fields", {})
                    summary = fields.get("summary", "")
                    issue_type = fields.get("issuetype", {}).get("name", "")
                    status = fields.get("status", {}).get("name", "")
                    priority_obj = fields.get("priority")
                    priority = priority_obj.get("name", "") if priority_obj else "Sin prioridad"
                    
                    print(f"- {key}: {summary}")
                    print(f"  Tipo: {issue_type} | Estado: {status} | Prioridad: {priority}")
                    print()
                
                if issues:
                    print("=== EJEMPLO DE USO ===")
                    first_issue = issues[0]
                    issue_key = first_issue.get("key", "")
                    print(f"Puedes probar con: {issue_key}")
                    print()
                    print("Comando PowerShell:")
                    print(f'Invoke-RestMethod -Uri "http://localhost:8000/analyze-jira-workitem" -Method POST -ContentType "application/json" -Body \'{{"work_item_id": "{issue_key}", "project_key": "AIQUAA", "test_types": ["functional", "integration"], "coverage_level": "high"}}\'')
                else:
                    print("No se encontraron issues en el proyecto")
                    
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(list_jira_issues())
