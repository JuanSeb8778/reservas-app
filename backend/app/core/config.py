"""Configuración de la app.

Pydantic Settings lee las variables de entorno (o del archivo .env) y las
valida con tipos. Así, si falta una variable obligatoria o tiene un formato
incorrecto, la app falla al arrancar en lugar de fallar más tarde.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Reservas API"
    environment: str = "development"

    # Formato: postgresql+psycopg://usuario:contraseña@host:puerto/base_de_datos
    database_url: str = "postgresql+psycopg://reservas:reservas@localhost:5432/reservas"

    # Orígenes que pueden llamar a la API desde el navegador (CORS).
    cors_origins: list[str] = ["http://localhost:5173"]

    # --- Autenticación ---
    # Clave con la que se firman los JWT. Obligatoria y sin valor por defecto: si falta, la app
    # no arranca (mejor que firmar tokens con una clave conocida). Mínimo 32 caracteres, que es
    # lo que recomienda PyJWT para HS256.
    jwt_secret: str = Field(min_length=32)
    # Literal: solo se aceptan algoritmos HMAC. Con un `str` libre, una variable de entorno
    # mal puesta (p. ej. "none") podría desactivar la firma.
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 7

    @property
    def cookie_secure(self) -> bool:
        """La cookie de refresco solo viaja por HTTPS fuera de desarrollo.

        En local se usa http://localhost; con `Secure` el navegador la descartaría.
        """
        return self.environment != "development"


@lru_cache
def get_settings() -> Settings:
    """Devuelve una única instancia de Settings (se crea la primera vez)."""
    return Settings()
