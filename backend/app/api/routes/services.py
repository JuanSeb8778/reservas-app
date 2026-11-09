"""Servicios del negocio.

- Cualquiera ve los servicios activos (la página pública los lista).
- El administrador ve también los archivados y es el único que crea y edita.
- No hay DELETE: un servicio se archiva con is_active = false (las citas lo referencian).
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AdminUser, DbSession, OptionalUser, is_admin, unauthorized
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate
from app.services.catalog import (
    DuplicateServiceNameError,
    create_service,
    get_service,
    list_services,
    update_service,
)

router = APIRouter(prefix="/services", tags=["services"])

NOT_FOUND = "El servicio no existe"
DUPLICATE_NAME = "Ya existe un servicio con ese nombre"

_auth_errors = {
    status.HTTP_401_UNAUTHORIZED: {"description": "No autenticado o token inválido"},
    status.HTTP_403_FORBIDDEN: {"description": "Solo para administradores"},
}
_not_found = {status.HTTP_404_NOT_FOUND: {"description": NOT_FOUND}}
_conflict = {status.HTTP_409_CONFLICT: {"description": DUPLICATE_NAME}}


@router.get("", responses=_auth_errors)
def read_services(
    db: DbSession,
    user: OptionalUser,
    include_inactive: Annotated[
        bool, Query(description="Incluir servicios archivados (solo administradores)")
    ] = False,
) -> list[ServiceRead]:
    # Pedir los archivados sin ser admin es un error del cliente: se responde 401/403 en vez
    # de ignorar el parámetro en silencio (así un fallo del frontend no pasa desapercibido).
    if include_inactive and not is_admin(user):
        if user is None:
            raise unauthorized("No autenticado")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso para esta acción")
    services = list_services(db, include_inactive=include_inactive)
    return [ServiceRead.model_validate(service) for service in services]


@router.get("/{service_id}", responses=_not_found)
def read_service(service_id: int, db: DbSession, user: OptionalUser) -> ServiceRead:
    service = get_service(db, service_id, include_inactive=is_admin(user))
    if service is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
    return ServiceRead.model_validate(service)


@router.post("", status_code=status.HTTP_201_CREATED, responses=_auth_errors | _conflict)
def create(data: ServiceCreate, db: DbSession, _admin: AdminUser) -> ServiceRead:
    try:
        service = create_service(db, data)
    except DuplicateServiceNameError:
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_NAME) from None
    return ServiceRead.model_validate(service)


@router.patch("/{service_id}", responses=_auth_errors | _not_found | _conflict)
def update(service_id: int, data: ServiceUpdate, db: DbSession, _admin: AdminUser) -> ServiceRead:
    service = get_service(db, service_id, include_inactive=True)
    if service is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
    try:
        service = update_service(db, service, data)
    except DuplicateServiceNameError:
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE_NAME) from None
    return ServiceRead.model_validate(service)
