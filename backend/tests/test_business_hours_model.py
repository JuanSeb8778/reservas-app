"""Tests del modelo BusinessHours y de las restricciones que impone la base de datos,
incluida la restricción de exclusión que impide tramos solapados el mismo día."""

from datetime import time

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import BusinessHours

MONDAY, TUESDAY = 0, 1


def add_range(db_session, weekday: int, opens: int, closes: int) -> None:
    db_session.add(BusinessHours(weekday=weekday, opens_at=time(opens), closes_at=time(closes)))
    db_session.flush()


def test_se_pueden_guardar_varios_tramos_separados_el_mismo_dia(db_session):
    add_range(db_session, MONDAY, 9, 13)
    add_range(db_session, MONDAY, 15, 19)

    assert db_session.query(BusinessHours).count() == 2


def test_el_mismo_tramo_en_dias_distintos_esta_permitido(db_session):
    add_range(db_session, MONDAY, 9, 17)
    add_range(db_session, TUESDAY, 9, 17)


@pytest.mark.parametrize("weekday", [-1, 7])
def test_el_dia_debe_estar_entre_0_y_6(db_session, weekday):
    with pytest.raises(IntegrityError, match="ck_business_hours_weekday_range"):
        add_range(db_session, weekday, 9, 17)


@pytest.mark.parametrize(("opens", "closes"), [(17, 9), (9, 9)])
def test_la_apertura_debe_ser_antes_del_cierre(db_session, opens, closes):
    with pytest.raises(IntegrityError, match="ck_business_hours_opens_before_closes"):
        add_range(db_session, MONDAY, opens, closes)


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ((9, 13), (12, 15)),  # se pisan
        ((9, 17), (10, 12)),  # uno dentro del otro
        ((9, 13), (13, 17)),  # se tocan en las 13:00 (deben guardarse como un solo tramo)
        ((9, 13), (9, 13)),  # repetido
    ],
)
def test_la_base_de_datos_rechaza_tramos_que_se_solapan_o_tocan(db_session, first, second):
    add_range(db_session, MONDAY, *first)

    with pytest.raises(IntegrityError, match="ex_business_hours_no_overlap"):
        add_range(db_session, MONDAY, *second)
