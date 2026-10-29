"""Comprueba que las migraciones de Alembic están al día con los modelos.

Si alguien cambia un modelo y olvida generar la migración, este test falla y muestra la
diferencia. Limitación: Alembic no compara restricciones CHECK (p. ej. un valor nuevo en
UserRole), así que esas se cubren con tests de comportamiento en cada modelo.
"""

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from app.models import Base


def test_el_esquema_migrado_coincide_con_los_modelos(engine):
    # Conexión propia (no db_session) para comparar solo lo que dejaron las migraciones.
    with engine.connect() as connection:
        context = MigrationContext.configure(connection, opts={"compare_type": True})
        diff = compare_metadata(context, Base.metadata)

    assert diff == [], f"Falta una migración para estos cambios: {diff}"
