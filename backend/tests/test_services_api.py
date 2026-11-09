"""Tests de /api/services."""

from decimal import Decimal

import pytest

from app.models import Service, UserRole
from tests.helpers import auth_headers

URL = "/api/services"
NEW_SERVICE = {"name": "Corte clásico", "duration_minutes": 30, "price": "25000"}


@pytest.fixture
def admin(create_user):
    return create_user(email="admin@example.com", role=UserRole.ADMIN)


@pytest.fixture
def client_user(create_user):
    return create_user(email="cliente@example.com")


@pytest.fixture
def make_service(db_session):
    def _make_service(name: str, *, is_active: bool = True, **extra) -> Service:
        service = Service(
            name=name,
            duration_minutes=extra.get("duration_minutes", 30),
            price=extra.get("price", Decimal("20000")),
            description=extra.get("description"),
            is_active=is_active,
        )
        db_session.add(service)
        # commit (no flush): el servicio "ya existía" antes de la petición. Si la API hace
        # rollback (p. ej. tras un 409) no debe llevárselo. Con join_transaction_mode=
        # "create_savepoint" (conftest.py) todo se deshace igualmente al acabar el test.
        db_session.commit()
        return service

    return _make_service


# --- Listado -------------------------------------------------------------------------------


def test_el_listado_publico_solo_muestra_activos_en_orden_alfabetico(client, make_service):
    make_service("barba")
    make_service("Afeitado")
    make_service("Corte infantil", is_active=False)

    response = client.get(URL)

    assert response.status_code == 200
    assert [s["name"] for s in response.json()] == ["Afeitado", "barba"]


def test_el_admin_puede_ver_tambien_los_archivados(client, admin, make_service):
    make_service("Barba")
    make_service("Corte infantil", is_active=False)

    response = client.get(URL, params={"include_inactive": True}, headers=auth_headers(admin))

    assert response.status_code == 200
    assert [s["name"] for s in response.json()] == ["Barba", "Corte infantil"]


def test_pedir_los_archivados_sin_sesion_da_401(client):
    assert client.get(URL, params={"include_inactive": True}).status_code == 401


def test_pedir_los_archivados_como_cliente_da_403(client, client_user):
    response = client.get(URL, params={"include_inactive": True}, headers=auth_headers(client_user))

    assert response.status_code == 403


def test_un_token_invalido_da_401_aunque_la_ruta_sea_publica(client):
    response = client.get(URL, headers={"Authorization": "Bearer roto"})

    assert response.status_code == 401


# --- Detalle -------------------------------------------------------------------------------


def test_el_detalle_de_un_servicio_activo_es_publico(client, make_service):
    service = make_service("Barba", price=Decimal("15000.50"), description="Con toalla caliente")

    response = client.get(f"{URL}/{service.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Barba"
    assert body["price"] == "15000.50"  # Decimal → texto, sin perder precisión
    assert body["description"] == "Con toalla caliente"


def test_un_servicio_archivado_no_existe_para_quien_no_es_admin(client, client_user, make_service):
    service = make_service("Corte infantil", is_active=False)

    assert client.get(f"{URL}/{service.id}").status_code == 404
    response = client.get(f"{URL}/{service.id}", headers=auth_headers(client_user))
    assert response.status_code == 404


def test_el_admin_ve_el_detalle_de_un_servicio_archivado(client, admin, make_service):
    service = make_service("Corte infantil", is_active=False)

    response = client.get(f"{URL}/{service.id}", headers=auth_headers(admin))

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_un_servicio_inexistente_da_404(client):
    response = client.get(f"{URL}/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "El servicio no existe"


@pytest.mark.parametrize("service_id", ["0", "-1", "2147483648", "9223372036854775808", "abc"])
def test_ids_imposibles_dan_422_y_no_llegan_a_la_base_de_datos(client, admin, service_id):
    # 2147483648 no cabe en un INTEGER de Postgres: antes daba 500 ("integer out of range").
    assert client.get(f"{URL}/{service_id}").status_code == 422
    response = client.patch(f"{URL}/{service_id}", json={"price": "1"}, headers=auth_headers(admin))
    assert response.status_code == 422


# --- Crear ---------------------------------------------------------------------------------


def test_el_admin_crea_un_servicio(client, admin):
    response = client.post(URL, json=NEW_SERVICE, headers=auth_headers(admin))

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Corte clásico"
    assert body["price"] == "25000.00"
    assert body["description"] is None
    assert body["is_active"] is True
    assert isinstance(body["id"], int)


def test_crear_sin_sesion_da_401_y_como_cliente_403(client, client_user):
    assert client.post(URL, json=NEW_SERVICE).status_code == 401
    response = client.post(URL, json=NEW_SERVICE, headers=auth_headers(client_user))
    assert response.status_code == 403


def test_crear_con_un_nombre_repetido_da_409_sin_importar_mayusculas(client, admin, make_service):
    make_service("corte clásico", is_active=False)

    response = client.post(URL, json=NEW_SERVICE, headers=auth_headers(admin))

    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe un servicio con ese nombre"


def test_los_espacios_del_nombre_y_la_descripcion_se_recortan(client, admin):
    payload = NEW_SERVICE | {"name": "  Barba  ", "description": "   "}

    response = client.post(URL, json=payload, headers=auth_headers(admin))

    assert response.status_code == 201
    assert response.json()["name"] == "Barba"
    assert response.json()["description"] is None  # descripción vacía → null


@pytest.mark.parametrize(
    "changes",
    [
        {"duration_minutes": 7},
        {"duration_minutes": 0},
        {"duration_minutes": 485},
        {"price": "-1"},
        {"price": "10.999"},
        {"price": "100000000"},
        {"name": ""},
        {"name": "   "},
        {"name": "a" * 101},
        {"name": "Corte\x00"},
        {"description": "a" * 501},
        {"extra": "campo de más"},
    ],
)
def test_crear_con_datos_invalidos_da_422(client, admin, changes):
    response = client.post(URL, json=NEW_SERVICE | changes, headers=auth_headers(admin))

    assert response.status_code == 422


def test_la_descripcion_admite_saltos_de_linea(client, admin):
    payload = NEW_SERVICE | {"description": "Incluye lavado.\nDuración aproximada."}

    response = client.post(URL, json=payload, headers=auth_headers(admin))

    assert response.status_code == 201


# --- Editar --------------------------------------------------------------------------------


def test_editar_solo_cambia_los_campos_enviados(client, admin, make_service):
    service = make_service("Barba", description="Con toalla caliente")

    response = client.patch(
        f"{URL}/{service.id}", json={"price": "18000"}, headers=auth_headers(admin)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["price"] == "18000.00"
    assert body["name"] == "Barba"
    assert body["description"] == "Con toalla caliente"


def test_enviar_description_null_la_borra(client, admin, make_service):
    service = make_service("Barba", description="Con toalla caliente")

    response = client.patch(
        f"{URL}/{service.id}", json={"description": None}, headers=auth_headers(admin)
    )

    assert response.json()["description"] is None


@pytest.mark.parametrize(
    "payload",
    [{}, {"name": None}, {"price": None}, {"duration_minutes": None}, {"is_active": None}],
)
def test_editar_sin_campos_o_con_null_en_campos_obligatorios_da_422(
    client, admin, make_service, payload
):
    service = make_service("Barba")

    response = client.patch(f"{URL}/{service.id}", json=payload, headers=auth_headers(admin))

    assert response.status_code == 422


def test_archivar_un_servicio_lo_saca_del_listado_publico(client, admin, make_service):
    service = make_service("Barba")

    response = client.patch(
        f"{URL}/{service.id}", json={"is_active": False}, headers=auth_headers(admin)
    )

    assert response.status_code == 200
    assert client.get(URL).json() == []


def test_renombrar_con_el_nombre_de_otro_servicio_da_409(client, admin, make_service):
    make_service("Barba")
    service = make_service("Corte")

    response = client.patch(
        f"{URL}/{service.id}", json={"name": "BARBA"}, headers=auth_headers(admin)
    )

    assert response.status_code == 409
    # El servicio no cambió (la transacción fallida se deshizo).
    assert client.get(f"{URL}/{service.id}").json()["name"] == "Corte"


def test_cambiar_solo_las_mayusculas_del_propio_nombre_esta_permitido(client, admin, make_service):
    service = make_service("barba")

    response = client.patch(
        f"{URL}/{service.id}", json={"name": "Barba"}, headers=auth_headers(admin)
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Barba"


def test_editar_un_servicio_inexistente_da_404(client, admin):
    response = client.patch(f"{URL}/999999", json={"price": "1"}, headers=auth_headers(admin))

    assert response.status_code == 404


def test_editar_como_cliente_da_403(client, client_user, make_service):
    service = make_service("Barba")

    response = client.patch(
        f"{URL}/{service.id}", json={"price": "1"}, headers=auth_headers(client_user)
    )

    assert response.status_code == 403


def test_no_existe_delete(client, admin, make_service):
    service = make_service("Barba")

    response = client.delete(f"{URL}/{service.id}", headers=auth_headers(admin))

    assert response.status_code == 405
