"""Esquemas de servicios. Repiten las reglas de app/models/service.py para responder 422 con
un mensaje claro antes de llegar a la base de datos."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


def _empty_to_none(value: str) -> str | None:
    return value or None


# Sin caracteres de control (Postgres no admite \x00 y respondería 500 en vez de 422).
ServiceName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=100, pattern=r"^[^\x00-\x1f\x7f]+$"
    ),
]
# La descripción sí admite saltos de línea (\n = \x0a). Si queda vacía se guarda como null.
Description = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, max_length=500, pattern=r"^[^\x00-\x09\x0b-\x1f\x7f]*$"
    ),
    AfterValidator(_empty_to_none),
]
Duration = Annotated[int, Field(ge=5, le=480, multiple_of=5)]
# Decimal (no float) con 2 decimales como máximo: 10.999 se rechaza en vez de redondearse.
Price = Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=2)]


class ServiceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: ServiceName
    description: Description | None = None
    duration_minutes: Duration
    price: Price
    is_active: bool = True


class ServiceUpdate(BaseModel):
    """Edición parcial (PATCH): solo se cambian los campos enviados."""

    model_config = ConfigDict(extra="forbid")

    name: ServiceName | None = None
    description: Description | None = None
    duration_minutes: Duration | None = None
    price: Price | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def _check_fields(self) -> Self:
        # model_fields_set contiene solo los campos que llegaron en el JSON. Así se distingue
        # "no enviado" (no se toca) de "enviado como null" (solo válido en la descripción,
        # para borrarla).
        if not self.model_fields_set:
            raise ValueError("Envía al menos un campo para modificar.")
        for field in ("name", "duration_minutes", "price", "is_active"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"El campo '{field}' no puede ser null.")
        return self


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    duration_minutes: int
    # Se envía como texto ("25000.00") para no perder precisión en JSON.
    price: Decimal
    is_active: bool
    created_at: datetime
