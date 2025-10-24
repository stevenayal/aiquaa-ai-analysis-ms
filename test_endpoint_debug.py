#!/usr/bin/env python3
"""
Script de debug para el endpoint /analyze-jira-confluence
Ayuda a identificar el problema específico
"""

import asyncio
import json
import httpx
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8000"
ENDPOINT = "/analyze-jira-confluence"

async def test_debug():
    """Probar el endpoint con debug detallado"""
    print("🔍 Debug del endpoint /analyze-jira-confluence")
    print("=" * 60)
    
    # Datos de prueba mínimos
    test_data = {
        "jira_issue_id": "PROJ-123",
        "confluence_space_key": "QA"
    }
    
    print(f"📤 Datos de prueba:")
    print(f"   {json.dumps(test_data, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print(f"\n🌐 Enviando petición a: {BASE_URL}{ENDPOINT}")
            
            start_time = datetime.now()
            response = await client.post(
                f"{BASE_URL}{ENDPOINT}",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            end_time = datetime.now()
            
            print(f"\n📥 Respuesta recibida:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Tiempo: {(end_time - start_time).total_seconds():.2f} segundos")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ Éxito!")
                result = response.json()
                print(f"   Análisis ID: {result.get('analysis_id', 'N/A')}")
                print(f"   Status: {result.get('status', 'N/A')}")
                print(f"   Casos de prueba: {result.get('total_test_cases', 0)}")
            else:
                print("❌ Error!")
                print(f"   Respuesta: {response.text}")
                
                # Intentar parsear como JSON para ver el detalle del error
                try:
                    error_data = response.json()
                    print(f"   Error detallado: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error como texto: {response.text}")
                    
    except httpx.ConnectError:
        print("❌ No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except httpx.TimeoutException:
        print("❌ Timeout en la petición")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_health():
    """Probar el endpoint de salud"""
    print("\n🏥 Probando endpoint de salud...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                print("✅ Servidor funcionando")
                health_data = response.json()
                print(f"   Estado: {health_data.get('status', 'unknown')}")
                print(f"   Componentes: {health_data.get('components', {})}")
            else:
                print(f"❌ Error en health check: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
    except Exception as e:
        print(f"❌ Error en health check: {str(e)}")

async def test_config():
    """Probar el endpoint de configuración"""
    print("\n⚙️ Probando endpoint de configuración...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/config")
            
            if response.status_code == 200:
                print("✅ Configuración obtenida")
                config_data = response.json()
                print(f"   Configuración: {json.dumps(config_data, indent=2)}")
            else:
                print(f"❌ Error en config: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
    except Exception as e:
        print(f"❌ Error en config: {str(e)}")

async def main():
    """Función principal de debug"""
    print("🚀 Iniciando debug del endpoint /analyze-jira-confluence")
    print("=" * 70)
    print(f"Servidor: {BASE_URL}")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Probar health check
    await test_health()
    
    # Probar configuración
    await test_config()
    
    # Probar endpoint principal
    await test_debug()
    
    print("\n" + "=" * 70)
    print("🏁 Debug completado")

if __name__ == "__main__":
    asyncio.run(main())
