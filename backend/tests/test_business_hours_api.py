"""Tests de /api/business-hours y del reemplazo atómico de la semana."""

from datetime import time

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import BusinessHours, UserRole
from app.schemas.business_hours import BusinessHoursRange
from app.services.business_hours import replace_business_hours
from tests.helpers import auth_headers

URL = "/api/business-hours"
MONDAY, TUESDAY, SATURDAY = 0, 1, 5


def rng(weekday: int, opens: str, closes: str) -> dict:
    return {"weekday": weekday, "opens_at": opens, "closes_at": closes}


@pytest.fixture
def admin(create_user):
    return create_user(email="admin@example.com", role=UserRole.ADMIN)


@pytest.fixture
def existing_week(db_session):
    """Un horario ya guardado: lunes 08:00–12:00."""
    db_session.add(BusinessHours(weekday=MONDAY, opens_at=time(8), closes_at=time(12)))
    db_session.commit()  # ya existía antes de la petición (ver test_services_api.py)


def test_sin_horario_la_semana_esta_cerrada(client):
    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == {"ranges": []}


def test_cambiar_el_horario_sin_sesion_da_401_y_como_cliente_403(client, create_user):
    week = {"ranges": [rng(MONDAY, "09:00", "17:00")]}

    assert client.put(URL, json=week).status_code == 401
    assert client.put(URL, json=week, headers=auth_headers(create_user())).status_code == 403


def test_el_admin_guarda_la_semana_y_se_devuelve_ordenada_en_formato_hh_mm(client, admin):
    week = {
        "ranges": [
            rng(SATURDAY, "10:00", "14:00"),
            rng(MONDAY, "15:00", "19:00"),
            rng(MONDAY, "09:00", "13:00"),
        ]
    }

    response = client.put(URL, json=week, headers=auth_headers(admin))

    expected = {
        "ranges": [
            rng(MONDAY, "09:00", "13:00"),
            rng(MONDAY, "15:00", "19:00"),
            rng(SATURDAY, "10:00", "14:00"),
        ]
    }
    assert response.status_code == 200
    assert response.json() == expected
    assert client.get(URL).json() == expected


def test_guardar_reemplaza_la_semana_anterior_por_completo(client, admin, existing_week):
    week = {"ranges": [rng(TUESDAY, "09:00", "17:00")]}

    client.put(URL, json=week, headers=auth_headers(admin))

    assert client.get(URL).json() == week


def test_una_lista_vacia_cierra_toda_la_semana(client, admin, existing_week):
    response = client.put(URL, json={"ranges": []}, headers=auth_headers(admin))

    assert response.status_code == 200
    assert client.get(URL).json() == {"ranges": []}


def test_el_mismo_tramo_en_varios_dias_esta_permitido(client, admin):
    week = {"ranges": [rng(day, "09:00", "17:00") for day in range(7)]}

    assert client.put(URL, json=week, headers=auth_headers(admin)).status_code == 200


@pytest.mark.parametrize(
    "ranges",
    [
        [rng(MONDAY, "09:00", "13:00"), rng(MONDAY, "12:00", "15:00")],  # se pisan
        [rng(MONDAY, "09:00", "13:00"), rng(MONDAY, "13:00", "17:00")],  # se tocan
        [rng(MONDAY, "09:00", "17:00"), rng(MONDAY, "10:00", "11:00")],  # uno dentro de otro
    ],
)
def test_tramos_que_se_solapan_o_tocan_dan_422_y_no_cambian_nada(
    client, admin, existing_week, ranges
):
    response = client.put(URL, json={"ranges": ranges}, headers=auth_headers(admin))

    assert response.status_code == 422
    assert "lunes" in response.text  # el mensaje dice qué día revisar
    assert client.get(URL).json() == {"ranges": [rng(MONDAY, "08:00", "12:00")]}


@pytest.mark.parametrize(
    "bad_range",
    [
        rng(MONDAY, "17:00", "09:00"),  # apertura después del cierre
        rng(MONDAY, "09:00", "09:00"),  # tramo vacío
        rng(7, "09:00", "17:00"),  # día inexistente
        rng(-1, "09:00", "17:00"),
        rng(MONDAY, "09:00:30", "17:00"),  # segundos
        rng(MONDAY, "09:00+05:00", "17:00"),  # con zona horaria
        rng(MONDAY, "25:00", "26:00"),  # hora imposible
        rng(MONDAY, "nueve", "17:00"),
        rng(MONDAY, "09:00", "17:00") | {"extra": 1},
    ],
)
def test_tramos_invalidos_dan_422(client, admin, bad_range):
    response = client.put(URL, json={"ranges": [bad_range]}, headers=auth_headers(admin))

    assert response.status_code == 422


def test_no_se_aceptan_mas_de_70_tramos(client, admin):
    ranges = [rng(MONDAY, f"{h:02d}:00", f"{h:02d}:30") for h in range(24)] * 3

    response = client.put(URL, json={"ranges": ranges}, headers=auth_headers(admin))

    assert response.status_code == 422


def test_si_falla_al_guardar_se_conserva_la_semana_anterior(db_session, existing_week):
    # Se salta la validación de Pydantic (model_construct) para que sea la base de datos la
    # que rechace los tramos solapados a mitad del guardado.
    overlapping = [
        BusinessHoursRange.model_construct(weekday=TUESDAY, opens_at=time(9), closes_at=time(13)),
        BusinessHoursRange.model_construct(weekday=TUESDAY, opens_at=time(12), closes_at=time(15)),
    ]

    with pytest.raises(IntegrityError, match="ex_business_hours_no_overlap"):
        replace_business_hours(db_session, overlapping)

    remaining = db_session.query(BusinessHours).all()
    assert [(h.weekday, h.opens_at, h.closes_at) for h in remaining] == [
        (MONDAY, time(8), time(12))
    ]
