import httpx
import asyncio
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "https://ia-analisis-production.up.railway.app"
ENDPOINT_SIMPLE = "/analizar-jira-simple"

async def test_jira_simple_endpoint():
    print(f"🚀 Iniciando prueba para el endpoint simplificado {ENDPOINT_SIMPLE}...")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Ejemplo de request con los parámetros en español para el endpoint simplificado
    request_body = {
        "id_work_item": "KAN-6",  # ID de un work item de Jira existente
        "nivel_analisis": "high"  # Nivel de análisis
    }
    
    print(f"   Enviando solicitud a {BASE_URL}{ENDPOINT_SIMPLE} con los siguientes datos:")
    print(json.dumps(request_body, indent=2))
    
    async with httpx.AsyncClient(timeout=150.0) as client: # Timeout de 2.5 minutos
        try:
            response = await client.post(f"{BASE_URL}{ENDPOINT_SIMPLE}", headers=headers, json=request_body)
            response.raise_for_status()  # Lanza una excepción para códigos de estado 4xx/5xx
            
            json_response = response.json()
            print("\n✅ Solicitud exitosa. Respuesta recibida:")
            print(json.dumps(json_response, indent=2, ensure_ascii=False))
            
            # Validaciones básicas de la respuesta en español para el endpoint simplificado
            assert "id_analisis" in json_response
            assert "id_work_item" in json_response
            assert "datos_jira" in json_response
            assert "estado" in json_response
            assert json_response["estado"] == "completed"
            assert "casos_prueba" in json_response
            assert isinstance(json_response["casos_prueba"], list)
            assert len(json_response["casos_prueba"]) >= 3 # Esperamos al menos 3 casos de prueba
            assert len(json_response["casos_prueba"]) <= 5 # Y no más de 5
            assert "analisis_cobertura" in json_response
            assert isinstance(json_response["analisis_cobertura"], dict)
            assert "puntuacion_confianza" in json_response
            assert isinstance(json_response["puntuacion_confianza"], (int, float))
            assert 0 <= json_response["puntuacion_confianza"] <= 1
            assert "tiempo_procesamiento" in json_response
            assert isinstance(json_response["tiempo_procesamiento"], (int, float))
            assert json_response["tiempo_procesamiento"] > 0
            assert "fecha_creacion" in json_response
            
            print("\n✨ Validaciones de respuesta en español para el endpoint simplificado pasadas exitosamente.")
            
        except httpx.HTTPStatusError as e:
            print(f"\n❌ Error de HTTP: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"\n❌ Error de solicitud: {e}")
        except AssertionError as e:
            print(f"\n❌ Error de validación en la respuesta: {e}")
        except Exception as e:
            print(f"\n❌ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    asyncio.run(test_jira_simple_endpoint())
