#!/usr/bin/env python3
"""
Script de prueba comprehensivo para todos los endpoints con parámetros en español
"""

import asyncio
import json
import httpx
from datetime import datetime
from typing import Dict, Any, List

# Configuración del servidor
BASE_URL = "http://localhost:8000"

# Ejemplos para cada endpoint
EJEMPLOS_ENDPOINTS = {
    "/analyze": [
        {
            "nombre": "Análisis de Caso de Prueba",
            "datos": {
                "id_contenido": "TC-001",
                "contenido": "Verificar que el usuario pueda iniciar sesión con credenciales válidas. Pasos: 1) Abrir la página de login, 2) Ingresar usuario válido, 3) Ingresar contraseña válida, 4) Hacer clic en 'Iniciar Sesión'. Resultado esperado: Usuario logueado exitosamente y redirigido al dashboard.",
                "tipo_contenido": "test_case",
                "nivel_analisis": "high"
            }
        },
        {
            "nombre": "Análisis de Requerimiento",
            "datos": {
                "id_contenido": "REQ-001",
                "contenido": "El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado.",
                "tipo_contenido": "requirement",
                "nivel_analisis": "comprehensive"
            }
        },
        {
            "nombre": "Análisis de Historia de Usuario",
            "datos": {
                "id_contenido": "US-001",
                "contenido": "Como usuario del sistema, quiero poder recuperar mi contraseña olvidada para poder acceder a mi cuenta nuevamente. Criterios de aceptación: 1) El usuario debe poder solicitar recuperación desde la página de login, 2) Debe recibir un email con instrucciones, 3) Debe poder establecer una nueva contraseña, 4) La nueva contraseña debe cumplir con los criterios de seguridad.",
                "tipo_contenido": "user_story",
                "nivel_analisis": "high"
            }
        }
    ],
    "/analyze-jira": [
        {
            "nombre": "Análisis de Work Item",
            "datos": {
                "id_work_item": "AUTH-123",
                "nivel_analisis": "high"
            }
        },
        {
            "nombre": "Análisis de Epic",
            "datos": {
                "id_work_item": "EPIC-001",
                "nivel_analisis": "comprehensive"
            }
        }
    ],
    "/generate-advanced-tests": [
        {
            "nombre": "Generación Avanzada - Autenticación",
            "datos": {
                "requerimiento": "El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado. El sistema debe implementar bloqueo de cuenta después de 3 intentos fallidos y permitir recuperación de contraseña.",
                "aplicacion": "SISTEMA_AUTH"
            }
        },
        {
            "nombre": "Generación Avanzada - E-commerce",
            "datos": {
                "requerimiento": "El sistema de e-commerce debe permitir a los usuarios agregar productos al carrito, modificar cantidades, aplicar cupones de descuento, calcular impuestos según la ubicación, procesar pagos con múltiples métodos (tarjeta, PayPal, transferencia), generar órdenes y enviar confirmaciones por email.",
                "aplicacion": "ECOMMERCE_PLATFORM"
            }
        }
    ],
    "/analysis/requirements/istqb-check": [
        {
            "nombre": "Análisis ISTQB - Requerimiento Simple",
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
        {
            "nombre": "Análisis ISTQB - Requerimiento Complejo",
            "datos": {
                "requirement_id": "REQ-002",
                "requirement_text": "El sistema de pagos debe procesar transacciones de tarjeta de crédito de manera segura, validando la información del usuario contra la base de datos, verificando fondos disponibles, aplicando reglas de negocio específicas por tipo de transacción, generando logs de auditoría completos y notificando al usuario del resultado dentro de 5 segundos.",
                "context": {
                    "producto": "Sistema de Pagos",
                    "modulo": "Procesamiento de Transacciones",
                    "stakeholders": ["PO", "QA", "Dev", "Compliance"],
                    "restricciones": ["PCI DSS", "SOX", "GDPR"],
                    "dependencias": ["Gateway de Pagos", "Sistema de Auditoría"]
                },
                "glossary": {
                    "transacción": "Operación de pago entre usuario y comercio",
                    "auditoría": "Registro de actividades para cumplimiento",
                    "gateway": "Servicio externo de procesamiento de pagos"
                },
                "acceptance_template": "Dado [condición] cuando [acción] entonces [resultado]",
                "non_functional_expectations": ["Rendimiento", "Seguridad", "Confiabilidad", "Auditabilidad"]
            }
        }
    ],
    "/analyze-jira-confluence": [
        {
            "nombre": "Análisis Jira-Confluence - Plan de Pruebas",
            "datos": {
                "id_issue_jira": "PROJ-123",
                "espacio_confluence": "QA",
                "titulo_plan_pruebas": "Plan de Pruebas - Autenticación de Usuarios"
            }
        },
        {
            "nombre": "Análisis Jira-Confluence - Solo Parámetros Requeridos",
            "datos": {
                "id_issue_jira": "AUTH-001",
                "espacio_confluence": "QA"
            }
        },
        {
            "nombre": "Análisis Jira-Confluence - Epic Complejo",
            "datos": {
                "id_issue_jira": "EPIC-001",
                "espacio_confluence": "PRODUCT",
                "titulo_plan_pruebas": "Plan de Pruebas - Nueva Funcionalidad de E-commerce"
            }
        }
    ]
}

# Casos de validación
CASOS_VALIDACION = [
    {
        "nombre": "ID Contenido Vacío",
        "endpoint": "/analyze",
        "datos": {
            "id_contenido": "",
            "contenido": "Contenido de prueba",
            "tipo_contenido": "test_case"
        },
        "esperado": 422
    },
    {
        "nombre": "Contenido Muy Corto",
        "endpoint": "/analyze",
        "datos": {
            "id_contenido": "TC-001",
            "contenido": "Corto",
            "tipo_contenido": "test_case"
        },
        "esperado": 422
    },
    {
        "nombre": "Tipo de Contenido Inválido",
        "endpoint": "/analyze",
        "datos": {
            "id_contenido": "TC-001",
            "contenido": "Contenido de prueba válido con suficiente longitud para pasar la validación",
            "tipo_contenido": "invalid_type"
        },
        "esperado": 422
    },
    {
        "nombre": "ID Work Item Vacío",
        "endpoint": "/analyze-jira",
        "datos": {
            "id_work_item": "",
            "nivel_analisis": "high"
        },
        "esperado": 422
    },
    {
        "nombre": "Requerimiento Vacío",
        "endpoint": "/generate-advanced-tests",
        "datos": {
            "requerimiento": "",
            "aplicacion": "TEST"
        },
        "esperado": 422
    },
    {
        "nombre": "Aplicación Vacía",
        "endpoint": "/generate-advanced-tests",
        "datos": {
            "requerimiento": "Requerimiento válido con suficiente longitud para pasar la validación",
            "aplicacion": ""
        },
        "esperado": 422
    }
]

async def probar_endpoint(endpoint: str, ejemplo: Dict[str, Any]) -> Dict[str, Any]:
    """Probar un endpoint con un ejemplo específico"""
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
                if endpoint == "/analyze":
                    print(f"\n📊 Resumen del Análisis:")
                    print(f"   ID del Análisis: {result.get('id_analisis', 'N/A')}")
                    print(f"   ID del Contenido: {result.get('id_contenido', 'N/A')}")
                    print(f"   Estado: {result.get('estado', 'N/A')}")
                    print(f"   Casos de Prueba: {len(result.get('casos_prueba', []))}")
                    print(f"   Sugerencias: {len(result.get('sugerencias', []))}")
                    print(f"   Puntuación de Confianza: {result.get('puntuacion_confianza', 0):.2f}")
                    print(f"   Tiempo de Procesamiento: {result.get('tiempo_procesamiento', 0):.2f} segundos")
                    
                elif endpoint == "/analyze-jira":
                    print(f"\n📊 Resumen del Análisis de Jira:")
                    print(f"   ID del Análisis: {result.get('id_analisis', 'N/A')}")
                    print(f"   ID del Work Item: {result.get('id_work_item', 'N/A')}")
                    print(f"   Estado: {result.get('estado', 'N/A')}")
                    print(f"   Casos de Prueba: {len(result.get('casos_prueba', []))}")
                    print(f"   Datos de Jira: {len(result.get('datos_jira', {}))} campos")
                    print(f"   Puntuación de Confianza: {result.get('puntuacion_confianza', 0):.2f}")
                    print(f"   Tiempo de Procesamiento: {result.get('tiempo_procesamiento', 0):.2f} segundos")
                    
                elif endpoint == "/generate-advanced-tests":
                    print(f"\n📊 Resumen de la Generación Avanzada:")
                    print(f"   ID de la Generación: {result.get('id_generacion', 'N/A')}")
                    print(f"   Aplicación: {result.get('aplicacion', 'N/A')}")
                    print(f"   Estado: {result.get('estado', 'N/A')}")
                    print(f"   Casos de Prueba: {len(result.get('casos_prueba', []))}")
                    print(f"   Puntuación de Confianza: {result.get('puntuacion_confianza', 0):.2f}")
                    print(f"   Tiempo de Procesamiento: {result.get('tiempo_procesamiento', 0):.2f} segundos")
                    
                elif endpoint == "/analysis/requirements/istqb-check":
                    print(f"\n📊 Resumen del Análisis ISTQB:")
                    print(f"   ID del Análisis: {result.get('id_analisis', 'N/A')}")
                    print(f"   ID del Requerimiento: {result.get('id_requerimiento', 'N/A')}")
                    print(f"   Puntuación de Calidad: {result.get('puntuacion_calidad', {})}")
                    print(f"   Issues Detectados: {len(result.get('issues', []))}")
                    print(f"   Criterios de Aceptación: {len(result.get('criterios_aceptacion', []))}")
                    print(f"   Tiempo de Procesamiento: {result.get('tiempo_procesamiento', 0):.2f} segundos")
                    
                elif endpoint == "/analyze-jira-confluence":
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

async def probar_validacion(caso: Dict[str, Any]) -> Dict[str, Any]:
    """Probar un caso de validación"""
    print(f"\n🔍 Probando validación: {caso['nombre']}")
    print(f"   Endpoint: {caso['endpoint']}")
    print(f"   Esperado: {caso['esperado']}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}{caso['endpoint']}",
                json=caso['datos'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == caso['esperado']:
                print(f"   ✅ Correcto: {response.status_code}")
                return {"success": True, "status_code": response.status_code}
            else:
                print(f"   ❌ Error: esperado {caso['esperado']}, recibido {response.status_code}")
                return {"success": False, "expected": caso['esperado'], "actual": response.status_code}
                
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

async def verificar_servidor():
    """Verificar que el servidor esté funcionando"""
    print("🔍 Verificando servidor...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            
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
    print("🚀 Prueba Comprehensiva de Todos los Endpoints - Parámetros en Español")
    print("=" * 80)
    print(f"Servidor: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Verificar servidor
    if not await verificar_servidor():
        print("\n❌ No se puede continuar sin servidor funcionando")
        return
    
    resultados = {}
    total_ejemplos = sum(len(ejemplos) for ejemplos in EJEMPLOS_ENDPOINTS.values())
    ejemplo_actual = 0
    
    print(f"\n📝 Se probarán {total_ejemplos} ejemplos en {len(EJEMPLOS_ENDPOINTS)} endpoints")
    
    # Probar cada endpoint
    for endpoint, ejemplos in EJEMPLOS_ENDPOINTS.items():
        print(f"\n{'='*80}")
        print(f"Endpoint: {endpoint}")
        print(f"{'='*80}")
        
        resultados[endpoint] = []
        
        for ejemplo in ejemplos:
            ejemplo_actual += 1
            print(f"\nEjemplo {ejemplo_actual}/{total_ejemplos}")
            
            resultado = await probar_endpoint(endpoint, ejemplo)
            resultados[endpoint].append(resultado)
    
    # Probar validaciones
    print(f"\n{'='*80}")
    print("Validaciones")
    print(f"{'='*80}")
    
    for caso in CASOS_VALIDACION:
        resultado = await probar_validacion(caso)
        if 'validaciones' not in resultados:
            resultados['validaciones'] = []
        resultados['validaciones'].append(resultado)
    
    # Resumen final
    print(f"\n{'='*80}")
    print("🏁 Resumen Final")
    print(f"{'='*80}")
    
    total_exitosos = 0
    total_fallidos = 0
    
    for endpoint, resultados_endpoint in resultados.items():
        if endpoint == 'validaciones':
            continue
            
        exitosos = sum(1 for r in resultados_endpoint if r.get('success', False))
        fallidos = len(resultados_endpoint) - exitosos
        
        print(f"\n📊 {endpoint}:")
        print(f"   ✅ Exitosos: {exitosos}")
        print(f"   ❌ Fallidos: {fallidos}")
        
        total_exitosos += exitosos
        total_fallidos += fallidos
    
    print(f"\n📈 Total General:")
    print(f"   ✅ Exitosos: {total_exitosos}")
    print(f"   ❌ Fallidos: {total_fallidos}")
    print(f"   📊 Tasa de Éxito: {(total_exitosos / (total_exitosos + total_fallidos) * 100):.1f}%")
    
    print(f"\n💡 Parámetros en Español Implementados:")
    print("   • /analyze: id_contenido, contenido, tipo_contenido, nivel_analisis")
    print("   • /analyze-jira: id_work_item, nivel_analisis")
    print("   • /generate-advanced-tests: requerimiento, aplicacion")
    print("   • /analysis/requirements/istqb-check: requirement_id, requirement_text, context, glossary")
    print("   • /analyze-jira-confluence: id_issue_jira, espacio_confluence, titulo_plan_pruebas")
    print("   • /health: estado, componentes")
    
    print(f"\n🎯 Respuestas en Español:")
    print("   • id_analisis, estado, casos_prueba, sugerencias")
    print("   • analisis_cobertura, puntuacion_confianza, tiempo_procesamiento")
    print("   • datos_jira, secciones_plan_pruebas, fases_ejecucion")
    print("   • total_casos_prueba, duracion_estimada, nivel_riesgo")
    print("   • contenido_confluence, analisis_cobertura, potencial_automatizacion")

if __name__ == "__main__":
    asyncio.run(main())
