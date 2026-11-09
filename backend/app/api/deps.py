"""Dependencias compartidas por los routers.

Uso en un endpoint:
    def mi_ruta(user: CurrentUser, db: DbSession): ...
    def solo_admin(admin: AdminUser): ...
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import TokenError, decode_token
from app.db.session import get_db
from app.models import User, UserRole

DbSession = Annotated[Session, Depends(get_db)]

# HTTPBearer lee la cabecera `Authorization: Bearer <token>` y añade el botón "Authorize" a
# /docs (ahí se pega el access_token que devuelve /api/auth/login). auto_error=False: si falta
# la cabecera devuelve None y el 401 lo lanzamos nosotros, con mensaje en español.
bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized(detail: str) -> HTTPException:
    # El estándar HTTP pide que un 401 indique cómo autenticarse (cabecera WWW-Authenticate).
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    if credentials is None:
        raise unauthorized("No autenticado")
    try:
        user_id = decode_token(credentials.credentials, "access")
    except TokenError:
        raise unauthorized("Token inválido o expirado") from None

    # El usuario (y su rol) se lee siempre de la base de datos, no del token: si lo borran o
    # le cambian el rol, el cambio se aplica en la siguiente petición.
    user = db.get(User, user_id)
    if user is None:
        raise unauthorized("Token inválido o expirado")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_optional_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User | None:
    """Para endpoints públicos que muestran más cosas a un admin (p. ej. servicios inactivos).

    Sin cabecera Authorization → None (visitante anónimo). Con un token inválido o caducado →
    401, a propósito: así el frontend renueva el token en vez de recibir en silencio la vista
    pública como si no hubiera iniciado sesión.
    """
    if credentials is None:
        return None
    return get_current_user(db, credentials)


OptionalUser = Annotated[User | None, Depends(get_optional_user)]


def is_admin(user: User | None) -> bool:
    return user is not None and user.role == UserRole.ADMIN


def require_admin(user: CurrentUser) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para esta acción"
        )
    return user


AdminUser = Annotated[User, Depends(require_admin)]
