#!/usr/bin/env python3
"""
Test para debuggear el formato del template
"""

import json
from datetime import datetime

def test_format():
    """Test del formato del template"""
    print("Debug del formato del template")
    
    # Template simple para probar
    template = """
Datos del issue: {jira_data}
Titulo: {test_plan_title}
Estrategia: {test_strategy}
Automatizacion: {include_automation}
Rendimiento: {include_performance}
Seguridad: {include_security}
Espacio: {confluence_space_key}
Timestamp: {timestamp}
"""
    
    # Datos de prueba
    jira_data = {
        "key": "PROJ-123",
        "summary": "Test issue"
    }
    
    try:
        # Convertir jira_data a string
        jira_data_str = json.dumps(jira_data, indent=2, ensure_ascii=False)
        
        print("Datos de Jira como string:")
        print(jira_data_str)
        print()
        
        # Probar formato
        prompt = template.format(
            jira_data=jira_data_str,
            test_plan_title="Test Plan",
            test_strategy="comprehensive",
            include_automation="true",
            include_performance="false",
            include_security="true",
            confluence_space_key="QA",
            timestamp=datetime.utcnow().isoformat()
        )
        
        print("Prompt generado:")
        print(prompt)
        
        # Verificar variables sin reemplazar
        if "{" in prompt and "}" in prompt:
            print("Advertencia: Variables sin reemplazar encontradas")
            import re
            variables = re.findall(r'\{[^}]+\}', prompt)
            print(f"Variables: {variables}")
        else:
            print("No hay variables sin reemplazar")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_format()
