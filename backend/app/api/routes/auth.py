"""Endpoints de autenticación: registro, login, refresco, logout y usuario actual.

Flujo:
1. POST /register crea la cuenta (no inicia sesión).
2. POST /login devuelve el access token en el JSON y deja el refresh token en una cookie
   httpOnly (JavaScript no puede leerla, así que un script inyectado no puede robarla).
3. Cuando el access token caduca, el frontend llama a POST /refresh: el navegador envía la
   cookie solo, y la API devuelve un access token nuevo.
4. POST /logout borra la cookie.

Limitación conocida: los tokens no se guardan en la base de datos, así que no se pueden
revocar. Tras el logout, un refresh token robado seguiría valiendo hasta que caduque.
"""

from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response, status

from app.api.deps import CurrentUser, DbSession, unauthorized
from app.core.config import get_settings
from app.core.security import TokenError, create_access_token, create_refresh_token, decode_token
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services.auth import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    authenticate_user,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "refresh_token"
# La cookie solo se envía a /api/auth/*: el resto de la API nunca la recibe.
REFRESH_COOKIE_PATH = "/api/auth"

_401 = {status.HTTP_401_UNAUTHORIZED: {"description": "No autenticado o token inválido"}}


def _cookie_options() -> dict:
    """Atributos de la cookie. Deben ser los mismos al crearla y al borrarla, o el navegador
    no la reconoce como la misma cookie y no la borra."""
    return {
        "path": REFRESH_COOKIE_PATH,
        "httponly": True,
        # Lax: el navegador no envía la cookie en peticiones POST desde otros sitios, lo que
        # protege /refresh y /logout de ataques CSRF.
        "samesite": "lax",
        "secure": get_settings().cookie_secure,
    }


def _issue_tokens(user: User, response: Response) -> TokenResponse:
    settings = get_settings()
    response.set_cookie(
        REFRESH_COOKIE,
        create_refresh_token(user.id),
        max_age=settings.refresh_token_days * 24 * 60 * 60,
        **_cookie_options(),
    )
    # Respuestas con tokens: que ningún navegador ni proxy las guarde en caché.
    response.headers["Cache-Control"] = "no-store"
    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.access_token_minutes * 60,
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "El email ya está registrado"}},
)
def register(data: UserCreate, db: DbSession) -> UserRead:
    try:
        user = register_user(db, data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ya existe una cuenta con este correo"
        ) from None
    return UserRead.model_validate(user)


@router.post("/login", responses=_401)
def login(data: LoginRequest, db: DbSession, response: Response) -> TokenResponse:
    try:
        user = authenticate_user(db, data.email, data.password)
    except InvalidCredentialsError:
        # Mismo mensaje si el email no existe o si la contraseña está mal.
        raise unauthorized("Correo o contraseña incorrectos") from None
    return _issue_tokens(user, response)


@router.post("/refresh", responses=_401)
def refresh(
    db: DbSession,
    response: Response,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None,
) -> TokenResponse:
    if refresh_token is None:
        raise unauthorized("No hay sesión activa")
    try:
        user_id = decode_token(refresh_token, "refresh")
    except TokenError:
        raise unauthorized("Sesión expirada, inicia sesión de nuevo") from None
    user = db.get(User, user_id)
    if user is None:
        raise unauthorized("Sesión expirada, inicia sesión de nuevo")
    # Se emite también una cookie nueva: la sesión se alarga 7 días desde el último uso.
    return _issue_tokens(user, response)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout() -> Response:
    # No exige estar autenticado: con el access token caducado también hay que poder salir.
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(REFRESH_COOKIE, **_cookie_options())
    return response


@router.get("/me", responses=_401)
def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
