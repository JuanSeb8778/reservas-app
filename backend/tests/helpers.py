"""Funciones de ayuda para los tests (las fixtures están en conftest.py)."""

from app.core.security import create_access_token
from app.models import User


def auth_headers(user: User) -> dict[str, str]:
    """Cabecera Authorization con un access token válido para `user`."""
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}
