#!/usr/bin/env python3
"""
Script de prueba para el endpoint simplificado de Jira-Confluence
"""

import asyncio
import json
import httpx
from datetime import datetime

# Configuración del servidor
BASE_URL = "https://ia-analisis-production.up.railway.app"
ENDPOINT_SIMPLE = "/analizar-jira-confluence-simple"
ENDPOINT_ORIGINAL = "/analizar-jira-confluence"

# Ejemplos de prueba
EJEMPLOS_PRUEBA = [
    {
        "nombre": "Prueba Simplificada - KAN-6",
        "datos": {
            "id_issue_jira": "KAN-6",
            "espacio_confluence": "QA",
            "titulo_plan_pruebas": "Plan de Pruebas - Autenticación de Usuarios"
        }
    },
    {
        "nombre": "Prueba Simplificada - Solo Parámetros Requeridos",
        "datos": {
            "id_issue_jira": "KAN-6",
            "espacio_confluence": "QA"
        }
    }
]

async def probar_endpoint_simple(ejemplo: dict) -> dict:
    """Probar el endpoint simplificado"""
    print(f"\n🧪 Probando: {ejemplo['nombre']}")
    print(f"   Endpoint: {ENDPOINT_SIMPLE}")
    print("-" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:  # 3 minutos de timeout
            print(f"📤 Enviando petición...")
            print(f"   Datos: {json.dumps(ejemplo['datos'], indent=2, ensure_ascii=False)}")
            
            start_time = datetime.now()
            response = await client.post(
                f"{BASE_URL}{ENDPOINT_SIMPLE}",
                json=ejemplo['datos'],
                headers={"Content-Type": "application/json"}
            )
            end_time = datetime.now()
            
            print(f"📥 Respuesta recibida en {(end_time - start_time).total_seconds():.2f} segundos")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Análisis simplificado completado exitosamente")
                
                print(f"\n📊 Resumen del Plan de Pruebas Simplificado:")
                print(f"   ID del Análisis: {result.get('id_analisis', 'N/A')}")
                print(f"   ID del Issue Jira: {result.get('id_issue_jira', 'N/A')}")
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
                
                # Mostrar algunos casos de prueba
                casos_prueba = result.get('casos_prueba', [])
                if casos_prueba:
                    print(f"\n🧪 Casos de Prueba (primeros 3):")
                    for i, caso in enumerate(casos_prueba[:3], 1):
                        print(f"   {i}. {caso.get('titulo', 'Sin título')}")
                        print(f"      Tipo: {caso.get('tipo_prueba', 'N/A')}, Prioridad: {caso.get('prioridad', 'N/A')}")
                        print(f"      Automatización: {caso.get('potencial_automatizacion', 'N/A')}")
                
                # Guardar resultado en archivo
                filename = f"resultado_simple_{ejemplo['nombre'].replace(' ', '_').lower()}_{int(datetime.now().timestamp())}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                print(f"\n💾 Resultado guardado en: {filename}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": (end_time - start_time).total_seconds(),
                    "result": result
                }
                
            else:
                print(f"❌ Error en la respuesta:")
                print(f"   Status: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "response_time": (end_time - start_time).total_seconds(),
                    "error": response.text
                }
                
    except httpx.ConnectError:
        print("❌ No se pudo conectar al servidor")
        return {"success": False, "error": "Connection error"}
    except httpx.TimeoutException:
        print("❌ Timeout en la petición")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return {"success": False, "error": str(e)}

async def verificar_servidor():
    """Verificar que el servidor esté funcionando"""
    print("🔍 Verificando servidor...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/salud")
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Servidor funcionando correctamente")
                print(f"   Estado: {health_data.get('estado', 'unknown')}")
                print(f"   Componentes: {health_data.get('componentes', {})}")
                return True
            else:
                print(f"❌ Servidor no disponible: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error verificando servidor: {str(e)}")
        return False

async def verificar_diagnostico_llm():
    """Verificar el diagnóstico del LLM"""
    print("🔍 Verificando diagnóstico del LLM...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/diagnostico-llm")
            
            if response.status_code == 200:
                diag_data = response.json()
                print("✅ Diagnóstico del LLM:")
                print(f"   Estado: {diag_data.get('status', 'unknown')}")
                print(f"   Conexión LLM: {diag_data.get('llm_connection', 'unknown')}")
                print(f"   Tiempo de Respuesta: {diag_data.get('response_time', 0):.2f} segundos")
                return True
            else:
                print(f"❌ Diagnóstico no disponible: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error verificando diagnóstico: {str(e)}")
        return False

async def main():
    """Función principal"""
    print("🚀 Prueba del Endpoint Simplificado de Jira-Confluence")
    print("=" * 80)
    print(f"Servidor: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Verificar servidor
    if not await verificar_servidor():
        print("\n❌ No se puede continuar sin servidor funcionando")
        return
    
    # Verificar diagnóstico del LLM
    await verificar_diagnostico_llm()
    
    resultados = []
    total_ejemplos = len(EJEMPLOS_PRUEBA)
    
    print(f"\n📝 Se probarán {total_ejemplos} ejemplos")
    
    # Probar cada ejemplo
    for i, ejemplo in enumerate(EJEMPLOS_PRUEBA, 1):
        print(f"\n{'='*80}")
        print(f"Ejemplo {i}/{total_ejemplos}")
        print(f"{'='*80}")
        
        resultado = await probar_endpoint_simple(ejemplo)
        resultados.append(resultado)
    
    # Resumen final
    print(f"\n{'='*80}")
    print("🏁 Resumen Final")
    print(f"{'='*80}")
    
    total_exitosos = sum(1 for r in resultados if r.get('success', False))
    total_fallidos = len(resultados) - total_exitosos
    
    print(f"\n📈 Total General:")
    print(f"   ✅ Exitosos: {total_exitosos}")
    print(f"   ❌ Fallidos: {total_fallidos}")
    print(f"   📊 Tasa de Éxito: {(total_exitosos / len(resultados) * 100):.1f}%")
    
    print(f"\n💡 Endpoint Simplificado:")
    print("   • /analizar-jira-confluence-simple - Versión simplificada")
    print("   • Timeout reducido a 2 minutos")
    print("   • Prompt más corto y directo")
    print("   • Máximo 5 casos de prueba")
    print("   • Plan de pruebas básico")
    
    print(f"\n🔧 Solución al Error 500:")
    print("   • Usar endpoint simplificado para evitar timeouts")
    print("   • Prompt más corto reduce tiempo de procesamiento")
    print("   • Timeout de 2 minutos en lugar de 5")
    print("   • Generación básica pero funcional")
    
    print(f"\n📝 Comando para probar:")
    print(f"curl -X POST '{BASE_URL}{ENDPOINT_SIMPLE}' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "id_issue_jira": "KAN-6",')
    print('    "espacio_confluence": "QA"')
    print("  }'")

if __name__ == "__main__":
    asyncio.run(main())
