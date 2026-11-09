"""Tests del modelo Service y de las restricciones que impone la base de datos."""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Service


def make_service(**overrides) -> Service:
    data = {"name": "Corte clásico", "duration_minutes": 30, "price": Decimal("25000.00")}
    return Service(**(data | overrides))


def test_un_servicio_nuevo_esta_activo_y_tiene_fecha(db_session):
    service = make_service()
    db_session.add(service)
    db_session.flush()
    db_session.refresh(service)

    assert service.is_active is True
    assert service.created_at.tzinfo is not None
    assert service.description is None
    assert service.price == Decimal("25000.00")


@pytest.mark.parametrize("minutes", [0, 4, 7, 481, 485])
def test_la_duracion_debe_ser_multiplo_de_5_entre_5_y_480(db_session, minutes):
    db_session.add(make_service(duration_minutes=minutes))
    with pytest.raises(IntegrityError, match="ck_services_duration_valid"):
        db_session.flush()


@pytest.mark.parametrize("minutes", [5, 45, 480])
def test_duraciones_validas(db_session, minutes):
    db_session.add(make_service(duration_minutes=minutes))
    db_session.flush()


def test_el_precio_no_puede_ser_negativo(db_session):
    db_session.add(make_service(price=Decimal("-1")))
    with pytest.raises(IntegrityError, match="ck_services_price_non_negative"):
        db_session.flush()


def test_un_servicio_puede_ser_gratis(db_session):
    db_session.add(make_service(price=Decimal("0")))
    db_session.flush()


@pytest.mark.parametrize("name", ["", " Corte", "Corte ", "   "])
def test_el_nombre_no_puede_estar_vacio_ni_tener_espacios_en_los_bordes(db_session, name):
    db_session.add(make_service(name=name))
    with pytest.raises(IntegrityError, match="ck_services_name_trimmed"):
        db_session.flush()


def test_el_nombre_es_unico_sin_distinguir_mayusculas(db_session):
    db_session.add(make_service(name="Corte"))
    db_session.flush()

    db_session.add(make_service(name="CORTE"))
    with pytest.raises(IntegrityError, match="uq_services_name_lower"):
        db_session.flush()


def test_un_servicio_archivado_sigue_ocupando_su_nombre(db_session):
    db_session.add(make_service(name="Corte", is_active=False))
    db_session.flush()

    db_session.add(make_service(name="corte"))
    with pytest.raises(IntegrityError, match="uq_services_name_lower"):
        db_session.flush()
