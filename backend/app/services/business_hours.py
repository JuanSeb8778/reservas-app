"""Lectura y reemplazo del horario semanal del negocio."""

from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import BusinessHours, BusinessSettings
from app.schemas.business_hours import BusinessHoursRange
from app.services.business_settings import SETTINGS_ID


def list_business_hours(db: Session) -> list[BusinessHours]:
    statement = select(BusinessHours).order_by(BusinessHours.weekday, BusinessHours.opens_at)
    return list(db.scalars(statement))


def replace_business_hours(
    db: Session, ranges: Sequence[BusinessHoursRange]
) -> list[BusinessHours]:
    """Borra la semana y guarda la nueva en una sola transacción: o se guarda todo o nada."""
    # Candado: si dos administradores guardan a la vez, sin esto los dos borrarían la semana
    # vieja y luego insertarían sus tramos, y el resultado mezclaría ambos horarios.
    # FOR UPDATE bloquea la fila única de configuración hasta el commit, así que el segundo
    # guardado espera a que termine el primero (y luego lo reemplaza entero).
    db.execute(
        select(BusinessSettings.id).where(BusinessSettings.id == SETTINGS_ID).with_for_update()
    )
    db.execute(delete(BusinessHours))
    db.add_all(BusinessHours(**r.model_dump(mode="python")) for r in ranges)
    try:
        db.commit()
    except Exception:
        db.rollback()  # la semana anterior queda intacta
        raise
    return list_business_hours(db)
