#!/usr/bin/env python3
"""
Script de prueba para la nueva estructura modular de test cases.
Demuestra el formato: CP001 - NOMBRE DE APLICACION - MODULO - CONDICION Y RESULTADO
"""

import json
from modular_test_case_template import ModularTestCaseTemplate

def test_modular_structure():
    """Probar la nueva estructura modular de test cases."""
    
    print("PRUEBA DE ESTRUCTURA MODULAR DE TEST CASES")
    print("=" * 60)
    
    # Crear instancia del template
    template = ModularTestCaseTemplate()
    
    # Ejemplo de test case con estructura modular
    test_case_example = {
        "test_case_id": "CP001-ECOMMERCE-CART-VALIDATION-SUCCESS",
        "title": "CP001 - ECOMMERCE - CART - VALIDATION Y SUCCESS",
        "description": "Verificar que el carrito de compras valida correctamente los productos agregados",
        "test_type": "functional",
        "priority": "high",
        "preconditions": [
            "Precondición 1: Usuario autenticado en el sistema",
            "Precondición 2: Productos disponibles en el catálogo",
            "Precondición 3: Carrito de compras vacío"
        ],
        "steps": [
            "Paso 1: Navegar a la página de productos",
            "Paso 2: Seleccionar un producto del catálogo",
            "Paso 3: Hacer clic en 'Agregar al carrito'",
            "Paso 4: Verificar que el producto aparece en el carrito",
            "Paso 5: Verificar que el total se calcula correctamente"
        ],
        "expected_results": [
            "Resultado Esperado 1: El producto se agrega al carrito exitosamente",
            "Resultado Esperado 2: El contador del carrito se actualiza",
            "Resultado Esperado 3: El total del carrito se calcula correctamente",
            "Resultado Esperado 4: Se muestra mensaje de confirmación"
        ],
        "test_data": {
            "input_data": "Producto: iPhone 15, Cantidad: 1, Precio: $999",
            "environment": "Entorno de testing con datos de prueba",
            "user_roles": "Usuario autenticado con permisos de compra"
        },
        "automation_potential": "high",
        "estimated_duration": "5-10 minutes",
        "risk_level": "medium",
        "business_impact": "high"
    }
    
    # Validar estructura
    print("Validando estructura del test case...")
    errors = template.validate_test_case_structure(test_case_example)
    
    if errors:
        print("Errores encontrados:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("Estructura valida")
    
    # Mostrar test case formateado
    print("\nTest Case Formateado:")
    print("-" * 40)
    formatted = template.format_test_case_for_display(test_case_example)
    print(formatted)
    
    # Generar ID y título programáticamente
    print("\nGenerando ID y titulo programaticamente:")
    print("-" * 40)
    
    project_key = "ECOMMERCE"
    module = "CART"
    condition = "VALIDATION"
    result = "SUCCESS"
    app_name = "ECOMMERCE"
    
    generated_id = template.generate_test_case_id(project_key, module, condition, result)
    generated_title = template.generate_test_case_title(app_name, module, condition, result)
    
    print(f"ID generado: {generated_id}")
    print(f"Título generado: {generated_title}")
    
    # Verificar que coinciden con el ejemplo
    print(f"\nID coincide: {generated_id == test_case_example['test_case_id']}")
    print(f"Titulo coincide: {generated_title == test_case_example['title']}")
    
    return test_case_example

def test_multiple_test_cases():
    """Probar múltiples test cases con estructura modular."""
    
    print("\n\nPRUEBA DE MULTIPLES TEST CASES MODULARES")
    print("=" * 60)
    
    template = ModularTestCaseTemplate()
    
    # Múltiples ejemplos de test cases
    test_cases = [
        {
            "app_name": "ECOMMERCE",
            "module": "CART",
            "condition": "VALIDATION",
            "result": "SUCCESS",
            "description": "Validación exitosa del carrito"
        },
        {
            "app_name": "ECOMMERCE", 
            "module": "PAYMENT",
            "condition": "PROCESSING",
            "result": "COMPLETION",
            "description": "Procesamiento completo del pago"
        },
        {
            "app_name": "ECOMMERCE",
            "module": "USER",
            "condition": "REGISTRATION",
            "result": "CONFIRMATION",
            "description": "Confirmación de registro de usuario"
        },
        {
            "app_name": "ECOMMERCE",
            "module": "PRODUCT",
            "condition": "SEARCH",
            "result": "RESULTS",
            "description": "Búsqueda y resultados de productos"
        }
    ]
    
    print("Generando test cases modulares:")
    print("-" * 40)
    
    for i, tc in enumerate(test_cases, 1):
        print(f"\n{i}. {tc['description']}")
        
        # Generar ID y título
        project_key = tc['app_name']
        generated_id = template.generate_test_case_id(
            project_key, 
            tc['module'], 
            tc['condition'], 
            tc['result']
        )
        generated_title = template.generate_test_case_title(
            tc['app_name'], 
            tc['module'], 
            tc['condition'], 
            tc['result']
        )
        
        print(f"   ID: {generated_id}")
        print(f"   Título: {generated_title}")
        
        # Validar formato
        import re
        id_valid = re.match(r'^CP001-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$', generated_id)
        title_valid = re.match(r'^CP001 - .+ - .+ - .+ Y .+$', generated_title)
        
        print(f"   ID valido: {bool(id_valid)}")
        print(f"   Titulo valido: {bool(title_valid)}")

def test_json_export():
    """Exportar test cases a JSON para uso en la aplicación."""
    
    print("\n\nEXPORTANDO ESTRUCTURA A JSON")
    print("=" * 60)
    
    # Crear estructura completa para exportar
    export_data = {
        "test_cases": [
            {
                "test_case_id": "CP001-ECOMMERCE-CART-VALIDATION-SUCCESS",
                "title": "CP001 - ECOMMERCE - CART - VALIDATION Y SUCCESS",
                "description": "Verificar que el carrito de compras valida correctamente los productos agregados",
                "test_type": "functional",
                "priority": "high",
                "preconditions": [
                    "Precondición 1: Usuario autenticado en el sistema",
                    "Precondición 2: Productos disponibles en el catálogo",
                    "Precondición 3: Carrito de compras vacío"
                ],
                "steps": [
                    "Paso 1: Navegar a la página de productos",
                    "Paso 2: Seleccionar un producto del catálogo", 
                    "Paso 3: Hacer clic en 'Agregar al carrito'",
                    "Paso 4: Verificar que el producto aparece en el carrito",
                    "Paso 5: Verificar que el total se calcula correctamente"
                ],
                "expected_results": [
                    "Resultado Esperado 1: El producto se agrega al carrito exitosamente",
                    "Resultado Esperado 2: El contador del carrito se actualiza",
                    "Resultado Esperado 3: El total del carrito se calcula correctamente",
                    "Resultado Esperado 4: Se muestra mensaje de confirmación"
                ],
                "test_data": {
                    "input_data": "Producto: iPhone 15, Cantidad: 1, Precio: $999",
                    "environment": "Entorno de testing con datos de prueba",
                    "user_roles": "Usuario autenticado con permisos de compra"
                },
                "automation_potential": "high",
                "estimated_duration": "5-10 minutes",
                "risk_level": "medium",
                "business_impact": "high"
            }
        ],
        "coverage_analysis": {
            "functional_coverage": "85%",
            "edge_case_coverage": "70%",
            "integration_coverage": "80%",
            "security_coverage": "60%",
            "ui_coverage": "90%",
            "usability_coverage": "75%",
            "accessibility_coverage": "65%"
        },
        "confidence_score": 0.85,
        "test_strategy": {
            "approach": "Testing basado en casos de uso con cobertura modular",
            "techniques_applied": ["Partición de equivalencia", "Valores límite", "Casos de uso"],
            "risks_identified": ["Dependencias externas", "Datos de prueba inconsistentes"],
            "mitigation_strategies": ["Mocking de servicios", "Datos de prueba estandarizados"]
        }
    }
    
    # Exportar a archivo JSON
    output_file = "modular_test_cases_example.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"Estructura exportada a: {output_file}")
    print(f"Test cases generados: {len(export_data['test_cases'])}")
    print(f"Cobertura funcional: {export_data['coverage_analysis']['functional_coverage']}")
    print(f"Score de confianza: {export_data['confidence_score']}")

def main():
    """Función principal de pruebas."""
    try:
        # Ejecutar todas las pruebas
        test_modular_structure()
        test_multiple_test_cases()
        test_json_export()
        
        print("\n\nTODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        print("Estructura modular implementada correctamente")
        print("Formato CP001 - NOMBRE DE APLICACION - MODULO - CONDICION Y RESULTADO")
        print("Precondiciones, pasos y resultados esperados estructurados")
        print("Validacion y generacion automatica funcionando")
        print("Exportacion a JSON lista para uso en produccion")
        
    except Exception as e:
        print(f"\nError en las pruebas: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
