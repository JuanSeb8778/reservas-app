"""Contraseñas y tokens JWT.

- Las contraseñas se guardan como hash Argon2 (con `pwdlib`); nunca en texto plano.
- Hay dos tipos de token, ambos JWT firmados con `JWT_SECRET`:
  - access (15 min): va en la cabecera `Authorization: Bearer <token>`.
  - refresh (7 días): va en una cookie httpOnly y solo sirve para pedir un access nuevo.
  El claim `type` los distingue, para que un refresh token no sirva como access token
  (y al revés).
"""

from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

TokenType = Literal["access", "refresh"]

_MAX_DB_INTEGER = 2**31 - 1  # mayor valor de una columna INTEGER en PostgreSQL

# recommended() usa Argon2 con los parámetros recomendados por pwdlib.
_password_hash = PasswordHash.recommended()

# Hash de una contraseña cualquiera. Cuando alguien intenta iniciar sesión con un email que
# no existe, se verifica contra este hash igualmente: así la respuesta tarda lo mismo que con
# un email real y no se puede adivinar qué emails están registrados midiendo el tiempo.
_DUMMY_HASH = _password_hash.hash("contrasena-ficticia-para-igualar-tiempos")


class TokenError(Exception):
    """El token no es válido: firma incorrecta, expirado, mal formado o de otro tipo."""


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return _password_hash.verify(password, hashed_password)


def verify_dummy_password(password: str) -> None:
    """Gasta el mismo tiempo que `verify_password`; el resultado no importa."""
    _password_hash.verify(password, _DUMMY_HASH)


# `expires_delta` permite crear tokens ya caducados en los tests (con un valor negativo).
def create_access_token(user_id: int, *, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=get_settings().access_token_minutes)
    return _create_token(user_id, "access", expires_delta)


def create_refresh_token(user_id: int, *, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(days=get_settings().refresh_token_days)
    return _create_token(user_id, "refresh", expires_delta)


def _create_token(user_id: int, token_type: TokenType, lifetime: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        # PyJWT exige que `sub` sea texto, por eso el id se convierte a str.
        "sub": str(user_id),
        "type": token_type,
        "iat": now,
        "exp": now + lifetime,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: TokenType) -> int:
    """Valida el token y devuelve el id del usuario. Lanza `TokenError` si no es válido."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            # Fijar el algoritmo es clave: si se leyera de la cabecera del token, un atacante
            # podría elegir "none" (sin firma).
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "iat", "sub", "type"]},
        )
    except jwt.InvalidTokenError as exc:  # incluye ExpiredSignatureError
        raise TokenError from exc

    if payload["type"] != expected_type:
        raise TokenError(f"Se esperaba un token de tipo {expected_type}")

    # Solo dígitos ASCII (int() aceptaría también " 1", "1_0" o "١") y dentro del rango de la
    # columna `id` (INTEGER de Postgres); si no, la consulta fallaría con un error 500.
    sub = payload["sub"]
    if not (sub.isascii() and sub.isdigit()) or not 1 <= int(sub) <= _MAX_DB_INTEGER:
        raise TokenError("El claim sub no es un id válido")
    return int(sub)
