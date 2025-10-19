"""
Microservicio de Análisis QA - Versión Ultra Simple
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import os

app = FastAPI(
    title="Microservicio de Análisis QA",
    description="API de Análisis Automatizado de Casos de Prueba",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Redirige automáticamente a la documentación de Swagger"""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
