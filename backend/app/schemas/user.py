"""Esquemas de usuario."""

from datetime import datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    StringConstraints,
)

from app.models.enums import UserRole


def _strip(value: object) -> object:
    return value.strip() if isinstance(value, str) else value


# El email se guarda en minúsculas (la base de datos lo exige con un CHECK). Primero se quitan
# los espacios (antes de validar), luego EmailStr valida el formato y la longitud (máx. 254),
# y al final se pasa todo a minúsculas.
Email = Annotated[EmailStr, BeforeValidator(_strip), AfterValidator(str.lower)]

# Mínimo 8 caracteres. El máximo (128) evita que alguien envíe una "contraseña" de varios MB
# para que Argon2 gaste CPU y memoria (ataque de denegación de servicio). No se recortan
# espacios: forman parte de la contraseña.
Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]

# 100 = longitud de la columna `full_name`. Los espacios se quitan antes de validar la
# longitud, así que un nombre "   " se rechaza. El patrón prohíbe caracteres de control
# (saltos de línea, tabuladores, el byte nulo \x00...): PostgreSQL no admite \x00 en un texto
# y sin esta regla la API respondería 500 en vez de 422.
FullName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=100, pattern=r"^[^\x00-\x1f\x7f]+$"
    ),
]


class UserCreate(BaseModel):
    """Datos para registrarse. No incluye `role`: todo usuario nuevo es cliente."""

    # extra="forbid": si alguien envía un campo de más (p. ej. "role": "admin"), la API
    # responde 422 en vez de ignorarlo en silencio.
    model_config = ConfigDict(extra="forbid")

    email: Email
    password: Password
    full_name: FullName


class UserRead(BaseModel):
    """Lo que la API devuelve de un usuario. Nunca incluye `hashed_password`."""

    # from_attributes=True: permite crear el esquema a partir de un objeto User de SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: UserRole
    created_at: datetime
