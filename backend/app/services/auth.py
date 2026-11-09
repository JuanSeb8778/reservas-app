"""Registro y autenticación de usuarios."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_dummy_password, verify_password
from app.models import User
from app.schemas.user import UserCreate


class EmailAlreadyRegisteredError(Exception):
    """Ya existe un usuario con ese email."""


class InvalidCredentialsError(Exception):
    """Email o contraseña incorrectos (a propósito no se dice cuál de los dos)."""


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def register_user(db: Session, data: UserCreate) -> User:
    # Comprobación previa: evita calcular el hash (lento) si el email ya está ocupado.
    if get_user_by_email(db, data.email) is not None:
        raise EmailAlreadyRegisteredError

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        # Dos registros simultáneos con el mismo email pueden pasar ambos la comprobación de
        # arriba; la restricción UNIQUE de la base de datos es la que decide al final.
        db.rollback()
        if getattr(exc.orig, "diag", None) and exc.orig.diag.constraint_name == "uq_users_email":
            raise EmailAlreadyRegisteredError from exc
        raise
    # role y created_at los rellena la base de datos; se recargan para devolverlos.
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if user is None:
        # Se verifica igualmente contra un hash ficticio para tardar lo mismo que con un
        # email existente (ver security.verify_dummy_password).
        verify_dummy_password(password)
        raise InvalidCredentialsError
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError
    return user
