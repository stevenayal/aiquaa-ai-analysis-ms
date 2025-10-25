#!/usr/bin/env python3
"""
Ejemplo de uso del endpoint de análisis ISTQB de requisitos
"""

import requests
import json
from datetime import datetime

# Configuración del servicio
BASE_URL = "http://localhost:8000"
ENDPOINT = "/analysis/requirements/istqb-check"

def ejemplo_analisis_istqb():
    """Ejemplo completo de análisis ISTQB de un requerimiento"""
    
    # Datos de ejemplo para el análisis
    payload = {
        "requirement_id": "REQ-AUTH-001",
        "requirement_text": """
        El sistema debe permitir a los usuarios autenticarse de manera rápida y segura. 
        Los usuarios podrán ingresar sus credenciales y el sistema validará la información 
        contra la base de datos. En caso de credenciales incorrectas, se mostrará un mensaje 
        de error apropiado. El proceso debe ser fácil de usar y responder en tiempo adecuado.
        """,
        "context": {
            "product": "Sistema de Autenticación Empresarial",
            "module": "Login",
            "stakeholders": ["PO", "QA", "Dev", "Security"],
            "constraints": ["PCI DSS", "LGPD", "SLA 200ms p95", "TLS 1.3"],
            "dependencies": ["API Usuarios v2", "Base de Datos LDAP"]
        },
        "glossary": {
            "Credenciales": "Usuario y contraseña del sistema",
            "Autenticación": "Proceso de verificación de identidad",
            "SLA": "Service Level Agreement - Acuerdo de Nivel de Servicio"
        },
        "acceptance_template": "Dado/Cuando/Entonces",
        "non_functional_expectations": [
            "p95<=300ms",
            "TLS1.3",
            "a11y WCAG AA",
            "Disponibilidad 99.9%"
        ]
    }
    
    print("🔍 Iniciando análisis ISTQB de requisitos...")
    print(f"📋 Requerimiento: {payload['requirement_id']}")
    print(f"📝 Texto: {payload['requirement_text'][:100]}...")
    print()
    
    try:
        # Realizar la petición
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Model": "gpt-4",
                "X-Analysis-Version": "istqb-v1",
                "Content-Language": "es-PY"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            resultado = response.json()
            mostrar_resultado_istqb(resultado)
        else:
            print(f"❌ Error en la petición: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def mostrar_resultado_istqb(resultado):
    """Mostrar el resultado del análisis ISTQB de forma legible"""
    
    print("✅ Análisis ISTQB completado exitosamente")
    print("=" * 60)
    
    # Información básica
    print(f"📊 ID del Análisis: {resultado['analysis_id']}")
    print(f"⏱️  Tiempo de Procesamiento: {resultado['processing_time']:.2f}s")
    print(f"📅 Fecha: {resultado['created_at']}")
    print()
    
    # Puntuación de calidad
    quality_score = resultado['quality_score']
    print("🎯 PUNTUACIÓN DE CALIDAD:")
    print(f"   • General: {quality_score['overall']}/100")
    print(f"   • Claridad: {quality_score['clarity']}/100")
    print(f"   • Completitud: {quality_score['completeness']}/100")
    print(f"   • Consistencia: {quality_score['consistency']}/100")
    print(f"   • Factibilidad: {quality_score['feasibility']}/100")
    print(f"   • Testabilidad: {quality_score['testability']}/100")
    print()
    
    # Issues detectados
    issues = resultado['issues']
    print(f"🚨 ISSUES DETECTADOS ({len(issues)}):")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. [{issue['type']}] {issue['heuristic']}")
        print(f"      📝 Fragmento: {issue['excerpt']}")
        print(f"      ⚠️  Riesgo: {issue['risk']['severity']} (RPN: {issue['risk']['rpn']})")
        print(f"      💡 Sugerencia: {issue['fix_suggestion']}")
        print()
    
    # Análisis de cobertura
    coverage = resultado['coverage']
    print("📋 ANÁLISIS DE COBERTURA:")
    print(f"   • Entradas definidas: {'✅' if coverage['inputs_defined'] else '❌'}")
    print(f"   • Salidas definidas: {'✅' if coverage['outputs_defined'] else '❌'}")
    print(f"   • Manejo de errores: {'✅' if coverage['error_handling_defined'] else '❌'}")
    print(f"   • Roles definidos: {'✅' if coverage['roles_responsibilities_defined'] else '❌'}")
    print(f"   • Contratos de datos: {'✅' if coverage['data_contracts_defined'] else '❌'}")
    print(f"   • NFRs definidos: {', '.join(coverage['nfr_defined']) if coverage['nfr_defined'] else 'Ninguno'}")
    print()
    
    # Criterios de aceptación
    acceptance_criteria = resultado['acceptance_criteria']
    if acceptance_criteria:
        print("✅ CRITERIOS DE ACEPTACIÓN GENERADOS:")
        for i, ac in enumerate(acceptance_criteria, 1):
            print(f"   {i}. [{ac['id']}] {ac['criterion']}")
            print(f"      📏 Medible: {'Sí' if ac['measurable'] else 'No'}")
            print(f"      🔍 Oráculo: {ac['test_oracle']}")
            print()
    
    # Resumen ejecutivo
    print("📄 RESUMEN EJECUTIVO:")
    print(f"   {resultado['summary']}")
    print()
    
    # Versión limpia propuesta
    if resultado['proposed_clean_version']:
        print("✨ VERSIÓN LIMPIA PROPUESTA:")
        print(f"   {resultado['proposed_clean_version']}")
        print()

def ejemplo_requerimiento_malo():
    """Ejemplo con un requerimiento de mala calidad para demostrar las validaciones"""
    
    payload = {
        "requirement_id": "REQ-BAD-001",
        "requirement_text": "El sistema debe ser rápido y fácil de usar.",
        "context": {
            "product": "Sistema de Pruebas",
            "module": "Interfaz",
            "stakeholders": ["PO"],
            "constraints": [],
            "dependencies": []
        },
        "glossary": {},
        "acceptance_template": "Dado/Cuando/Entonces",
        "non_functional_expectations": []
    }
    
    print("🔍 Analizando requerimiento de mala calidad...")
    print(f"📝 Texto: {payload['requirement_text']}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Model": "gpt-4",
                "X-Analysis-Version": "istqb-v1",
                "Content-Language": "es-PY"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print("✅ Análisis completado - Se detectaron múltiples issues:")
            print(f"🎯 Puntuación General: {resultado['quality_score']['overall']}/100")
            print(f"🚨 Issues Detectados: {len(resultado['issues'])}")
            print()
            
            for issue in resultado['issues']:
                print(f"   • [{issue['type']}] {issue['explanation']}")
                print(f"     Riesgo: {issue['risk']['severity']} (RPN: {issue['risk']['rpn']})")
                print()
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Ejemplos de Análisis ISTQB de Requisitos")
    print("=" * 50)
    print()
    
    # Ejemplo 1: Requerimiento típico
    print("📋 EJEMPLO 1: Requerimiento típico de autenticación")
    print("-" * 50)
    ejemplo_analisis_istqb()
    print()
    
    # Ejemplo 2: Requerimiento de mala calidad
    print("📋 EJEMPLO 2: Requerimiento de mala calidad")
    print("-" * 50)
    ejemplo_requerimiento_malo()
    print()
    
    print("🎉 Ejemplos completados!")
    print()
    print("💡 Para usar el endpoint en tu aplicación:")
    print(f"   POST {BASE_URL}{ENDPOINT}")
    print("   Content-Type: application/json")
    print("   X-Model: gpt-4")
    print("   X-Analysis-Version: istqb-v1")
    print("   Content-Language: es-PY")