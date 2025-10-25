#!/usr/bin/env python3
"""
Script para probar un issue específico de Jira
"""
import asyncio
import httpx
import os
import base64
from dotenv import load_dotenv

load_dotenv()

async def test_specific_issue():
    """Probar un issue específico de Jira"""
    jira_url = os.getenv("JIRA_BASE_URL", "https://aiquaa.atlassian.net")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    print(f"=== PROBANDO ISSUE ESPECIFICO ===")
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
            # Probar con KAN-4
            issue_key = "KAN-4"
            issue_url = f"{jira_url}/rest/api/3/issue/{issue_key}"
            
            print(f"Probando issue: {issue_key}")
            response = await client.get(issue_url, headers=headers)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
            if response.status_code == 200:
                issue_data = response.json()
                fields = issue_data.get("fields", {})
                print(f"SUCCESS! Issue encontrado:")
                print(f"  Key: {issue_data.get('key')}")
                print(f"  Summary: {fields.get('summary')}")
                print(f"  Type: {fields.get('issuetype', {}).get('name')}")
                print(f"  Status: {fields.get('status', {}).get('name')}")
            else:
                print(f"Error: {response.status_code}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_specific_issue())
