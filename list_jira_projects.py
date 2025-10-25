#!/usr/bin/env python3
"""
Script para listar proyectos de Jira
"""
import asyncio
import httpx
import os
import base64
from dotenv import load_dotenv

load_dotenv()

async def list_jira_projects():
    """Listar proyectos de Jira"""
    jira_url = os.getenv("JIRA_BASE_URL", "https://aiquaa.atlassian.net")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    print(f"=== LISTANDO PROYECTOS DE JIRA ===")
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
            # Listar proyectos
            projects_url = f"{jira_url}/rest/api/3/project"
            
            response = await client.get(projects_url, headers=headers)
            
            if response.status_code == 200:
                projects = response.json()
                
                print(f"Encontrados {len(projects)} proyectos:")
                print()
                
                for project in projects:
                    key = project.get("key", "")
                    name = project.get("name", "")
                    project_type = project.get("projectTypeKey", "")
                    
                    print(f"- {key}: {name} ({project_type})")
                
                print()
                print("=== EJEMPLO DE USO ===")
                if projects:
                    first_project = projects[0]
                    project_key = first_project.get("key", "")
                    print(f"Proyecto principal: {project_key}")
                    
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(list_jira_projects())
