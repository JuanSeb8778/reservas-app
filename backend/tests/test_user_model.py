"""Tests del modelo User y de las restricciones que impone la base de datos."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models import User, UserRole


def make_user(**overrides) -> User:
    data = {"email": "ana@example.com", "hashed_password": "hash", "full_name": "Ana Pérez"}
    return User(**(data | overrides))


def test_un_usuario_nuevo_tiene_rol_client_y_fecha_por_defecto(db_session):
    user = make_user()
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)  # created_at lo pone la base de datos; se recarga para leerlo

    assert isinstance(user.id, int)
    assert user.role == UserRole.CLIENT
    assert user.created_at.tzinfo is not None


def test_el_rol_se_guarda_con_su_valor_en_minusculas(db_session):
    db_session.add(make_user(role=UserRole.ADMIN))
    db_session.flush()

    stored = db_session.execute(text("SELECT role FROM users")).scalar_one()
    assert stored == "admin"


def test_un_insert_directo_sin_rol_usa_client(db_session):
    db_session.execute(
        text(
            "INSERT INTO users (email, hashed_password, full_name) "
            "VALUES ('seed@example.com', 'hash', 'Seed')"
        )
    )

    stored = db_session.execute(text("SELECT role FROM users")).scalar_one()
    assert stored == "client"


def test_dos_emails_distintos_conviven(db_session):
    db_session.add_all([make_user(), make_user(email="luis@example.com")])
    db_session.flush()

    assert db_session.execute(text("SELECT count(*) FROM users")).scalar_one() == 2


def test_un_email_duplicado_lanza_integrity_error(db_session):
    db_session.add(make_user())
    db_session.flush()

    db_session.add(make_user(full_name="Otra Ana"))
    with pytest.raises(IntegrityError, match="uq_users_email"):
        db_session.flush()


def test_un_email_con_mayusculas_lo_rechaza_la_base_de_datos(db_session):
    db_session.add(make_user(email="Ana@Example.com"))

    with pytest.raises(IntegrityError, match="ck_users_email_lowercase"):
        db_session.flush()


def test_un_rol_invalido_lo_rechaza_la_base_de_datos(db_session):
    with pytest.raises(IntegrityError, match="ck_users_user_role"):
        db_session.execute(
            text(
                "INSERT INTO users (email, hashed_password, full_name, role) "
                "VALUES ('x@example.com', 'hash', 'X', 'superuser')"
            )
        )


@pytest.mark.parametrize("column", ["email", "hashed_password", "full_name"])
def test_los_campos_obligatorios_no_admiten_null(db_session, column):
    values = {"email": "'x@example.com'", "hashed_password": "'hash'", "full_name": "'X'"}
    values[column] = "NULL"

    with pytest.raises(IntegrityError, match="not-null"):
        db_session.execute(
            text(
                "INSERT INTO users (email, hashed_password, full_name) "
                f"VALUES ({values['email']}, {values['hashed_password']}, {values['full_name']})"
            )
        )
