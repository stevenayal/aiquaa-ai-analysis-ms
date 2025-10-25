import httpx
import asyncio
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "https://ia-analisis-production.up.railway.app"

async def test_jira_endpoint_english_params():
    """Test Jira endpoint with English parameters (feature flag OFF)"""
    print("🧪 Testing Jira endpoint with English parameters...")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request with English parameters
    request_body = {
        "work_item_id": "KAN-6",  # English parameter name
        "analysis_level": "high"  # English parameter name
    }
    
    print(f"   Enviando solicitud a {BASE_URL}/analizar-jira con parámetros en inglés:")
    print(json.dumps(request_body, indent=2))
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar-jira", headers=headers, json=request_body)
            
            print(f"\n📊 Respuesta recibida (Status: {response.status_code}):")
            if response.status_code == 200:
                json_response = response.json()
                print("✅ Solicitud exitosa con parámetros en inglés!")
                print(json.dumps(json_response, indent=2, ensure_ascii=False))
                
                # Validaciones básicas
                assert "id_work_item" in json_response
                assert "datos_jira" in json_response
                assert "estado" in json_response
                assert json_response["estado"] == "completed"
                assert "casos_prueba" in json_response
                assert isinstance(json_response["casos_prueba"], list)
                
                print("✨ Validaciones pasadas exitosamente.")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except httpx.RequestError as e:
            print(f"❌ Error de solicitud: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

async def test_jira_endpoint_spanish_params():
    """Test Jira endpoint with Spanish parameters (feature flag ON)"""
    print("\n🧪 Testing Jira endpoint with Spanish parameters...")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request with Spanish parameters
    request_body = {
        "id_work_item": "KAN-6",  # Spanish parameter name
        "nivel_analisis": "high"   # Spanish parameter name
    }
    
    print(f"   Enviando solicitud a {BASE_URL}/analizar-jira con parámetros en español:")
    print(json.dumps(request_body, indent=2))
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar-jira", headers=headers, json=request_body)
            
            print(f"\n📊 Respuesta recibida (Status: {response.status_code}):")
            if response.status_code == 200:
                json_response = response.json()
                print("✅ Solicitud exitosa con parámetros en español!")
                print(json.dumps(json_response, indent=2, ensure_ascii=False))
                
                # Validaciones básicas
                assert "id_work_item" in json_response
                assert "datos_jira" in json_response
                assert "estado" in json_response
                assert json_response["estado"] == "completed"
                assert "casos_prueba" in json_response
                assert isinstance(json_response["casos_prueba"], list)
                
                print("✨ Validaciones pasadas exitosamente.")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except httpx.RequestError as e:
            print(f"❌ Error de solicitud: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

async def test_jira_simple_endpoint():
    """Test simplified Jira endpoint"""
    print("\n🧪 Testing simplified Jira endpoint...")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request with English parameters for simplified endpoint
    request_body = {
        "work_item_id": "KAN-6",
        "analysis_level": "high"
    }
    
    print(f"   Enviando solicitud a {BASE_URL}/analizar-jira-simple:")
    print(json.dumps(request_body, indent=2))
    
    async with httpx.AsyncClient(timeout=150.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/analizar-jira-simple", headers=headers, json=request_body)
            
            print(f"\n📊 Respuesta recibida (Status: {response.status_code}):")
            if response.status_code == 200:
                json_response = response.json()
                print("✅ Solicitud exitosa al endpoint simplificado!")
                print(json.dumps(json_response, indent=2, ensure_ascii=False))
                
                # Validaciones básicas
                assert "id_work_item" in json_response
                assert "datos_jira" in json_response
                assert "estado" in json_response
                assert json_response["estado"] == "completed"
                assert "casos_prueba" in json_response
                assert isinstance(json_response["casos_prueba"], list)
                assert len(json_response["casos_prueba"]) <= 5  # Simplified should have max 5 cases
                
                print("✨ Validaciones del endpoint simplificado pasadas exitosamente.")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except httpx.RequestError as e:
            print(f"❌ Error de solicitud: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

async def main():
    print("🚀 Iniciando pruebas del feature flag para endpoints de Jira...")
    print("=" * 60)
    
    # Test with English parameters (feature flag OFF)
    await test_jira_endpoint_english_params()
    
    # Test with Spanish parameters (feature flag ON)
    await test_jira_endpoint_spanish_params()
    
    # Test simplified endpoint
    await test_jira_simple_endpoint()
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas!")

if __name__ == "__main__":
    asyncio.run(main())
