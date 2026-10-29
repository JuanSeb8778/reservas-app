"""Fixtures compartidas por todos los tests.

Los tests usan una base de datos propia (`<base de desarrollo>_test`, p. ej. `reservas_test`)
en el mismo servidor de PostgreSQL. En cada ejecución de pytest:

1. Se borra y se vuelve a crear la base de pruebas, para empezar siempre desde cero.
2. Se aplican las migraciones de Alembic (`upgrade head`). Así los tests prueban el mismo
   esquema que producción, incluidas extensiones y restricciones que `create_all` no crea.
3. Cada test corre dentro de una transacción que se deshace al terminar, de modo que lo que
   escribe un test nunca lo ve el siguiente.
"""

from collections.abc import Generator
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import URL, Engine, create_engine, make_url, text
from sqlalchemy.orm import Session

from alembic import command
from app.core.config import get_settings
from app.db.session import get_db
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parent.parent


def get_test_database_url() -> URL:
    """Deriva la URL de pruebas de la de desarrollo: mismo servidor, base `<nombre>_test`.

    Derivarla (en vez de configurarla aparte) evita que alguien la apunte por error a la
    base de desarrollo.
    """
    url = make_url(get_settings().database_url)
    return url.set(database=f"{url.database}_test")


def assert_is_test_database(url: URL) -> None:
    """Barrera de seguridad: nunca borramos ni migramos una base que no termine en `_test`."""
    if not url.database or not url.database.endswith("_test"):
        raise RuntimeError(f"Los tests solo pueden usar una base '*_test', no '{url.database}'")


def recreate_database(url: URL) -> None:
    """Borra (si existe) y crea la base de pruebas.

    `CREATE DATABASE` no puede ejecutarse dentro de una transacción, por eso esta conexión
    usa AUTOCOMMIT y se conecta a la base de mantenimiento `postgres`.
    """
    assert_is_test_database(url)
    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    # El nombre de una base no se puede pasar como parámetro; se entrecomilla con
    # quote_identifier y ya se validó arriba.
    name = admin_engine.dialect.identifier_preparer.quote_identifier(url.database)
    with admin_engine.connect() as conn:
        # WITH (FORCE) cierra conexiones que hayan quedado abiertas de una ejecución anterior.
        conn.execute(text(f"DROP DATABASE IF EXISTS {name} WITH (FORCE)"))
        conn.execute(text(f"CREATE DATABASE {name}"))
    admin_engine.dispose()


@pytest.fixture(scope="session")
def engine() -> Generator[Engine]:
    """Engine de la base de pruebas, recreada y migrada una vez por ejecución de pytest."""
    url = get_test_database_url()
    try:
        recreate_database(url)
    except RuntimeError as exc:
        pytest.exit(str(exc), returncode=1)

    test_engine = create_engine(url)
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    with test_engine.begin() as conn:
        # env.py usa esta conexión en lugar de la URL de desarrollo.
        alembic_cfg.attributes["connection"] = conn
        command.upgrade(alembic_cfg, "head")

    yield test_engine
    test_engine.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Generator[Session]:
    """Sesión dentro de una transacción externa que se deshace al terminar el test.

    join_transaction_mode="create_savepoint": si el código de la app hace `commit()` o
    `rollback()`, solo afecta a un SAVEPOINT; la transacción externa sigue abierta y se
    revierte al final. Las demás opciones son iguales que en `SessionLocal`.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
        autoflush=False,
        expire_on_commit=False,
    )
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient]:
    """Cliente HTTP de pruebas cuyas peticiones usan `db_session` en lugar de la base real."""

    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Aunque el test falle, el siguiente no debe heredar el override.
        app.dependency_overrides.clear()
