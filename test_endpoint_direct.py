#!/usr/bin/env python3
"""
Script para probar el endpoint directamente
"""
import asyncio
import httpx
import json

async def test_endpoint():
    """Probar el endpoint directamente"""
    url = "http://localhost:8000/analyze-jira-workitem"
    data = {
        "work_item_id": "KAN-4",
        "project_key": "KAN",
        "test_types": ["functional", "integration"],
        "coverage_level": "high",
        "include_acceptance_criteria": True
    }
    
    print(f"=== PROBANDO ENDPOINT DIRECTO ===")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=data)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
