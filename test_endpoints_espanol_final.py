#!/usr/bin/env python3
"""
Script de prueba final para todos los endpoints en español
"""

import asyncio
import json
import httpx
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8000"

# Ejemplos para cada endpoint en español
EJEMPLOS_ENDPOINTS_ESPAÑOL = {
    "/analizar": {
        "nombre": "Análisis de Contenido",
        "datos": {
            "id_contenido": "TC-001",
            "contenido": "Verificar que el usuario pueda iniciar sesión con credenciales válidas. Pasos: 1) Abrir la página de login, 2) Ingresar usuario válido, 3) Ingresar contraseña válida, 4) Hacer clic en 'Iniciar Sesión'. Resultado esperado: Usuario logueado exitosamente y redirigido al dashboard.",
            "tipo_contenido": "test_case",
            "nivel_analisis": "high"
        }
    },
    "/analizar-jira": {
        "nombre": "Análisis de Jira",
        "datos": {
            "id_work_item": "AUTH-123",
            "nivel_analisis": "high"
        }
    },
    "/generar-pruebas-avanzadas": {
        "nombre": "Generación Avanzada",
        "datos": {
            "requerimiento": "El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado.",
            "aplicacion": "SISTEMA_AUTH"
        }
    },
    "/analisis/requisitos/verificacion-istqb": {
        "nombre": "Análisis ISTQB",
        "datos": {
            "requirement_id": "REQ-001",
            "requirement_text": "El sistema debe permitir a los usuarios iniciar sesión con email y contraseña.",
            "context": {
                "producto": "Sistema de Autenticación",
                "modulo": "Login",
                "stakeholders": ["PO", "QA", "Dev"],
                "restricciones": ["PCI DSS", "LGPD"],
                "dependencias": ["API Clientes v2"]
            },
            "glossary": {
                "usuario": "Persona que accede al sistema",
                "autenticación": "Proceso de verificación de identidad"
            },
            "acceptance_template": "Dado [condición] cuando [acción] entonces [resultado]",
            "non_functional_expectations": ["Rendimiento", "Seguridad", "Usabilidad"]
        }
    },
    "/analizar-jira-confluence": {
        "nombre": "Análisis Jira-Confluence",
        "datos": {
            "id_issue_jira": "PROJ-123",
            "espacio_confluence": "QA",
            "titulo_plan_pruebas": "Plan de Pruebas - Autenticación de Usuarios"
        }
    }
}

async def probar_endpoint_espanol(endpoint: str, ejemplo: dict) -> dict:
    """Probar un endpoint en español"""
    print(f"\n🧪 Probando: {ejemplo['nombre']}")
    print(f"   Endpoint: {endpoint}")
    print("-" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print(f"📤 Enviando petición...")
            print(f"   Datos: {json.dumps(ejemplo['datos'], indent=2, ensure_ascii=False)}")
            
            start_time = datetime.now()
            response = await client.post(
                f"{BASE_URL}{endpoint}",
                json=ejemplo['datos'],
                headers={"Content-Type": "application/json"}
            )
            end_time = datetime.now()
            
            print(f"📥 Respuesta recibida en {(end_time - start_time).total_seconds():.2f} segundos")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Análisis completado exitosamente")
                
                # Mostrar resumen según el endpoint
                if endpoint == "/analizar":
                    print(f"\n📊 Resumen del Análisis:")
                    print(f"   ID del Análisis: {result.get('id_analisis', 'N/A')}")
                    print(f"   ID del Contenido: {result.get('id_contenido', 'N/A')}")
                    print(f"   Estado: {result.get('estado', 'N/A')}")
                    print(f"   Casos de Prueba: {len(result.get('casos_prueba', []))}")
                    print(f"   Sugerencias: {len(result.get('sugerencias', []))}")
                    print(f"   Puntuación de Confianza: {result.get('puntuacion_confianza', 0):.2f}")
                    print(f"   Tiempo de Procesamiento: {result.get('tiempo_procesamiento', 0):.2f} segundos")
                    
                elif endpoint == "/analizar-jira":
                    print(f"\n📊 Resumen del Análisis de Jira:")
                    print(f"   ID del Análisis: {result.get('id_analisis', 'N/A')}")
                    print(f"   ID del Work Item: {result.get('id_work_item', 'N/A')}")
                    print(f"   Estado: {result.get('estado', 'N/A')}")
                    print(f"   Casos de Prueba: {len(result.get('casos_prueba', []))}")
                    print(f"   Datos de Jira: {len(result.get('datos_jira', {}))} campos")
                    print(f"   Puntuación de Confianza: {result.get('puntuacion_confianza', 0):.2f}")
                    print(f"   Tiempo de Procesamiento: {result.get('tiempo_procesamiento', 0):.2f} segundos")
                    
                elif endpoint == "/generar-pruebas-avanzadas":
                    print(f"\n📊 Resumen de la Generación Avanzada:")
                    print(f"   ID de la Generación: {result.get('id_generacion', 'N/A')}")
                    print(f"   Aplicación: {result.get('aplicacion', 'N/A')}")
                    print(f"   Estado: {result.get('estado', 'N/A')}")
                    print(f"   Casos de Prueba: {len(result.get('casos_prueba', []))}")
                    print(f"   Puntuación de Confianza: {result.get('puntuacion_confianza', 0):.2f}")
                    print(f"   Tiempo de Procesamiento: {result.get('tiempo_procesamiento', 0):.2f} segundos")
                    
                elif endpoint == "/analisis/requisitos/verificacion-istqb":
                    print(f"\n📊 Resumen del Análisis ISTQB:")
                    print(f"   ID del Análisis: {result.get('id_analisis', 'N/A')}")
                    print(f"   ID del Requerimiento: {result.get('id_requerimiento', 'N/A')}")
                    print(f"   Puntuación de Calidad: {result.get('puntuacion_calidad', {})}")
                    print(f"   Issues Detectados: {len(result.get('issues', []))}")
                    print(f"   Criterios de Aceptación: {len(result.get('criterios_aceptacion', []))}")
                    print(f"   Tiempo de Procesamiento: {result.get('tiempo_procesamiento', 0):.2f} segundos")
                    
                elif endpoint == "/analizar-jira-confluence":
                    print(f"\n📊 Resumen del Plan de Pruebas:")
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
                filename = f"resultado_{endpoint.replace('/', '_')}_{ejemplo['nombre'].replace(' ', '_').lower()}_{int(datetime.now().timestamp())}.json"
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

async def verificar_servidor_espanol():
    """Verificar que el servidor esté funcionando con endpoint en español"""
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

async def main():
    """Función principal"""
    print("🚀 Prueba Final de Todos los Endpoints en Español")
    print("=" * 80)
    print(f"Servidor: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Verificar servidor
    if not await verificar_servidor_espanol():
        print("\n❌ No se puede continuar sin servidor funcionando")
        return
    
    resultados = {}
    total_ejemplos = len(EJEMPLOS_ENDPOINTS_ESPAÑOL)
    ejemplo_actual = 0
    
    print(f"\n📝 Se probarán {total_ejemplos} ejemplos en {len(EJEMPLOS_ENDPOINTS_ESPAÑOL)} endpoints")
    
    # Probar cada endpoint
    for endpoint, ejemplo in EJEMPLOS_ENDPOINTS_ESPAÑOL.items():
        print(f"\n{'='*80}")
        print(f"Endpoint: {endpoint}")
        print(f"{'='*80}")
        
        ejemplo_actual += 1
        print(f"\nEjemplo {ejemplo_actual}/{total_ejemplos}")
        
        resultado = await probar_endpoint_espanol(endpoint, ejemplo)
        resultados[endpoint] = resultado
    
    # Resumen final
    print(f"\n{'='*80}")
    print("🏁 Resumen Final")
    print(f"{'='*80}")
    
    total_exitosos = 0
    total_fallidos = 0
    
    for endpoint, resultado in resultados.items():
        if resultado.get('success', False):
            exitosos = 1
            fallidos = 0
        else:
            exitosos = 0
            fallidos = 1
        
        print(f"\n📊 {endpoint}:")
        print(f"   ✅ Exitosos: {exitosos}")
        print(f"   ❌ Fallidos: {fallidos}")
        
        total_exitosos += exitosos
        total_fallidos += fallidos
    
    print(f"\n📈 Total General:")
    print(f"   ✅ Exitosos: {total_exitosos}")
    print(f"   ❌ Fallidos: {total_fallidos}")
    print(f"   📊 Tasa de Éxito: {(total_exitosos / (total_exitosos + total_fallidos) * 100):.1f}%")
    
    print(f"\n💡 Endpoints en Español Implementados:")
    print("   • /analizar - Análisis de contenido")
    print("   • /analizar-jira - Análisis de Jira")
    print("   • /generar-pruebas-avanzadas - Generación avanzada")
    print("   • /analisis/requisitos/verificacion-istqb - Análisis ISTQB")
    print("   • /analizar-jira-confluence - Análisis Jira-Confluence")
    print("   • /salud - Health check")
    
    print(f"\n🎯 Parámetros en Español:")
    print("   • id_contenido, contenido, tipo_contenido, nivel_analisis")
    print("   • id_work_item, datos_jira, casos_prueba, sugerencias")
    print("   • analisis_cobertura, puntuacion_confianza, tiempo_procesamiento")
    print("   • secciones_plan_pruebas, fases_ejecucion, total_casos_prueba")
    print("   • duracion_estimada, nivel_riesgo, contenido_confluence")
    
    print(f"\n🌐 Swagger UI actualizado:")
    print("   • http://localhost:8000/docs")
    print("   • http://localhost:8000/redoc")

if __name__ == "__main__":
    asyncio.run(main())
