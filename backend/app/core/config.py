"""Configuración de la app.

Pydantic Settings lee las variables de entorno (o del archivo .env) y las
valida con tipos. Así, si falta una variable obligatoria o tiene un formato
incorrecto, la app falla al arrancar en lugar de fallar más tarde.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Reservas API"
    environment: str = "development"

    # Formato: postgresql+psycopg://usuario:contraseña@host:puerto/base_de_datos
    database_url: str = "postgresql+psycopg://reservas:reservas@localhost:5432/reservas"

    # Orígenes que pueden llamar a la API desde el navegador (CORS).
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    """Devuelve una única instancia de Settings (se crea la primera vez)."""
    return Settings()
