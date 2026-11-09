"""Catálogo de servicios del negocio.

(Se llama `catalog` y no `services` para no confundirse con el paquete app/services.)
"""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Service
from app.schemas.service import ServiceCreate, ServiceUpdate

UNIQUE_NAME_INDEX = "uq_services_name_lower"


class DuplicateServiceNameError(Exception):
    """Ya existe un servicio con ese nombre (sin distinguir mayúsculas)."""


def list_services(db: Session, *, include_inactive: bool = False) -> list[Service]:
    statement = select(Service).order_by(func.lower(Service.name))
    if not include_inactive:
        statement = statement.where(Service.is_active)
    return list(db.scalars(statement))


def get_service(db: Session, service_id: int, *, include_inactive: bool = False) -> Service | None:
    """None si no existe o si está archivado y no se piden los inactivos (para quien no es
    admin, un servicio archivado "no existe": no se revela que esté ahí)."""
    service = db.get(Service, service_id)
    if service is None or (not service.is_active and not include_inactive):
        return None
    return service


def create_service(db: Session, data: ServiceCreate) -> Service:
    service = Service(**data.model_dump())
    db.add(service)
    _commit(db)
    db.refresh(service)  # created_at lo pone la base de datos
    return service


def update_service(db: Session, service: Service, data: ServiceUpdate) -> Service:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    _commit(db)
    db.refresh(service)
    return service


def _commit(db: Session) -> None:
    # No se comprueba antes si el nombre existe: dos peticiones a la vez podrían pasar esa
    # comprobación. El índice único de la base de datos decide, y aquí se traduce su error.
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        diag = getattr(exc.orig, "diag", None)
        if diag is not None and diag.constraint_name == UNIQUE_NAME_INDEX:
            raise DuplicateServiceNameError from exc
        raise
