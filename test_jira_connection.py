#!/usr/bin/env python3
"""
Script para probar la conexión con Jira
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_jira_connection():
    """Probar conexión con Jira"""
    jira_url = os.getenv("JIRA_BASE_URL", "https://aiquaa.atlassian.net")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    print(f"Probando conexion con Jira: {jira_url}")
    print(f"Token configurado: {'SI' if jira_token else 'NO'}")
    print(f"Email configurado: {'SI' if jira_email else 'NO'}")
    
    if not jira_token:
        print("Error: JIRA_TOKEN no esta configurado")
        return
    
    if not jira_email:
        print("Error: JIRA_EMAIL no esta configurado")
        print("Necesitas configurar tu email de Jira en JIRA_EMAIL")
        return
    
    # Usar Basic Authentication para Jira
    import base64
    credentials = f"{jira_email}:{jira_token}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Probar endpoint básico
            response = await client.get(f"{jira_url}/rest/api/3/myself", headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"Conexion exitosa!")
                print(f"Usuario: {user_data.get('displayName', 'N/A')}")
                print(f"Email: {user_data.get('emailAddress', 'N/A')}")
                print(f"Account ID: {user_data.get('accountId', 'N/A')}")
            else:
                print(f"Error en la conexion: {response.text}")
                
    except Exception as e:
        print(f"Error de conexion: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_jira_connection())
