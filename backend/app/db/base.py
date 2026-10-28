"""Clase base de los modelos de SQLAlchemy.

Todos los modelos (User, Service, Booking...) heredarán de `Base`.
Alembic usa `Base.metadata` para detectar cambios y generar migraciones.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Cuando crees modelos en app/models/, impórtalos en app/models/__init__.py
# para que Alembic los vea al generar migraciones.
