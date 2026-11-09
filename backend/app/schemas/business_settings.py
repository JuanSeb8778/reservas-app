"""Esquemas de la configuración del negocio (zona horaria y moneda)."""

from functools import cache
from typing import Annotated
from zoneinfo import available_timezones

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, StringConstraints


@cache
def _known_timezones() -> frozenset[str]:
    # La lista de zonas IANA del sistema (~500 nombres). Se calcula una sola vez.
    return frozenset(available_timezones())


def _validate_timezone(value: str) -> str:
    # Se exige el nombre exacto: "america/bogota" no es válido aunque Windows lo aceptara.
    if value not in _known_timezones():
        raise ValueError("Zona horaria desconocida. Usa un nombre IANA, p. ej. 'America/Bogota'.")
    return value


Timezone = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=64),
    AfterValidator(_validate_timezone),
]


def _normalize_code(value: object) -> object:
    return value.strip().upper() if isinstance(value, str) else value


# Código ISO 4217: tres letras. Se acepta en minúsculas ("cop") y se guarda en mayúsculas.
# La normalización va en un BeforeValidator porque Pydantic comprueba `pattern` antes de
# aplicar `to_upper`: con StringConstraints(to_upper=True, pattern=...) "cop" se rechazaría.
Currency = Annotated[
    str, BeforeValidator(_normalize_code), StringConstraints(pattern=r"^[A-Z]{3}$")
]


class BusinessSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timezone: str
    currency: str


class BusinessSettingsUpdate(BaseModel):
    """Reemplaza la configuración completa (PUT): los dos campos son obligatorios."""

    model_config = ConfigDict(extra="forbid")

    timezone: Timezone
    currency: Currency
