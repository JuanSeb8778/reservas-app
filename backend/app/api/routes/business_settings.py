"""Configuración del negocio: la lee cualquiera (la web necesita la moneda y la zona horaria),
la cambia solo el administrador."""

from fastapi import APIRouter, status

from app.api.deps import AdminUser, DbSession
from app.schemas.business_settings import BusinessSettingsRead, BusinessSettingsUpdate
from app.services.business_settings import get_business_settings, update_business_settings

router = APIRouter(prefix="/business-settings", tags=["business-settings"])

_admin_only = {
    status.HTTP_401_UNAUTHORIZED: {"description": "No autenticado o token inválido"},
    status.HTTP_403_FORBIDDEN: {"description": "Solo para administradores"},
}


@router.get("")
def read_business_settings(db: DbSession) -> BusinessSettingsRead:
    return BusinessSettingsRead.model_validate(get_business_settings(db))


@router.put("", responses=_admin_only)
def replace_business_settings(
    data: BusinessSettingsUpdate, db: DbSession, _admin: AdminUser
) -> BusinessSettingsRead:
    return BusinessSettingsRead.model_validate(update_business_settings(db, data))
