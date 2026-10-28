"""Punto de entrada de la API.

Arranca con:  uvicorn app.main:app --reload
Documentación interactiva: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,  # necesario para enviar cookies (token de refresco)
    allow_methods=["*"],
    allow_headers=["*"],
)

# Todas las rutas de la API cuelgan de /api
app.include_router(health.router, prefix="/api")
