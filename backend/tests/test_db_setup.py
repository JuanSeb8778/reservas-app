"""Tests de la propia infraestructura de tests (ver conftest.py)."""

import pytest
from sqlalchemy import make_url, text
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.main import app
from tests.conftest import assert_is_test_database


def test_el_client_entrega_la_sesion_de_pruebas(client, db_session):
    # Las peticiones hechas con `client` reciben `db_session`, no una sesión de desarrollo.
    override = app.dependency_overrides[get_db]

    assert next(override()) is db_session


def test_la_sesion_usa_la_base_de_pruebas(db_session):
    database = db_session.execute(text("SELECT current_database()")).scalar_one()

    assert database.endswith("_test")


def test_las_migraciones_se_aplicaron(db_session):
    table = db_session.execute(text("SELECT to_regclass('alembic_version')")).scalar_one()

    assert table is not None


def test_la_barrera_rechaza_la_base_de_desarrollo():
    with pytest.raises(RuntimeError):
        assert_is_test_database(make_url("postgresql+psycopg://u:p@localhost/reservas"))


def test_un_commit_del_test_no_se_guarda_de_verdad(db_session, engine):
    db_session.execute(text("CREATE TABLE isolation_check (id int)"))
    db_session.execute(text("INSERT INTO isolation_check VALUES (1)"))
    db_session.commit()  # solo libera un SAVEPOINT; la transacción externa sigue abierta

    # Otra conexión no ve la tabla: no se ha confirmado nada en la base.
    with engine.connect() as other:
        table = other.execute(text("SELECT to_regclass('isolation_check')")).scalar_one()
    assert table is None


def test_tras_un_error_de_integridad_la_sesion_sigue_usable(db_session):
    # Simula lo que pasará con la restricción de solapamiento de citas: un IntegrityError
    # seguido de rollback() no debe perder los datos anteriores del test.
    db_session.execute(text("CREATE TABLE unique_check (id int UNIQUE)"))
    db_session.execute(text("INSERT INTO unique_check VALUES (1)"))
    db_session.commit()

    with pytest.raises(IntegrityError):
        db_session.execute(text("INSERT INTO unique_check VALUES (1)"))
    db_session.rollback()

    count = db_session.execute(text("SELECT count(*) FROM unique_check")).scalar_one()
    assert count == 1
