"""
Script para probar la aplicación localmente
"""

import uvicorn

if __name__ == "__main__":
    print("Testing app.py locally...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
