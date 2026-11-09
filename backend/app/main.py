"""Punto de entrada de la API.

Arranca con:  uvicorn app.main:app --reload
Documentación interactiva: http://localhost:8000/docs
"""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, business_hours, business_settings, health, services
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


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """422 sin el valor recibido.

    El manejador por defecto de FastAPI incluye en cada error el `input` que envió el cliente.
    Eso tenía dos problemas:
    - Si el valor era NaN, Infinity o un texto con un carácter Unicode inválido, la respuesta
      no se podía convertir a JSON y el 422 acababa en un 500.
    - Devolvía datos sensibles, p. ej. la contraseña en un registro con errores.
    Se conservan `type`, `loc` y `msg`, que es lo que necesita quien llama a la API.
    """
    errors = [
        {key: value for key, value in error.items() if key in ("type", "loc", "msg")}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": jsonable_encoder(errors)},
    )


# Todas las rutas de la API cuelgan de /api
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(business_settings.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(business_hours.router, prefix="/api")
