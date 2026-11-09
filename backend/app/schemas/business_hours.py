"""Esquemas del horario del negocio.

Las horas viajan como "HH:MM" en los dos sentidos (se acepta "09:00" y se devuelve "09:00").
Son horas locales del negocio: la zona horaria está en /api/business-settings.
"""

from datetime import time
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    model_validator,
)

WEEKDAY_NAMES = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")


def _local_minute(value: time) -> time:
    if value.tzinfo is not None:
        raise ValueError("La hora no lleva zona horaria: es la hora local del negocio.")
    if value.second or value.microsecond:
        raise ValueError("Usa horas sin segundos, con el formato HH:MM.")
    return value


LocalTime = Annotated[time, AfterValidator(_local_minute)]


class BusinessHoursRange(BaseModel):
    """Un tramo de apertura: el lunes (0) de 09:00 a 13:00."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    weekday: Annotated[int, Field(ge=0, le=6, description="0 = lunes … 6 = domingo")]
    opens_at: LocalTime
    closes_at: LocalTime

    @model_validator(mode="after")
    def _opens_before_closes(self) -> Self:
        if self.opens_at >= self.closes_at:
            raise ValueError("La hora de apertura debe ser anterior a la de cierre.")
        return self

    @field_serializer("opens_at", "closes_at")
    def _as_hh_mm(self, value: time) -> str:
        return value.strftime("%H:%M")


class BusinessHoursWeek(BaseModel):
    """La semana completa. GET la devuelve y PUT la reemplaza entera (mismo formato).

    Sin tramos para un día = ese día está cerrado. Lista vacía = cerrado toda la semana.
    """

    model_config = ConfigDict(extra="forbid")

    # 70 = 10 tramos por día: un límite holgado que evita peticiones absurdamente grandes.
    ranges: Annotated[list[BusinessHoursRange], Field(max_length=70)]

    @model_validator(mode="after")
    def _no_overlaps(self) -> Self:
        # Se ordena por día y hora: dos tramos chocan si, siendo del mismo día, el siguiente
        # empieza antes de que termine el anterior (o justo cuando termina: 9–13 y 13–17 son
        # en realidad un tramo 9–17 y se pide guardarlo así). La base de datos lo comprueba
        # también (ex_business_hours_no_overlap); aquí se valida antes para dar un 422 claro.
        ordered = sorted(self.ranges, key=lambda r: (r.weekday, r.opens_at))
        for previous, current in zip(ordered, ordered[1:], strict=False):
            if current.weekday == previous.weekday and current.opens_at <= previous.closes_at:
                day = WEEKDAY_NAMES[current.weekday]
                raise ValueError(
                    f"Los tramos del {day} se solapan o se tocan. Únelos en uno solo o sepáralos."
                )
        return self
