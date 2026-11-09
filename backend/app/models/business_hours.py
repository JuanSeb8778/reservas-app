"""Modelo BusinessHours: los tramos de apertura del negocio para cada día de la semana.

- Las horas son locales del negocio (la zona horaria está en business_settings), por eso
  son `time` sin zona.
- Puede haber varios tramos por día (p. ej. 9–13 y 15–19). Un día sin tramos está cerrado.
- El horario se reemplaza entero desde la API, así que los ids cambian: ninguna otra tabla
  debe apuntar a business_hours.id.
- Limitación: `time` no puede representar 24:00, así que el cierre más tardío es 23:59.
"""

from datetime import time

from sqlalchemy import CheckConstraint, Identity, SmallInteger, Time, literal_column
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Rango de tiempo del tramo, anclado a una fecha cualquiera porque Postgres no tiene rangos de
# `time`. '[]' = cerrado por los dos lados: 9–13 y 13–17 también chocan (comparten las 13:00);
# un horario así debe guardarse como un solo tramo 9–17.
TIME_RANGE = "tsrange(date '2000-01-01' + opens_at, date '2000-01-01' + closes_at, '[]')"


class BusinessHours(Base):
    __tablename__ = "business_hours"
    __table_args__ = (
        CheckConstraint("weekday BETWEEN 0 AND 6", name="weekday_range"),
        CheckConstraint("opens_at < closes_at", name="opens_before_closes"),
        # Restricción de exclusión: no puede haber dos filas con el mismo día (weekday =) y
        # rangos que se solapen (&&). La garantiza la base de datos aunque alguien inserte
        # directamente. `weekday WITH =` en un índice GiST necesita la extensión btree_gist.
        # Es la misma técnica que impedirá que dos citas se solapen.
        ExcludeConstraint(
            ("weekday", "="),
            (literal_column(TIME_RANGE), "&&"),
            using="gist",
            name="ex_business_hours_no_overlap",
        ),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    # 0 = lunes … 6 = domingo (igual que date.weekday() en Python).
    weekday: Mapped[int] = mapped_column(SmallInteger)
    opens_at: Mapped[time] = mapped_column(Time)
    closes_at: Mapped[time] = mapped_column(Time)
