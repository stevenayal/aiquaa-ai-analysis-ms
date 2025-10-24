#!/usr/bin/env python3
"""
Script de prueba para el endpoint /analyze-jira-confluence
Prueba el nuevo endpoint que analiza issues de Jira y diseña planes de prueba para Confluence
"""

import asyncio
import json
import httpx
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8000"
ENDPOINT = "/analyze-jira-confluence"

# Datos de prueba
TEST_DATA = {
    "jira_issue_id": "PROJ-123",
    "confluence_space_key": "QA",
    "test_plan_title": "Plan de Pruebas - Autenticación de Usuarios",
    "test_strategy": "comprehensive",
    "include_automation": True,
    "include_performance": False,
    "include_security": True
}

async def test_confluence_endpoint():
    """Probar el endpoint de análisis de Jira y diseño de plan de pruebas para Confluence"""
    
    print("🧪 Probando endpoint /analyze-jira-confluence")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Verificar que el servidor esté funcionando
            print("1. Verificando estado del servidor...")
            health_response = await client.get(f"{BASE_URL}/health")
            if health_response.status_code == 200:
                print("✅ Servidor funcionando correctamente")
                health_data = health_response.json()
                print(f"   Estado: {health_data.get('status', 'unknown')}")
                print(f"   Componentes: {health_data.get('components', {})}")
            else:
                print(f"❌ Servidor no disponible: {health_response.status_code}")
                return
            
            print("\n2. Probando endpoint de análisis de Jira-Confluence...")
            print(f"   URL: {BASE_URL}{ENDPOINT}")
            print(f"   Datos de prueba: {json.dumps(TEST_DATA, indent=2)}")
            
            # Realizar la petición
            start_time = datetime.now()
            response = await client.post(
                f"{BASE_URL}{ENDPOINT}",
                json=TEST_DATA,
                headers={"Content-Type": "application/json"}
            )
            end_time = datetime.now()
            
            print(f"\n3. Respuesta del servidor:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Tiempo de respuesta: {(end_time - start_time).total_seconds():.2f} segundos")
            
            if response.status_code == 200:
                print("✅ Análisis completado exitosamente")
                
                # Parsear respuesta
                result = response.json()
                
                print(f"\n4. Resultados del análisis:")
                print(f"   ID del análisis: {result.get('analysis_id', 'N/A')}")
                print(f"   Issue de Jira: {result.get('jira_issue_id', 'N/A')}")
                print(f"   Espacio de Confluence: {result.get('confluence_space_key', 'N/A')}")
                print(f"   Título del plan: {result.get('test_plan_title', 'N/A')}")
                print(f"   Estado: {result.get('status', 'N/A')}")
                
                # Secciones del plan
                sections = result.get('test_plan_sections', [])
                print(f"\n5. Secciones del plan de pruebas ({len(sections)} secciones):")
                for i, section in enumerate(sections, 1):
                    print(f"   {i}. {section.get('title', 'Sin título')} (ID: {section.get('section_id', 'N/A')})")
                
                # Fases de ejecución
                phases = result.get('test_execution_phases', [])
                print(f"\n6. Fases de ejecución ({len(phases)} fases):")
                for i, phase in enumerate(phases, 1):
                    print(f"   {i}. {phase.get('phase_name', 'Sin nombre')}")
                    print(f"      Duración: {phase.get('duration', 'N/A')}")
                    print(f"      Casos de prueba: {phase.get('test_cases_count', 0)}")
                    print(f"      Responsable: {phase.get('responsible', 'N/A')}")
                
                # Casos de prueba
                test_cases = result.get('test_cases', [])
                print(f"\n7. Casos de prueba generados ({len(test_cases)} casos):")
                for i, tc in enumerate(test_cases[:5], 1):  # Mostrar solo los primeros 5
                    print(f"   {i}. {tc.get('title', 'Sin título')}")
                    print(f"      ID: {tc.get('test_case_id', 'N/A')}")
                    print(f"      Tipo: {tc.get('test_type', 'N/A')}")
                    print(f"      Prioridad: {tc.get('priority', 'N/A')}")
                    print(f"      Automatización: {tc.get('automation_potential', 'N/A')}")
                
                if len(test_cases) > 5:
                    print(f"   ... y {len(test_cases) - 5} casos más")
                
                # Métricas
                print(f"\n8. Métricas del plan:")
                print(f"   Total de casos de prueba: {result.get('total_test_cases', 0)}")
                print(f"   Duración estimada: {result.get('estimated_duration', 'N/A')}")
                print(f"   Nivel de riesgo: {result.get('risk_level', 'N/A')}")
                print(f"   Puntuación de confianza: {result.get('confidence_score', 0):.2f}")
                print(f"   Tiempo de procesamiento: {result.get('processing_time', 0):.2f} segundos")
                
                # Análisis de cobertura
                coverage = result.get('coverage_analysis', {})
                if coverage:
                    print(f"\n9. Análisis de cobertura:")
                    for key, value in coverage.items():
                        print(f"   {key}: {value}")
                
                # Potencial de automatización
                automation = result.get('automation_potential', {})
                if automation:
                    print(f"\n10. Potencial de automatización:")
                    for key, value in automation.items():
                        print(f"    {key}: {value}")
                
                # Contenido de Confluence
                confluence_content = result.get('confluence_content', '')
                confluence_markup = result.get('confluence_markup', '')
                
                if confluence_content:
                    print(f"\n11. Contenido de Confluence generado:")
                    print(f"    Longitud del contenido: {len(confluence_content)} caracteres")
                    print(f"    Primeros 200 caracteres: {confluence_content[:200]}...")
                
                if confluence_markup:
                    print(f"\n12. Markup de Confluence:")
                    print(f"    Longitud del markup: {len(confluence_markup)} caracteres")
                    print(f"    Primeros 200 caracteres: {confluence_markup[:200]}...")
                
                print(f"\n✅ Prueba completada exitosamente")
                print(f"   Tiempo total: {(end_time - start_time).total_seconds():.2f} segundos")
                
            else:
                print(f"❌ Error en la respuesta:")
                print(f"   Status: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
    except httpx.ConnectError:
        print("❌ No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except httpx.TimeoutException:
        print("❌ Timeout en la petición")
        print("   El análisis puede estar tomando más tiempo del esperado")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

async def test_health_endpoint():
    """Probar el endpoint de salud"""
    print("🏥 Probando endpoint de salud")
    print("=" * 40)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                print("✅ Endpoint de salud funcionando")
                health_data = response.json()
                print(f"   Estado general: {health_data.get('status', 'unknown')}")
                print(f"   Timestamp: {health_data.get('timestamp', 'N/A')}")
                print(f"   Versión: {health_data.get('version', 'N/A')}")
                
                components = health_data.get('components', {})
                print(f"   Componentes:")
                for component, status in components.items():
                    print(f"     - {component}: {status}")
            else:
                print(f"❌ Error en endpoint de salud: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error probando endpoint de salud: {str(e)}")

async def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas del endpoint /analyze-jira-confluence")
    print("=" * 70)
    print(f"Servidor: {BASE_URL}")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Probar endpoint de salud primero
    await test_health_endpoint()
    print()
    
    # Probar endpoint principal
    await test_confluence_endpoint()
    
    print("\n" + "=" * 70)
    print("🏁 Pruebas completadas")

if __name__ == "__main__":
    asyncio.run(main())
