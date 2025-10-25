#!/usr/bin/env python3
"""
Test para debuggear el template de Confluence
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prompt_templates import PromptTemplates
from datetime import datetime

def test_template():
    """Test del template de Confluence"""
    print("🔍 Debug del template de Confluence")
    
    try:
        # Crear instancia de PromptTemplates
        prompt_templates = PromptTemplates()
        
        # Datos de prueba
        jira_data = {
            "key": "PROJ-123",
            "summary": "Implementar autenticación de usuarios",
            "description": "El sistema debe permitir a los usuarios autenticarse",
            "issue_type": "Story",
            "priority": "High"
        }
        
        test_plan_title = "Plan de Pruebas - Autenticación de Usuarios"
        
        print("📤 Generando prompt...")
        
        # Generar prompt
        prompt = prompt_templates.get_confluence_test_plan_prompt(
            jira_data=jira_data,
            test_plan_title=test_plan_title,
            test_strategy="comprehensive",
            include_automation=True,
            include_performance=False,
            include_security=True,
            confluence_space_key="QA"
        )
        
        print("✅ Prompt generado exitosamente")
        print(f"   Longitud: {len(prompt)} caracteres")
        print(f"   Primeros 200 caracteres: {prompt[:200]}...")
        
        # Verificar que no hay variables sin reemplazar
        if "{" in prompt and "}" in prompt:
            print("⚠️  Advertencia: Posibles variables sin reemplazar en el prompt")
            # Buscar variables sin reemplazar
            import re
            variables = re.findall(r'\{[^}]+\}', prompt)
            if variables:
                print(f"   Variables encontradas: {variables}")
        else:
            print("✅ No se encontraron variables sin reemplazar")
            
    except Exception as e:
        print(f"❌ Error generando prompt: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template()
