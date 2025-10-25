#!/usr/bin/env python3
"""
Script de prueba simplificado para el endpoint /analyze-jira-confluence
Prueba el endpoint con parámetros simplificados
"""

import asyncio
import json
import httpx
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8000"
ENDPOINT = "/analyze-jira-confluence"

# Ejemplos simplificados
EJEMPLOS_SIMPLIFICADOS = [
    {
        "nombre": "Mínimo - Solo Parámetros Requeridos",
        "datos": {
            "jira_issue_id": "PROJ-123",
            "confluence_space_key": "QA"
        }
    },
    {
        "nombre": "Con Título Personalizado",
        "datos": {
            "jira_issue_id": "AUTH-001",
            "confluence_space_key": "QA",
            "test_plan_title": "Plan de Pruebas - Sistema de Autenticación"
        }
    },
    {
        "nombre": "Tarea de Integración",
        "datos": {
            "jira_issue_id": "API-002",
            "confluence_space_key": "DEV",
            "test_plan_title": "Plan de Pruebas - Integración API de Pagos"
        }
    },
    {
        "nombre": "Bug de Rendimiento",
        "datos": {
            "jira_issue_id": "PERF-003",
            "confluence_space_key": "QA",
            "test_plan_title": "Plan de Pruebas - Optimización de Rendimiento"
        }
    }
]

async def probar_ejemplo_simplificado(ejemplo):
    """Probar un ejemplo simplificado"""
    print(f"\n🧪 Probando: {ejemplo['nombre']}")
    print("-" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print(f"📤 Enviando petición...")
            print(f"   Issue ID: {ejemplo['datos']['jira_issue_id']}")
            print(f"   Espacio: {ejemplo['datos']['confluence_space_key']}")
            if 'test_plan_title' in ejemplo['datos']:
                print(f"   Título: {ejemplo['datos']['test_plan_title']}")
            else:
                print(f"   Título: (se generará automáticamente)")
            
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
                print(f"   Issue de Jira: {result.get('jira_issue_id', 'N/A')}")
                print(f"   Espacio de Confluence: {result.get('confluence_space_key', 'N/A')}")
                print(f"   Título del plan: {result.get('test_plan_title', 'N/A')}")
                print(f"   Secciones del plan: {len(result.get('test_plan_sections', []))}")
                print(f"   Fases de ejecución: {len(result.get('test_execution_phases', []))}")
                print(f"   Casos de prueba: {result.get('total_test_cases', 0)}")
                print(f"   Duración estimada: {result.get('estimated_duration', 'N/A')}")
                print(f"   Nivel de riesgo: {result.get('risk_level', 'N/A')}")
                print(f"   Confianza: {result.get('confidence_score', 0):.2f}")
                print(f"   Tiempo de procesamiento: {result.get('processing_time', 0):.2f} segundos")
                
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
                filename = f"resultado_simplificado_{ejemplo['datos']['jira_issue_id'].lower()}_{int(datetime.now().timestamp())}.json"
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

async def probar_validacion():
    """Probar validación de parámetros"""
    print(f"\n🔍 Probando validación de parámetros...")
    
    casos_validacion = [
        {
            "nombre": "Issue ID vacío",
            "datos": {"jira_issue_id": "", "confluence_space_key": "QA"},
            "esperado": 422
        },
        {
            "nombre": "Espacio vacío",
            "datos": {"jira_issue_id": "PROJ-123", "confluence_space_key": ""},
            "esperado": 422
        },
        {
            "nombre": "Issue no encontrado",
            "datos": {"jira_issue_id": "INVALID-999", "confluence_space_key": "QA"},
            "esperado": 404
        }
    ]
    
    for caso in casos_validacion:
        print(f"\n   Probando: {caso['nombre']}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{BASE_URL}{ENDPOINT}",
                    json=caso['datos'],
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == caso['esperado']:
                    print(f"   ✅ Correcto: {response.status_code}")
                else:
                    print(f"   ❌ Error: esperado {caso['esperado']}, recibido {response.status_code}")
                    
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

async def main():
    """Función principal"""
    print("🚀 Prueba Simplificada del endpoint /analyze-jira-confluence")
    print("=" * 70)
    print(f"Servidor: {BASE_URL}")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Verificar servidor
    if not await verificar_servidor():
        print("\n❌ No se puede continuar sin servidor funcionando")
        return
    
    print(f"\n📝 Se probarán {len(EJEMPLOS_SIMPLIFICADOS)} ejemplos simplificados")
    
    # Probar cada ejemplo
    for i, ejemplo in enumerate(EJEMPLOS_SIMPLIFICADOS, 1):
        print(f"\n{'='*70}")
        print(f"Ejemplo {i}/{len(EJEMPLOS_SIMPLIFICADOS)}")
        await probar_ejemplo_simplificado(ejemplo)
    
    # Probar validación
    await probar_validacion()
    
    print(f"\n{'='*70}")
    print("🏁 Todas las pruebas completadas")
    print("\n💡 Parámetros Simplificados:")
    print("   • jira_issue_id (requerido): ID del issue de Jira")
    print("   • confluence_space_key (requerido): Espacio de Confluence")
    print("   • test_plan_title (opcional): Título personalizado del plan")
    print("\n🎯 Valores por Defecto:")
    print("   • Estrategia: comprehensive")
    print("   • Automatización: habilitada")
    print("   • Rendimiento: deshabilitado")
    print("   • Seguridad: habilitada")
    print("   • Título: se genera automáticamente si no se proporciona")

if __name__ == "__main__":
    asyncio.run(main())
