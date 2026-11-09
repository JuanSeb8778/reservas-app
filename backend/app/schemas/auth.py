"""Esquemas de autenticación."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.schemas.user import Email


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Email
    # En el login no se exige el mínimo de 8: si algún día cambia la política, los usuarios
    # antiguos deben poder entrar igual. Sí se limita el máximo, por la misma razón que en el
    # registro (no dejar que Argon2 procese textos enormes).
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    # Segundos hasta que caduca el access token. Así el frontend sabe cuándo renovarlo
    # sin tener que decodificar el JWT.
    expires_in: int
