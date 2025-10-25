#!/usr/bin/env python3
"""
Ejemplo de uso del endpoint /analyze-jira-confluence
Demuestra cómo usar el nuevo endpoint para analizar issues de Jira y generar planes de prueba para Confluence
"""

import asyncio
import json
import httpx
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
ENDPOINT = "/analyze-jira-confluence"

# Ejemplos de datos de entrada
EJEMPLOS = [
    {
        "nombre": "Historia de Usuario - Autenticación",
        "datos": {
            "jira_issue_id": "AUTH-001",
            "confluence_space_key": "QA",
            "test_plan_title": "Plan de Pruebas - Sistema de Autenticación",
            "test_strategy": "comprehensive",
            "include_automation": True,
            "include_performance": False,
            "include_security": True
        }
    },
    {
        "nombre": "Tarea - Integración API",
        "datos": {
            "jira_issue_id": "API-002",
            "confluence_space_key": "DEV",
            "test_plan_title": "Plan de Pruebas - Integración API de Pagos",
            "test_strategy": "agile",
            "include_automation": True,
            "include_performance": True,
            "include_security": True
        }
    },
    {
        "nombre": "Bug - Rendimiento",
        "datos": {
            "jira_issue_id": "PERF-003",
            "confluence_space_key": "QA",
            "test_plan_title": "Plan de Pruebas - Optimización de Rendimiento",
            "test_strategy": "standard",
            "include_automation": False,
            "include_performance": True,
            "include_security": False
        }
    }
]

async def probar_ejemplo(ejemplo):
    """Probar un ejemplo específico"""
    print(f"\n🧪 Probando: {ejemplo['nombre']}")
    print("-" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print(f"📤 Enviando petición...")
            print(f"   Issue ID: {ejemplo['datos']['jira_issue_id']}")
            print(f"   Espacio: {ejemplo['datos']['confluence_space_key']}")
            print(f"   Estrategia: {ejemplo['datos']['test_strategy']}")
            
            start_time = datetime.now()
            response = await client.post(
                f"{BASE_URL}{ENDPOINT}",
                json=ejemplo['datos'],
                headers={"Content-Type": "application/json"}
            )
            end_time = datetime.now()
            
            print(f"📥 Respuesta recibida en {(end_time - start_time).total_seconds():.2f} segundos")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Análisis completado exitosamente")
                
                # Mostrar resumen
                print(f"\n📊 Resumen del Plan de Pruebas:")
                print(f"   ID del análisis: {result.get('analysis_id', 'N/A')}")
                print(f"   Secciones del plan: {len(result.get('test_plan_sections', []))}")
                print(f"   Fases de ejecución: {len(result.get('test_execution_phases', []))}")
                print(f"   Casos de prueba: {result.get('total_test_cases', 0)}")
                print(f"   Duración estimada: {result.get('estimated_duration', 'N/A')}")
                print(f"   Nivel de riesgo: {result.get('risk_level', 'N/A')}")
                print(f"   Confianza: {result.get('confidence_score', 0):.2f}")
                
                # Mostrar secciones del plan
                sections = result.get('test_plan_sections', [])
                if sections:
                    print(f"\n📋 Secciones del Plan:")
                    for section in sections:
                        print(f"   • {section.get('title', 'Sin título')}")
                
                # Mostrar fases de ejecución
                phases = result.get('test_execution_phases', [])
                if phases:
                    print(f"\n⏱️ Fases de Ejecución:")
                    for phase in phases:
                        print(f"   • {phase.get('phase_name', 'Sin nombre')} ({phase.get('duration', 'N/A')})")
                        print(f"     Casos: {phase.get('test_cases_count', 0)}, Responsable: {phase.get('responsible', 'N/A')}")
                
                # Mostrar algunos casos de prueba
                test_cases = result.get('test_cases', [])
                if test_cases:
                    print(f"\n🧪 Casos de Prueba (primeros 3):")
                    for i, tc in enumerate(test_cases[:3], 1):
                        print(f"   {i}. {tc.get('title', 'Sin título')}")
                        print(f"      Tipo: {tc.get('test_type', 'N/A')}, Prioridad: {tc.get('priority', 'N/A')}")
                        print(f"      Automatización: {tc.get('automation_potential', 'N/A')}")
                
                # Mostrar análisis de cobertura
                coverage = result.get('coverage_analysis', {})
                if coverage:
                    print(f"\n📈 Análisis de Cobertura:")
                    for key, value in coverage.items():
                        print(f"   • {key}: {value}")
                
                # Mostrar potencial de automatización
                automation = result.get('automation_potential', {})
                if automation:
                    print(f"\n🤖 Potencial de Automatización:")
                    for key, value in automation.items():
                        print(f"   • {key}: {value}")
                
                # Guardar resultado en archivo
                filename = f"resultado_{ejemplo['datos']['jira_issue_id'].lower()}_{int(datetime.now().timestamp())}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                print(f"\n💾 Resultado guardado en: {filename}")
                
            else:
                print(f"❌ Error en la respuesta:")
                print(f"   Status: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
    except httpx.ConnectError:
        print("❌ No se pudo conectar al servidor")
    except httpx.TimeoutException:
        print("❌ Timeout en la petición")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

async def verificar_servidor():
    """Verificar que el servidor esté funcionando"""
    print("🔍 Verificando servidor...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Servidor funcionando correctamente")
                print(f"   Estado: {health_data.get('status', 'unknown')}")
                print(f"   Componentes: {health_data.get('components', {})}")
                return True
            else:
                print(f"❌ Servidor no disponible: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error verificando servidor: {str(e)}")
        return False

async def main():
    """Función principal"""
    print("🚀 Ejemplo de uso del endpoint /analyze-jira-confluence")
    print("=" * 70)
    print(f"Servidor: {BASE_URL}")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Verificar servidor
    if not await verificar_servidor():
        print("\n❌ No se puede continuar sin servidor funcionando")
        return
    
    print(f"\n📝 Se probarán {len(EJEMPLOS)} ejemplos diferentes")
    
    # Probar cada ejemplo
    for i, ejemplo in enumerate(EJEMPLOS, 1):
        print(f"\n{'='*70}")
        print(f"Ejemplo {i}/{len(EJEMPLOS)}")
        await probar_ejemplo(ejemplo)
    
    print(f"\n{'='*70}")
    print("🏁 Todos los ejemplos completados")
    print("\n💡 Consejos de uso:")
    print("   • Asegúrate de que el issue de Jira exista y sea accesible")
    print("   • El espacio de Confluence debe existir y tener permisos")
    print("   • Las estrategias disponibles son: basic, standard, comprehensive, agile")
    print("   • Puedes habilitar/deshabilitar automatización, rendimiento y seguridad")
    print("   • El contenido generado está optimizado para Confluence con macros y formato")

if __name__ == "__main__":
    asyncio.run(main())
