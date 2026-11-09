"""Tests del manejador de errores de validación (422) de app/main.py."""

import json

import pytest

from app.models import UserRole
from tests.helpers import auth_headers


@pytest.fixture
def admin_headers(create_user):
    return auth_headers(create_user(email="admin@example.com", role=UserRole.ADMIN))


@pytest.mark.parametrize("bad_number", ["NaN", "Infinity", "-Infinity", "1e400"])
def test_numeros_no_representables_en_json_dan_422_y_no_500(client, admin_headers, bad_number):
    # Se envía el JSON a mano: NaN o 1e400 son válidos para el parser de Python, pero el valor
    # resultante (nan, inf) no se puede volver a escribir en JSON.
    body = f'{{"name": "Corte", "duration_minutes": 30, "price": {bad_number}}}'

    response = client.post(
        "/api/services",
        content=body,
        headers=admin_headers | {"Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_un_caracter_unicode_invalido_da_422_y_no_500(client, admin_headers):
    # \ud800 es un "surrogate" suelto: no se puede codificar en UTF-8.
    body = '{"name": "Corte \\ud800", "duration_minutes": 30, "price": "1"}'

    response = client.post(
        "/api/services",
        content=body,
        headers=admin_headers | {"Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_el_422_no_devuelve_lo_que_envio_el_cliente(client):
    # Antes, el error incluía el valor recibido: aquí, la contraseña.
    response = client.post(
        "/api/auth/register",
        json={"email": "ana@example.com", "password": "corta77", "full_name": "Ana"},
    )

    assert response.status_code == 422
    assert "corta77" not in response.text
    error = response.json()["detail"][0]
    assert set(error) == {"type", "loc", "msg"}
    assert error["loc"] == ["body", "password"]
    json.dumps(response.json())  # sigue siendo JSON válido
