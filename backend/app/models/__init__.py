"""Modelos de la base de datos.

Importa cada modelo nuevo en este archivo para que Alembic lo detecte al generar migraciones.
"""

from app.db.base import Base  # noqa: F401
from app.models.enums import UserRole  # noqa: F401
from app.models.user import User  # noqa: F401
