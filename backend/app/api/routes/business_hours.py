"""Horario de apertura del negocio: lo ve cualquiera (página pública y cálculo de
disponibilidad) y solo el administrador lo reemplaza."""

from fastapi import APIRouter, status

from app.api.deps import AdminUser, DbSession
from app.schemas.business_hours import BusinessHoursRange, BusinessHoursWeek
from app.services.business_hours import list_business_hours, replace_business_hours

router = APIRouter(prefix="/business-hours", tags=["business-hours"])

_admin_only = {
    status.HTTP_401_UNAUTHORIZED: {"description": "No autenticado o token inválido"},
    status.HTTP_403_FORBIDDEN: {"description": "Solo para administradores"},
}


def _to_week(rows: list) -> BusinessHoursWeek:
    return BusinessHoursWeek(ranges=[BusinessHoursRange.model_validate(row) for row in rows])


@router.get("")
def read_business_hours(db: DbSession) -> BusinessHoursWeek:
    return _to_week(list_business_hours(db))


@router.put("", responses=_admin_only)
def replace_week(data: BusinessHoursWeek, db: DbSession, _admin: AdminUser) -> BusinessHoursWeek:
    return _to_week(replace_business_hours(db, data.ranges))
