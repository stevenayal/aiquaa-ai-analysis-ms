#!/usr/bin/env python3
"""
Script de prueba para el endpoint /analyze-jira-confluence con parámetros en español
"""

import asyncio
import json
import httpx
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8000"
ENDPOINT = "/analyze-jira-confluence"

# Ejemplos con parámetros en español
EJEMPLOS_ESPAÑOL = [
    {
        "nombre": "Mínimo - Solo Parámetros Requeridos",
        "datos": {
            "id_issue_jira": "PROJ-123",
            "espacio_confluence": "QA"
        }
    },
    {
        "nombre": "Con Título Personalizado",
        "datos": {
            "id_issue_jira": "AUTH-001",
            "espacio_confluence": "QA",
            "titulo_plan_pruebas": "Plan de Pruebas - Sistema de Autenticación"
        }
    },
    {
        "nombre": "Tarea de Integración",
        "datos": {
            "id_issue_jira": "API-002",
            "espacio_confluence": "DEV",
            "titulo_plan_pruebas": "Plan de Pruebas - Integración API de Pagos"
        }
    },
    {
        "nombre": "Bug de Rendimiento",
        "datos": {
            "id_issue_jira": "PERF-003",
            "espacio_confluence": "QA",
            "titulo_plan_pruebas": "Plan de Pruebas - Optimización de Rendimiento"
        }
    }
]

async def probar_ejemplo_espanol(ejemplo):
    """Probar un ejemplo con parámetros en español"""
    print(f"\n🧪 Probando: {ejemplo['nombre']}")
    print("-" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print(f"📤 Enviando petición...")
            print(f"   ID Issue Jira: {ejemplo['datos']['id_issue_jira']}")
            print(f"   Espacio Confluence: {ejemplo['datos']['espacio_confluence']}")
            if 'titulo_plan_pruebas' in ejemplo['datos']:
                print(f"   Título Plan Pruebas: {ejemplo['datos']['titulo_plan_pruebas']}")
            else:
                print(f"   Título Plan Pruebas: (se generará automáticamente)")
            
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
                
                # Mostrar resumen con nombres en español
                print(f"\n📊 Resumen del Plan de Pruebas:")
                print(f"   ID del Análisis: {result.get('id_analisis', 'N/A')}")
                print(f"   ID Issue Jira: {result.get('id_issue_jira', 'N/A')}")
                print(f"   Espacio Confluence: {result.get('espacio_confluence', 'N/A')}")
                print(f"   Título del Plan: {result.get('titulo_plan_pruebas', 'N/A')}")
                print(f"   Estado: {result.get('estado', 'N/A')}")
                print(f"   Secciones del Plan: {len(result.get('secciones_plan_pruebas', []))}")
                print(f"   Fases de Ejecución: {len(result.get('fases_ejecucion', []))}")
                print(f"   Casos de Prueba: {result.get('total_casos_prueba', 0)}")
                print(f"   Duración Estimada: {result.get('duracion_estimada', 'N/A')}")
                print(f"   Nivel de Riesgo: {result.get('nivel_riesgo', 'N/A')}")
                print(f"   Puntuación de Confianza: {result.get('puntuacion_confianza', 0):.2f}")
                print(f"   Tiempo de Procesamiento: {result.get('processing_time', 0):.2f} segundos")
                
                # Mostrar secciones del plan
                secciones = result.get('secciones_plan_pruebas', [])
                if secciones:
                    print(f"\n📋 Secciones del Plan:")
                    for seccion in secciones:
                        print(f"   • {seccion.get('titulo', 'Sin título')}")
                
                # Mostrar fases de ejecución
                fases = result.get('fases_ejecucion', [])
                if fases:
                    print(f"\n⏱️ Fases de Ejecución:")
                    for fase in fases:
                        print(f"   • {fase.get('nombre_fase', 'Sin nombre')} ({fase.get('duracion', 'N/A')})")
                        print(f"     Casos: {fase.get('cantidad_casos_prueba', 0)}, Responsable: {fase.get('responsable', 'N/A')}")
                
                # Mostrar algunos casos de prueba
                casos_prueba = result.get('casos_prueba', [])
                if casos_prueba:
                    print(f"\n🧪 Casos de Prueba (primeros 3):")
                    for i, caso in enumerate(casos_prueba[:3], 1):
                        print(f"   {i}. {caso.get('title', 'Sin título')}")
                        print(f"      Tipo: {caso.get('test_type', 'N/A')}, Prioridad: {caso.get('priority', 'N/A')}")
                        print(f"      Automatización: {caso.get('automation_potential', 'N/A')}")
                
                # Mostrar análisis de cobertura
                cobertura = result.get('analisis_cobertura', {})
                if cobertura:
                    print(f"\n📈 Análisis de Cobertura:")
                    for key, value in cobertura.items():
                        print(f"   • {key}: {value}")
                
                # Mostrar potencial de automatización
                automatizacion = result.get('potencial_automatizacion', {})
                if automatizacion:
                    print(f"\n🤖 Potencial de Automatización:")
                    for key, value in automatizacion.items():
                        print(f"   • {key}: {value}")
                
                # Guardar resultado en archivo
                filename = f"resultado_espanol_{ejemplo['datos']['id_issue_jira'].lower()}_{int(datetime.now().timestamp())}.json"
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
            "nombre": "ID Issue Jira vacío",
            "datos": {"id_issue_jira": "", "espacio_confluence": "QA"},
            "esperado": 422
        },
        {
            "nombre": "Espacio Confluence vacío",
            "datos": {"id_issue_jira": "PROJ-123", "espacio_confluence": ""},
            "esperado": 422
        },
        {
            "nombre": "Issue no encontrado",
            "datos": {"id_issue_jira": "INVALID-999", "espacio_confluence": "QA"},
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
    print("🚀 Prueba del endpoint /analyze-jira-confluence con parámetros en español")
    print("=" * 70)
    print(f"Servidor: {BASE_URL}")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Verificar servidor
    if not await verificar_servidor():
        print("\n❌ No se puede continuar sin servidor funcionando")
        return
    
    print(f"\n📝 Se probarán {len(EJEMPLOS_ESPAÑOL)} ejemplos con parámetros en español")
    
    # Probar cada ejemplo
    for i, ejemplo in enumerate(EJEMPLOS_ESPAÑOL, 1):
        print(f"\n{'='*70}")
        print(f"Ejemplo {i}/{len(EJEMPLOS_ESPAÑOL)}")
        await probar_ejemplo_espanol(ejemplo)
    
    # Probar validación
    await probar_validacion()
    
    print(f"\n{'='*70}")
    print("🏁 Todas las pruebas completadas")
    print("\n💡 Parámetros en Español:")
    print("   • id_issue_jira (requerido): ID del issue de Jira")
    print("   • espacio_confluence (requerido): Espacio de Confluence")
    print("   • titulo_plan_pruebas (opcional): Título personalizado del plan")
    print("\n🎯 Respuesta en Español:")
    print("   • id_analisis: ID único del análisis")
    print("   • id_issue_jira: ID del issue analizado")
    print("   • espacio_confluence: Espacio de Confluence")
    print("   • titulo_plan_pruebas: Título del plan")
    print("   • estado: Estado del análisis")
    print("   • secciones_plan_pruebas: Secciones del plan")
    print("   • fases_ejecucion: Fases de ejecución")
    print("   • casos_prueba: Casos de prueba generados")
    print("   • total_casos_prueba: Total de casos")
    print("   • duracion_estimada: Duración estimada")
    print("   • nivel_riesgo: Nivel de riesgo")
    print("   • puntuacion_confianza: Puntuación de confianza")
    print("   • contenido_confluence: Contenido para Confluence")
    print("   • analisis_cobertura: Análisis de cobertura")
    print("   • potencial_automatizacion: Potencial de automatización")

if __name__ == "__main__":
    asyncio.run(main())
