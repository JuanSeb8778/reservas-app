"""Tests de /api/business-settings."""

import pytest

from app.models import UserRole
from tests.helpers import auth_headers

URL = "/api/business-settings"
VALID = {"timezone": "Europe/Madrid", "currency": "EUR"}


@pytest.fixture
def admin(create_user):
    return create_user(email="admin@example.com", role=UserRole.ADMIN)


def test_cualquiera_puede_leer_la_configuracion(client):
    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == {"timezone": "America/Bogota", "currency": "COP"}


def test_sin_sesion_no_se_puede_cambiar(client):
    assert client.put(URL, json=VALID).status_code == 401


def test_un_cliente_no_puede_cambiarla(client, create_user):
    response = client.put(URL, json=VALID, headers=auth_headers(create_user()))

    assert response.status_code == 403


def test_el_admin_la_cambia_y_queda_guardada(client, admin):
    response = client.put(URL, json=VALID, headers=auth_headers(admin))

    assert response.status_code == 200
    assert response.json() == VALID
    assert client.get(URL).json() == VALID


def test_la_moneda_se_normaliza_y_se_quitan_espacios(client, admin):
    response = client.put(
        URL, json={"timezone": " Europe/Madrid ", "currency": " eur"}, headers=auth_headers(admin)
    )

    assert response.status_code == 200
    assert response.json() == VALID


@pytest.mark.parametrize(
    "timezone",
    [
        "Mars/Olympus",
        "america/bogota",
        "",
        "Bogota",
        "../etc/passwd",
        "UTC+5",
        "localtime",  # la zona del servidor, no una zona real
        "Factory",
    ],
)
def test_rechaza_zonas_horarias_desconocidas(client, admin, timezone):
    response = client.put(
        URL, json={"timezone": timezone, "currency": "COP"}, headers=auth_headers(admin)
    )

    assert response.status_code == 422


@pytest.mark.parametrize("currency", ["COPP", "CO", "C0P", "", "€"])
def test_rechaza_monedas_con_formato_invalido(client, admin, currency):
    response = client.put(
        URL, json={"timezone": "America/Bogota", "currency": currency}, headers=auth_headers(admin)
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "body",
    [
        {"timezone": "America/Bogota"},
        {"currency": "COP"},
        {"timezone": "America/Bogota", "currency": "COP", "extra": "x"},
    ],
)
def test_exige_exactamente_los_dos_campos(client, admin, body):
    assert client.put(URL, json=body, headers=auth_headers(admin)).status_code == 422
