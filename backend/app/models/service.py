"""Modelo Service: lo que ofrece el negocio (corte de cabello, consulta, alquiler de cancha...).

Los servicios no se borran: se archivan con is_active = False. Las citas (más adelante)
apuntarán a su servicio y borrarlo rompería el historial.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Identity, Index, Numeric, String, func, true
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Service(Base):
    __tablename__ = "services"
    __table_args__ = (
        # Múltiplos de 5 entre 5 min y 8 h: así las horas disponibles caen en valores limpios.
        # mod() y no el operador %: Alembic escapa el % al generar la migración y SQLAlchemy lo
        # vuelve a escapar al ejecutarla, y el SQL resultante (%%%%) no es válido.
        CheckConstraint(
            "duration_minutes BETWEEN 5 AND 480 AND mod(duration_minutes, 5) = 0",
            name="duration_valid",
        ),
        CheckConstraint("price >= 0", name="price_non_negative"),
        # Sin espacios al principio o al final: " Corte" parecería distinto de "Corte".
        CheckConstraint("name = btrim(name) AND name <> ''", name="name_trimmed"),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500))
    duration_minutes: Mapped[int]
    # Numeric (no float): el dinero necesita decimales exactos. 0.1 + 0.2 en float da
    # 0.30000000000000004. Hasta 99 999 999.99, suficiente incluso para pesos colombianos.
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# Nombre único sin distinguir mayúsculas: "Corte" y "corte" no pueden convivir. Es un índice
# sobre una expresión (lower(name)), por eso va fuera de la clase y con nombre explícito (la
# convención de nombres de db/base.py no sabe nombrar expresiones). Incluye los servicios
# archivados: un nombre archivado sigue ocupado, para poder reactivarlo sin choques.
Index("uq_services_name_lower", func.lower(Service.name), unique=True)
