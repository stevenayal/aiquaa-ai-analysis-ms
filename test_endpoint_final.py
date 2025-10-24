#!/usr/bin/env python3
"""
Test final del endpoint /analyze-jira-confluence
"""

import asyncio
import json
import httpx

async def test_endpoint():
    """Test del endpoint corregido"""
    print("Test del endpoint /analyze-jira-confluence")
    
    # Datos mínimos
    data = {
        "jira_issue_id": "PROJ-123",
        "confluence_space_key": "QA"
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print(f"Enviando: {json.dumps(data, indent=2)}")
            
            response = await client.post(
                "http://localhost:8000/analyze-jira-confluence",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("Exito!")
                print(f"ID: {result.get('analysis_id', 'N/A')}")
                print(f"Casos: {result.get('total_test_cases', 0)}")
                print(f"Secciones: {len(result.get('test_plan_sections', []))}")
                print(f"Fases: {len(result.get('test_execution_phases', []))}")
            else:
                print("Error!")
                print(f"Respuesta: {response.text}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoint())
