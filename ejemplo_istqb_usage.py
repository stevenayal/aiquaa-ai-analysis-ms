#!/usr/bin/env python3
"""
Ejemplo de uso del sistema ISTQB para generación de casos de prueba
Este script demuestra cómo utilizar la API para generar casos de prueba
aplicando técnicas ISTQB Foundation Level.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuración de la API
API_BASE_URL = "http://localhost:8000"
ISTQB_ENDPOINT = f"{API_BASE_URL}/generate-istqb-tests"

def generar_casos_istqb(configuracion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera casos de prueba usando técnicas ISTQB
    
    Args:
        configuracion: Configuración del sistema para generar casos
        
    Returns:
        Respuesta de la API con casos generados
    """
    try:
        print(f"🚀 Iniciando generación de casos para: {configuracion['programa']}")
        print(f"📋 Módulos: {', '.join(configuracion['modulos'])}")
        print(f"🔬 Técnicas activas: {sum(1 for v in configuracion['tecnicas'].values() if v)}")
        
        # Realizar petición a la API
        response = requests.post(
            ISTQB_ENDPOINT,
            json=configuracion,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"✅ Generación completada exitosamente")
            print(f"📊 Casos CSV generados: {len(resultado['csv_cases'])}")
            print(f"📝 Fichas detalladas: {len(resultado['fichas'])}")
            print(f"🔧 Artefactos técnicos: {len(resultado['artefactos_tecnicos'])}")
            print(f"⏱️  Tiempo de procesamiento: {resultado['processing_time']:.2f}s")
            print(f"🎯 Puntuación de confianza: {resultado['confidence_score']:.2f}")
            return resultado
        else:
            print(f"❌ Error en la generación: {response.status_code}")
            print(f"📄 Detalles: {response.text}")
            return {}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return {}
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return {}

def mostrar_casos_csv(casos: list, limite: int = 10):
    """Muestra los primeros casos CSV generados"""
    print(f"\n📋 Primeros {min(limite, len(casos))} casos CSV:")
    print("-" * 80)
    for i, caso in enumerate(casos[:limite], 1):
        print(f"{i:2d}. {caso}")
    if len(casos) > limite:
        print(f"... y {len(casos) - limite} casos más")

def mostrar_fichas(fichas: list, limite: int = 3):
    """Muestra las primeras fichas detalladas"""
    print(f"\n📝 Primeras {min(limite, len(fichas))} fichas detalladas:")
    print("-" * 80)
    for i, ficha in enumerate(fichas[:limite], 1):
        print(f"\n--- FICHA {i} ---")
        print(ficha)
    if len(fichas) > limite:
        print(f"\n... y {len(fichas) - limite} fichas más")

def mostrar_artefactos(artefactos: Dict[str, Any]):
    """Muestra los artefactos técnicos generados"""
    print(f"\n🔧 Artefactos técnicos generados:")
    print("-" * 80)
    for tecnica, contenido in artefactos.items():
        print(f"\n📌 {tecnica.upper()}:")
        if isinstance(contenido, str):
            print(f"   {contenido}")
        elif isinstance(contenido, dict):
            for key, value in contenido.items():
                print(f"   {key}: {value}")
        else:
            print(f"   {contenido}")

def ejemplo_sistema_autenticacion():
    """Ejemplo: Sistema de autenticación"""
    configuracion = {
        "programa": "SISTEMA_AUTH",
        "dominio": "Autenticación de usuarios con validación de credenciales y control de acceso",
        "modulos": ["AUTORIZACION", "VALIDACION", "AUDITORIA", "RECUPERACION"],
        "factores": {
            "TIPO_USUARIO": ["ADMIN", "USER", "GUEST", "SERVICE"],
            "ESTADO_CREDENCIAL": ["VALIDA", "INVALIDA", "EXPIRADA", "BLOQUEADA"],
            "INTENTOS": ["OK", "ERROR_TIPO_1", "ERROR_TIPO_2", "TIMEOUT"],
            "METODO_AUTH": ["PASSWORD", "TOKEN", "BIOMETRICO", "SSO"]
        },
        "limites": {
            "CAMPO_USUARIO_len": {"min": 3, "max": 50},
            "CAMPO_PASSWORD_len": {"min": 8, "max": 128},
            "REINTENTOS": 3,
            "TIMEOUT_MS": 5000,
            "TOKEN_EXPIRY_HOURS": 24
        },
        "reglas": [
            "R1: si TIPO_USUARIO=ADMIN y ESTADO_CREDENCIAL=VALIDA -> ACCESO_TOTAL",
            "R2: si TIPO_USUARIO=USER y ESTADO_CREDENCIAL=VALIDA -> ACCESO_LIMITADO",
            "R3: si ESTADO_CREDENCIAL=EXPIRADA -> REQUERIR_RENOVACION",
            "R4: si INTENTOS=TIMEOUT -> reintentar 1 vez y marcar pendiente",
            "R5: si REINTENTOS supera límite -> bloquear y auditar",
            "R6: si METODO_AUTH=TOKEN y TOKEN_EXPIRY_HOURS>24 -> RECHAZAR"
        ],
        "tecnicas": {
            "equivalencia": True,
            "valores_limite": True,
            "tabla_decision": True,
            "transicion_estados": True,
            "arbol_clasificacion": True,
            "pairwise": True,
            "casos_uso": True,
            "error_guessing": True,
            "checklist": True
        },
        "priorizacion": "Riesgo",
        "cantidad_max": 200,
        "salida_plan_ejecucion": {
            "incluir": True,
            "formato": "cursor_playwright_mcp"
        }
    }
    
    print("🔐 EJEMPLO: Sistema de Autenticación")
    print("=" * 80)
    resultado = generar_casos_istqb(configuracion)
    
    if resultado:
        mostrar_casos_csv(resultado['csv_cases'])
        mostrar_fichas(resultado['fichas'])
        mostrar_artefactos(resultado['artefactos_tecnicos'])
    
    return resultado

def ejemplo_ecommerce():
    """Ejemplo: Sistema de e-commerce"""
    configuracion = {
        "programa": "ECOMMERCE_PLATFORM",
        "dominio": "Procesamiento de pedidos con validación de inventario y pagos",
        "modulos": ["INVENTARIO", "PAGOS", "ENVIO", "FACTURACION"],
        "factores": {
            "ESTADO_PRODUCTO": ["DISPONIBLE", "AGOTADO", "DESCONTINUADO", "RESERVADO"],
            "METODO_PAGO": ["TARJETA", "PAYPAL", "TRANSFERENCIA", "CRYPTO"],
            "ZONA_ENVIO": ["NACIONAL", "INTERNACIONAL", "RESTRINGIDA"],
            "TIPO_CLIENTE": ["NUEVO", "RECURRENTE", "VIP", "CORPORATIVO"]
        },
        "limites": {
            "CANTIDAD_MAX": 100,
            "MONTO_MAX": 10000,
            "TIEMPO_PROCESAMIENTO_MS": 30000,
            "STOCK_MINIMO": 5
        },
        "reglas": [
            "R1: si ESTADO_PRODUCTO=DISPONIBLE y CANTIDAD<=STOCK -> PROCESAR_PEDIDO",
            "R2: si ESTADO_PRODUCTO=AGOTADO -> MARCAR_COMO_AGOTADO",
            "R3: si METODO_PAGO=TARJETA -> VALIDAR_TARJETA",
            "R4: si ZONA_ENVIO=RESTRINGIDA -> REQUERIR_AUTORIZACION",
            "R5: si TIPO_CLIENTE=VIP -> APLICAR_DESCUENTO",
            "R6: si MONTO>MONTO_MAX -> REQUERIR_APROBACION_MANAGER"
        ],
        "tecnicas": {
            "equivalencia": True,
            "valores_limite": True,
            "tabla_decision": True,
            "transicion_estados": True,
            "arbol_clasificacion": False,
            "pairwise": True,
            "casos_uso": True,
            "error_guessing": True,
            "checklist": True
        },
        "priorizacion": "Riesgo",
        "cantidad_max": 150
    }
    
    print("\n🛒 EJEMPLO: Sistema de E-commerce")
    print("=" * 80)
    resultado = generar_casos_istqb(configuracion)
    
    if resultado:
        mostrar_casos_csv(resultado['csv_cases'])
        mostrar_fichas(resultado['fichas'])
        mostrar_artefactos(resultado['artefactos_tecnicos'])
    
    return resultado

def ejemplo_api_gateway():
    """Ejemplo: API Gateway"""
    configuracion = {
        "programa": "API_GATEWAY",
        "dominio": "Validación y enrutamiento de requests HTTP con control de acceso",
        "modulos": ["AUTHENTICATION", "RATE_LIMITING", "ROUTING", "LOGGING"],
        "factores": {
            "HTTP_METHOD": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "AUTH_STATUS": ["VALID", "INVALID", "EXPIRED", "MISSING"],
            "RATE_LIMIT": ["WITHIN_LIMIT", "EXCEEDED", "BLOCKED"],
            "ENDPOINT_TYPE": ["PUBLIC", "PRIVATE", "ADMIN", "WEBHOOK"]
        },
        "limites": {
            "REQUEST_SIZE_MAX": 10485760,  # 10MB
            "RATE_LIMIT_PER_MINUTE": 100,
            "TIMEOUT_MS": 5000,
            "MAX_HEADERS": 50
        },
        "reglas": [
            "R1: si AUTH_STATUS=VALID y RATE_LIMIT=WITHIN_LIMIT -> PROCESS_REQUEST",
            "R2: si AUTH_STATUS=INVALID -> RETURN_401",
            "R3: si RATE_LIMIT=EXCEEDED -> RETURN_429",
            "R4: si ENDPOINT_TYPE=ADMIN y AUTH_STATUS!=VALID -> RETURN_403",
            "R5: si REQUEST_SIZE>REQUEST_SIZE_MAX -> RETURN_413",
            "R6: si TIMEOUT_MS>TIMEOUT_MS -> RETURN_504"
        ],
        "tecnicas": {
            "equivalencia": True,
            "valores_limite": True,
            "tabla_decision": True,
            "transicion_estados": True,
            "arbol_clasificacion": False,
            "pairwise": True,
            "casos_uso": True,
            "error_guessing": True,
            "checklist": True
        },
        "priorizacion": "Impacto",
        "cantidad_max": 100
    }
    
    print("\n🌐 EJEMPLO: API Gateway")
    print("=" * 80)
    resultado = generar_casos_istqb(configuracion)
    
    if resultado:
        mostrar_casos_csv(resultado['csv_cases'])
        mostrar_fichas(resultado['fichas'])
        mostrar_artefactos(resultado['artefactos_tecnicos'])
    
    return resultado

def verificar_servicio():
    """Verifica que el servicio esté disponible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Servicio disponible - Estado: {health['status']}")
            print(f"🔧 Componentes: {health['components']}")
            return True
        else:
            print(f"❌ Servicio no disponible - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servicio: {e}")
        return False

def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("🎯 SISTEMA ISTQB - Generación de Casos de Prueba")
    print("=" * 80)
    
    # Verificar que el servicio esté disponible
    if not verificar_servicio():
        print("\n❌ No se puede continuar sin el servicio. Asegúrate de que esté ejecutándose.")
        return
    
    print("\n🚀 Iniciando ejemplos de generación de casos ISTQB...")
    
    # Ejecutar ejemplos
    ejemplos = [
        ejemplo_sistema_autenticacion,
        ejemplo_ecommerce,
        ejemplo_api_gateway
    ]
    
    resultados = []
    for ejemplo in ejemplos:
        try:
            resultado = ejemplo()
            resultados.append(resultado)
            time.sleep(2)  # Pausa entre ejemplos
        except KeyboardInterrupt:
            print("\n⏹️  Ejecución interrumpida por el usuario")
            break
        except Exception as e:
            print(f"\n❌ Error en ejemplo: {e}")
            continue
    
    # Resumen final
    print("\n📊 RESUMEN DE EJECUCIÓN")
    print("=" * 80)
    total_casos = sum(len(r.get('csv_cases', [])) for r in resultados if r)
    total_tiempo = sum(r.get('processing_time', 0) for r in resultados if r)
    promedio_confianza = sum(r.get('confidence_score', 0) for r in resultados if r) / len(resultados) if resultados else 0
    
    print(f"📋 Total de casos generados: {total_casos}")
    print(f"⏱️  Tiempo total de procesamiento: {total_tiempo:.2f}s")
    print(f"🎯 Puntuación promedio de confianza: {promedio_confianza:.2f}")
    print(f"✅ Ejemplos ejecutados exitosamente: {len([r for r in resultados if r])}")
    
    print("\n🎉 ¡Generación de casos ISTQB completada!")

if __name__ == "__main__":
    main()
