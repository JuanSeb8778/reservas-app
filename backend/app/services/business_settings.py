"""Lectura y actualización de la configuración del negocio (una sola fila)."""

from sqlalchemy.orm import Session

from app.models import BusinessSettings
from app.schemas.business_settings import BusinessSettingsUpdate

SETTINGS_ID = 1


def get_business_settings(db: Session) -> BusinessSettings:
    settings = db.get(BusinessSettings, SETTINGS_ID)
    if settings is None:
        # La fila la crea la migración: si falta, la base de datos no está bien inicializada.
        raise RuntimeError("Falta la fila de business_settings; ejecuta 'alembic upgrade head'.")
    return settings


def update_business_settings(db: Session, data: BusinessSettingsUpdate) -> BusinessSettings:
    settings = get_business_settings(db)
    settings.timezone = data.timezone
    settings.currency = data.currency
    db.commit()
    return settings
