"""Clase base de los modelos de SQLAlchemy.

Todos los modelos (User, Service, Booking...) heredarán de `Base`.
Alembic usa `Base.metadata` para detectar cambios y generar migraciones.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Convención de nombres para índices y restricciones. Sin ella, Postgres inventa los nombres
# (p. ej. `users_email_key`) y las migraciones futuras no pueden referirse a ellos de forma
# fiable para borrarlos o cambiarlos. Se define antes de la primera migración porque
# cambiarla después obligaría a renombrar todo lo ya creado.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Cuando crees modelos en app/models/, impórtalos en app/models/__init__.py
# para que Alembic los vea al generar migraciones.
