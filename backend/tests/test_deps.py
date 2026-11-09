"""Tests de las dependencias `require_admin` (AdminUser) y `get_optional_user` (OptionalUser).

Se monta una app mínima solo para el test, con rutas que usan cada dependencia. Así no se
añaden rutas de prueba a la app real.
"""

from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import AdminUser, OptionalUser, is_admin
from app.db.session import get_db
from app.models import UserRole
from tests.helpers import auth_headers

admin_app = FastAPI()


@admin_app.get("/solo-admin")
def admin_only(admin: AdminUser) -> dict[str, int]:
    return {"id": admin.id}


@admin_app.get("/opcional")
def optional_user(user: OptionalUser) -> dict[str, int | bool | None]:
    return {"id": user.id if user else None, "is_admin": is_admin(user)}


@pytest.fixture
def admin_client(db_session: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db_session

    admin_app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(admin_app) as test_client:
            yield test_client
    finally:
        admin_app.dependency_overrides.clear()


def test_require_admin_deja_pasar_a_un_admin(admin_client, create_user):
    admin = create_user(role=UserRole.ADMIN)

    response = admin_client.get("/solo-admin", headers=auth_headers(admin))

    assert response.status_code == 200
    assert response.json() == {"id": admin.id}


def test_require_admin_con_un_cliente_devuelve_403(admin_client, create_user):
    client_user = create_user()

    response = admin_client.get("/solo-admin", headers=auth_headers(client_user))

    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permiso para esta acción"


def test_require_admin_sin_token_devuelve_401(admin_client):
    response = admin_client.get("/solo-admin")

    assert response.status_code == 401


def test_optional_user_sin_token_es_anonimo(admin_client):
    response = admin_client.get("/opcional")

    assert response.status_code == 200
    assert response.json() == {"id": None, "is_admin": False}


@pytest.mark.parametrize("role", [UserRole.CLIENT, UserRole.ADMIN])
def test_optional_user_con_token_valido_devuelve_el_usuario(admin_client, create_user, role):
    user = create_user(role=role)

    response = admin_client.get("/opcional", headers=auth_headers(user))

    assert response.json() == {"id": user.id, "is_admin": role == UserRole.ADMIN}


@pytest.mark.parametrize("header", ["Bearer roto", "Basic dXNlcjpwYXNz", "Bearer", "token"])
def test_optional_user_con_cabecera_invalida_devuelve_401(admin_client, header):
    # Un token roto (o una cabecera que no es Bearer) no se trata como "anónimo": el frontend
    # debe enterarse y renovar el token.
    response = admin_client.get("/opcional", headers={"Authorization": header})

    assert response.status_code == 401


def test_optional_user_con_usuario_borrado_devuelve_401(admin_client, create_user, db_session):
    user = create_user()
    headers = auth_headers(user)
    db_session.delete(user)
    db_session.flush()

    assert admin_client.get("/opcional", headers=headers).status_code == 401
