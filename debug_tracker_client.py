#!/usr/bin/env python3
"""
Script para debuggear el tracker_client
"""
import asyncio
import os
from dotenv import load_dotenv
from tracker_client import TrackerClient

load_dotenv()

async def debug_tracker_client():
    """Debuggear el tracker_client"""
    print("=== DEBUGGEANDO TRACKER CLIENT ===")
    
    # Crear instancia del tracker client
    tracker_client = TrackerClient()
    
    # Probar el método get_work_item_details
    work_item_id = "KAN-4"
    project_key = "KAN"
    
    print(f"Probando: work_item_id={work_item_id}, project_key={project_key}")
    print()
    
    try:
        result = await tracker_client.get_work_item_details(work_item_id, project_key)
        
        if result:
            print("SUCCESS! Work item encontrado:")
            print(f"  Key: {result.get('key')}")
            print(f"  Summary: {result.get('summary')}")
            print(f"  Type: {result.get('issue_type')}")
            print(f"  Status: {result.get('status')}")
        else:
            print("ERROR: Work item no encontrado")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_tracker_client())
