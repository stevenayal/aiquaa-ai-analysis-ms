#!/usr/bin/env python3
"""
Script para probar la búsqueda JQL
"""
import asyncio
import httpx
import os
import base64
from dotenv import load_dotenv

load_dotenv()

async def test_jql_search():
    """Probar búsqueda JQL"""
    jira_url = os.getenv("JIRA_BASE_URL", "https://aiquaa.atlassian.net")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    print(f"=== PROBANDO BUSQUEDA JQL ===")
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
            # Probar búsqueda JQL
            search_url = f"{jira_url}/rest/api/3/search/jql"
            jql_query = "key = KAN-4 AND project = KAN"
            
            search_params = {
                "jql": jql_query,
                "fields": ["key", "summary", "issuetype", "status"],
                "maxResults": 1
            }
            
            print(f"JQL Query: {jql_query}")
            print(f"URL: {search_url}")
            print()
            
            response = await client.get(search_url, params=search_params, headers=headers)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get("issues", [])
                print(f"Encontrados {len(issues)} issues")
                
                for issue in issues:
                    key = issue.get("key", "")
                    fields = issue.get("fields", {})
                    summary = fields.get("summary", "")
                    print(f"  - {key}: {summary}")
            else:
                print(f"Error: {response.status_code}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_jql_search())
