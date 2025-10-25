#!/usr/bin/env python3
"""
Script detallado para probar la conexión con Jira
"""
import asyncio
import httpx
import os
import base64
from dotenv import load_dotenv

load_dotenv()

async def test_jira_detailed():
    """Probar conexión con Jira con diferentes métodos de autenticación"""
    jira_url = os.getenv("JIRA_BASE_URL", "https://aiquaa.atlassian.net")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    print(f"=== DIAGNOSTICO DE CONEXION JIRA ===")
    print(f"URL: {jira_url}")
    print(f"Email: {jira_email}")
    print(f"Token: {'Configurado' if jira_token else 'No configurado'}")
    print(f"Token length: {len(jira_token) if jira_token else 0}")
    print()
    
    if not jira_token or not jira_email:
        print("Error: Faltan credenciales")
        return
    
    # Método 1: Basic Auth con email y API token
    print("=== METODO 1: Basic Auth (email + API token) ===")
    credentials = f"{jira_email}:{jira_token}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers_basic = {
        "Authorization": f"Basic {encoded_credentials}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{jira_url}/rest/api/3/myself", headers=headers_basic)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"SUCCESS! Usuario: {user_data.get('displayName')}")
                return True
                
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print()
    
    # Método 2: Bearer Token (por si acaso)
    print("=== METODO 2: Bearer Token ===")
    headers_bearer = {
        "Authorization": f"Bearer {jira_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{jira_url}/rest/api/3/myself", headers=headers_bearer)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print()
    
    # Método 3: Probar endpoint de información del servidor
    print("=== METODO 3: Server Info ===")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{jira_url}/rest/api/3/serverInfo", headers=headers_basic)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print()
    print("=== RECOMENDACIONES ===")
    print("1. Verifica que el API token sea válido")
    print("2. Asegúrate de que el email sea correcto")
    print("3. Verifica que tengas permisos en el proyecto")
    print("4. Intenta generar un nuevo API token")

if __name__ == "__main__":
    asyncio.run(test_jira_detailed())
