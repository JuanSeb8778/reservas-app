"""Tests de la dependencia `require_admin` (AdminUser).

Todavía no hay endpoints de admin, así que se monta una app mínima solo para el test, con
una ruta protegida. Así no se añaden rutas de prueba a la app real.
"""

from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import AdminUser
from app.db.session import get_db
from app.models import UserRole
from tests.helpers import auth_headers

admin_app = FastAPI()


@admin_app.get("/solo-admin")
def admin_only(admin: AdminUser) -> dict[str, int]:
    return {"id": admin.id}


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
