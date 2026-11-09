"""Tests del modelo BusinessSettings y de las restricciones que impone la base de datos."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models import BusinessSettings


def test_la_migracion_crea_la_fila_con_valores_iniciales(db_session):
    settings = db_session.get(BusinessSettings, 1)

    assert settings is not None
    assert settings.timezone == "America/Bogota"
    assert settings.currency == "COP"


def test_solo_puede_existir_la_fila_con_id_1(db_session):
    with pytest.raises(IntegrityError, match="ck_business_settings_single_row"):
        db_session.execute(
            text("INSERT INTO business_settings (id, timezone, currency) VALUES (2, 'UTC', 'USD')")
        )


def test_no_se_puede_crear_una_segunda_fila_sin_id(db_session):
    # Sin id, la base de datos usa 1, que ya existe: choca con la clave primaria.
    with pytest.raises(IntegrityError, match="pk_business_settings"):
        db_session.execute(
            text("INSERT INTO business_settings (timezone, currency) VALUES ('UTC', 'USD')")
        )


# (Un código de 4 letras ni llega al CHECK: la columna es VARCHAR(3) y Postgres lo rechaza por
# longitud. Ese caso lo cubre el test de la API.)
@pytest.mark.parametrize("currency", ["cop", "CO", "C0P"])
def test_la_moneda_debe_ser_un_codigo_de_tres_mayusculas(db_session, currency):
    with pytest.raises(IntegrityError, match="ck_business_settings_currency_format"):
        db_session.execute(
            text("UPDATE business_settings SET currency = :currency WHERE id = 1"),
            {"currency": currency},
        )


def test_la_zona_horaria_no_puede_estar_vacia(db_session):
    with pytest.raises(IntegrityError, match="ck_business_settings_timezone_not_empty"):
        db_session.execute(text("UPDATE business_settings SET timezone = '  ' WHERE id = 1"))
