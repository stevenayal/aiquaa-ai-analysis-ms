"""
Microservicio de Análisis QA - Versión Ultra Simple
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict

app = FastAPI(
    title="Microservicio de Análisis QA",
    description="API de Análisis Automatizado de Casos de Prueba",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

@app.get("/")
async def root():
    return {"message": "Microservicio de Análisis QA", "status": "running"}

@app.get("/health")
async def health():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
