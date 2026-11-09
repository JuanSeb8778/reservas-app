"""Modelo BusinessSettings: la configuración del negocio (zona horaria y moneda).

Es una tabla de una sola fila. La crea la migración con valores iniciales y el administrador
la edita desde la app (por eso no son variables de entorno: esas solo cambian al redesplegar).
"""

from sqlalchemy import CheckConstraint, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BusinessSettings(Base):
    __tablename__ = "business_settings"
    __table_args__ = (
        # Solo puede existir la fila con id = 1: hay una única configuración para todo el negocio.
        CheckConstraint("id = 1", name="single_row"),
        # Código ISO 4217 de tres letras en mayúsculas (COP, USD, EUR...).
        CheckConstraint("currency ~ '^[A-Z]{3}$'", name="currency_format"),
        # Que sea una zona horaria real (p. ej. "America/Bogota") lo valida la API con zoneinfo:
        # Postgres no puede comprobarlo en un CHECK (necesitaría consultar otra tabla).
        CheckConstraint("btrim(timezone) <> ''", name="timezone_not_empty"),
    )

    # Sin Identity: el id no se genera, siempre es 1.
    id: Mapped[int] = mapped_column(
        SmallInteger, primary_key=True, autoincrement=False, server_default=text("1")
    )
    # Nombre IANA, p. ej. "America/Bogota". Las horas de apertura (business_hours) son horas
    # locales de esta zona. Los nombres IANA más largos rondan los 30 caracteres.
    timezone: Mapped[str] = mapped_column(String(64))
    currency: Mapped[str] = mapped_column(String(3))
