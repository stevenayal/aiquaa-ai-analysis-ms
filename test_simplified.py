"""
Script de Prueba Simplificado
Prueba todos los endpoints con parámetros en inglés y español
"""

import httpx
import asyncio
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "https://ia-analisis-production.up.railway.app"

async def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/salud")
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ Health check successful!")
            print(f"   Status: {json_response['status']}")
            print(f"   Version: {json_response['version']}")
            print(f"   Feature Flags: {json_response['feature_flags']}")
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")

async def test_llm_diagnostic():
    """Test LLM diagnostic endpoint"""
    print("\n🔍 Testing LLM diagnostic...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/diagnostico-llm")
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ LLM diagnostic successful!")
            print(f"   Status: {json_response['status']}")
            print(f"   Response Time: {json_response['response_time']:.2f}s")
            print(f"   LLM Available: {json_response['llm_available']}")
            
        except Exception as e:
            print(f"❌ LLM diagnostic failed: {e}")

async def test_analyze_content_english():
    """Test content analysis with English parameters"""
    print("\n📝 Testing content analysis (English parameters)...")
    
    headers = {"Content-Type": "application/json"}
    
    request_body = {
        "content": "El usuario debe poder iniciar sesión con email y contraseña",
        "content_type": "requirement",
        "analysis_level": "high"
    }
    
    print(f"   Request: {json.dumps(request_body, indent=2)}")
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar", headers=headers, json=request_body)
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ Content analysis successful!")
            print(f"   Analysis ID: {json_response['id_contenido']}")
            print(f"   Content Type: {json_response['tipo_contenido']}")
            print(f"   Test Cases: {len(json_response['casos_prueba'])}")
            print(f"   Suggestions: {len(json_response['sugerencias'])}")
            print(f"   Processing Time: {json_response['tiempo_procesamiento']:.2f}s")
            
        except Exception as e:
            print(f"❌ Content analysis failed: {e}")

async def test_analyze_content_spanish():
    """Test content analysis with Spanish parameters"""
    print("\n📝 Testing content analysis (Spanish parameters)...")
    
    headers = {"Content-Type": "application/json"}
    
    request_body = {
        "contenido": "El usuario debe poder iniciar sesión con email y contraseña",
        "tipo_contenido": "requirement",
        "nivel_analisis": "high"
    }
    
    print(f"   Request: {json.dumps(request_body, indent=2)}")
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar", headers=headers, json=request_body)
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ Content analysis successful!")
            print(f"   Analysis ID: {json_response['id_contenido']}")
            print(f"   Content Type: {json_response['tipo_contenido']}")
            print(f"   Test Cases: {len(json_response['casos_prueba'])}")
            print(f"   Suggestions: {len(json_response['sugerencias'])}")
            print(f"   Processing Time: {json_response['tiempo_procesamiento']:.2f}s")
            
        except Exception as e:
            print(f"❌ Content analysis failed: {e}")

async def test_analyze_jira_english():
    """Test Jira analysis with English parameters"""
    print("\n🔧 Testing Jira analysis (English parameters)...")
    
    headers = {"Content-Type": "application/json"}
    
    request_body = {
        "work_item_id": "KAN-6",
        "analysis_level": "high"
    }
    
    print(f"   Request: {json.dumps(request_body, indent=2)}")
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar-jira", headers=headers, json=request_body)
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ Jira analysis successful!")
            print(f"   Work Item ID: {json_response['id_work_item']}")
            print(f"   Analysis ID: {json_response['id_analisis']}")
            print(f"   Test Cases: {len(json_response['casos_prueba'])}")
            print(f"   Processing Time: {json_response['tiempo_procesamiento']:.2f}s")
            
        except Exception as e:
            print(f"❌ Jira analysis failed: {e}")

async def test_analyze_jira_spanish():
    """Test Jira analysis with Spanish parameters"""
    print("\n🔧 Testing Jira analysis (Spanish parameters)...")
    
    headers = {"Content-Type": "application/json"}
    
    request_body = {
        "id_work_item": "KAN-6",
        "nivel_analisis": "high"
    }
    
    print(f"   Request: {json.dumps(request_body, indent=2)}")
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar-jira", headers=headers, json=request_body)
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ Jira analysis successful!")
            print(f"   Work Item ID: {json_response['id_work_item']}")
            print(f"   Analysis ID: {json_response['id_analisis']}")
            print(f"   Test Cases: {len(json_response['casos_prueba'])}")
            print(f"   Processing Time: {json_response['tiempo_procesamiento']:.2f}s")
            
        except Exception as e:
            print(f"❌ Jira analysis failed: {e}")

async def test_analyze_jira_simple():
    """Test simplified Jira analysis"""
    print("\n⚡ Testing simplified Jira analysis...")
    
    headers = {"Content-Type": "application/json"}
    
    request_body = {
        "work_item_id": "KAN-6",
        "analysis_level": "high"
    }
    
    print(f"   Request: {json.dumps(request_body, indent=2)}")
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar-jira-simple", headers=headers, json=request_body)
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ Simplified Jira analysis successful!")
            print(f"   Work Item ID: {json_response['id_work_item']}")
            print(f"   Analysis ID: {json_response['id_analisis']}")
            print(f"   Test Cases: {len(json_response['casos_prueba'])}")
            print(f"   Processing Time: {json_response['tiempo_procesamiento']:.2f}s")
            
        except Exception as e:
            print(f"❌ Simplified Jira analysis failed: {e}")

async def test_analyze_jira_confluence_english():
    """Test Jira-Confluence analysis with English parameters"""
    print("\n📋 Testing Jira-Confluence analysis (English parameters)...")
    
    headers = {"Content-Type": "application/json"}
    
    request_body = {
        "jira_issue_id": "KAN-6",
        "confluence_space_key": "QA",
        "test_plan_title": "Plan de Pruebas - Autenticación"
    }
    
    print(f"   Request: {json.dumps(request_body, indent=2)}")
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar-jira-confluence", headers=headers, json=request_body)
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ Jira-Confluence analysis successful!")
            print(f"   Jira Issue ID: {json_response['id_issue_jira']}")
            print(f"   Analysis ID: {json_response['id_analisis']}")
            print(f"   Test Cases: {len(json_response['casos_prueba'])}")
            print(f"   Processing Time: {json_response['processing_time']:.2f}s")
            
        except Exception as e:
            print(f"❌ Jira-Confluence analysis failed: {e}")

async def test_analyze_jira_confluence_spanish():
    """Test Jira-Confluence analysis with Spanish parameters"""
    print("\n📋 Testing Jira-Confluence analysis (Spanish parameters)...")
    
    headers = {"Content-Type": "application/json"}
    
    request_body = {
        "id_issue_jira": "KAN-6",
        "espacio_confluence": "QA",
        "titulo_plan_pruebas": "Plan de Pruebas - Autenticación"
    }
    
    print(f"   Request: {json.dumps(request_body, indent=2)}")
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar-jira-confluence", headers=headers, json=request_body)
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ Jira-Confluence analysis successful!")
            print(f"   Jira Issue ID: {json_response['id_issue_jira']}")
            print(f"   Analysis ID: {json_response['id_analisis']}")
            print(f"   Test Cases: {len(json_response['casos_prueba'])}")
            print(f"   Processing Time: {json_response['processing_time']:.2f}s")
            
        except Exception as e:
            print(f"❌ Jira-Confluence analysis failed: {e}")

async def test_analyze_jira_confluence_simple():
    """Test simplified Jira-Confluence analysis"""
    print("\n⚡ Testing simplified Jira-Confluence analysis...")
    
    headers = {"Content-Type": "application/json"}
    
    request_body = {
        "jira_issue_id": "KAN-6",
        "confluence_space_key": "QA",
        "test_plan_title": "Plan de Pruebas - Autenticación"
    }
    
    print(f"   Request: {json.dumps(request_body, indent=2)}")
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar-jira-confluence-simple", headers=headers, json=request_body)
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ Simplified Jira-Confluence analysis successful!")
            print(f"   Jira Issue ID: {json_response['id_issue_jira']}")
            print(f"   Analysis ID: {json_response['id_analisis']}")
            print(f"   Test Cases: {len(json_response['casos_prueba'])}")
            print(f"   Processing Time: {json_response['processing_time']:.2f}s")
            
        except Exception as e:
            print(f"❌ Simplified Jira-Confluence analysis failed: {e}")

async def test_generate_advanced_tests():
    """Test advanced test generation"""
    print("\n🚀 Testing advanced test generation...")
    
    headers = {"Content-Type": "application/json"}
    
    request_body = {
        "content": "Sistema de autenticación con múltiples factores",
        "content_type": "requirement",
        "analysis_level": "high"
    }
    
    print(f"   Request: {json.dumps(request_body, indent=2)}")
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/generar-pruebas-avanzadas", headers=headers, json=request_body)
            response.raise_for_status()
            
            json_response = response.json()
            print("✅ Advanced test generation successful!")
            print(f"   Content ID: {json_response['id_contenido']}")
            print(f"   Content Type: {json_response['tipo_contenido']}")
            print(f"   Test Cases: {len(json_response['casos_prueba'])}")
            print(f"   Strategies: {len(json_response['estrategias_prueba'])}")
            print(f"   Processing Time: {json_response['tiempo_procesamiento']:.2f}s")
            
        except Exception as e:
            print(f"❌ Advanced test generation failed: {e}")

async def main():
    print("🚀 Iniciando pruebas del microservicio simplificado...")
    print("=" * 60)
    
    # Test system endpoints
    await test_health_check()
    await test_llm_diagnostic()
    
    # Test content analysis
    await test_analyze_content_english()
    await test_analyze_content_spanish()
    
    # Test Jira analysis
    await test_analyze_jira_english()
    await test_analyze_jira_spanish()
    await test_analyze_jira_simple()
    
    # Test Jira-Confluence analysis
    await test_analyze_jira_confluence_english()
    await test_analyze_jira_confluence_spanish()
    await test_analyze_jira_confluence_simple()
    
    # Test advanced test generation
    await test_generate_advanced_tests()
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas!")

if __name__ == "__main__":
    asyncio.run(main())
