#!/usr/bin/env python3
"""
Script para probar Swagger en Railway.
Verifica que todos los endpoints de documentación funcionen correctamente.
"""

import requests
import json
import sys
from urllib.parse import urljoin

# URL base de Railway
BASE_URL = "https://aiquaa-ai-analysis-ms-v2-production.up.railway.app"

def test_endpoint(url, expected_status=200, description=""):
    """Prueba un endpoint y retorna el resultado."""
    try:
        print(f"🔍 Probando: {description}")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == expected_status:
            print(f"   ✅ Status: {response.status_code} (OK)")
            return True
        else:
            print(f"   ❌ Status: {response.status_code} (esperado: {expected_status})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return False

def test_swagger_content(url):
    """Verifica que el contenido de Swagger contenga elementos esperados."""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            content = response.text
            
            # Verificar elementos clave de Swagger UI
            swagger_elements = [
                "swagger-ui",
                "OpenAPI",
                "AIQUAA AI Analysis MS",
                "API Documentation"
            ]
            
            found_elements = []
            for element in swagger_elements:
                if element in content:
                    found_elements.append(element)
            
            print(f"   📋 Elementos encontrados: {len(found_elements)}/{len(swagger_elements)}")
            for element in found_elements:
                print(f"      ✅ {element}")
            
            return len(found_elements) >= 3  # Al menos 3 elementos deben estar presentes
            
    except Exception as e:
        print(f"   ❌ Error verificando contenido: {e}")
        return False

def test_openapi_schema(url):
    """Verifica que el esquema OpenAPI sea válido."""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            schema = response.json()
            
            # Verificar campos requeridos del esquema OpenAPI
            required_fields = ["openapi", "info", "paths"]
            found_fields = [field for field in required_fields if field in schema]
            
            print(f"   📋 Campos del esquema: {len(found_fields)}/{len(required_fields)}")
            for field in found_fields:
                print(f"      ✅ {field}")
            
            # Verificar que info.title contenga el nombre del servicio
            if "info" in schema and "title" in schema["info"]:
                title = schema["info"]["title"]
                print(f"   📝 Título del servicio: {title}")
                return "AIQUAA" in title
            
            return len(found_fields) >= 2
            
    except Exception as e:
        print(f"   ❌ Error verificando esquema: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 PRUEBAS DE SWAGGER EN RAILWAY")
    print("=" * 50)
    
    # URLs a probar
    tests = [
        {
            "url": f"{BASE_URL}/",
            "description": "Redirección raíz a /docs",
            "test_function": None
        },
        {
            "url": f"{BASE_URL}/docs",
            "description": "Swagger UI",
            "test_function": test_swagger_content
        },
        {
            "url": f"{BASE_URL}/redoc",
            "description": "ReDoc UI",
            "test_function": None
        },
        {
            "url": f"{BASE_URL}/openapi.json",
            "description": "Esquema OpenAPI",
            "test_function": test_openapi_schema
        },
        {
            "url": f"{BASE_URL}/api/v1/salud",
            "description": "Health check",
            "test_function": None
        },
        {
            "url": f"{BASE_URL}/api/v1/status",
            "description": "Status detallado",
            "test_function": None
        },
        {
            "url": f"{BASE_URL}/api/v1/info",
            "description": "Información del servicio",
            "test_function": None
        }
    ]
    
    results = []
    
    for test in tests:
        print()
        success = test_endpoint(test["url"], description=test["description"])
        
        # Si el endpoint básico funciona, probar función específica si existe
        if success and test["test_function"]:
            print("   🔍 Probando función específica...")
            success = test["test_function"](test["url"])
        
        results.append({
            "description": test["description"],
            "url": test["url"],
            "success": success
        })
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 50)
    
    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {result['description']}")
    
    print(f"\n🎯 Resultado: {successful_tests}/{total_tests} pruebas exitosas")
    
    if successful_tests == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! Swagger está funcionando correctamente.")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar la configuración.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
