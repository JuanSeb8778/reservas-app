"""Modelo User: las personas que usan la app (clientes y administradores)."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, Identity, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        # La API guarda el email en minúsculas; esta restricción lo garantiza también para
        # inserciones directas (p. ej. el seed), así "Ana@x.com" y "ana@x.com" no conviven.
        CheckConstraint("email = lower(email)", name="email_lowercase"),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    # 254 caracteres es el límite práctico de una dirección de correo (RFC 5321).
    email: Mapped[str] = mapped_column(String(254), unique=True)
    # Hash Argon2 en formato PHC (~100 caracteres); 255 deja margen si cambian los parámetros.
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    # native_enum=False: se guarda como VARCHAR + CHECK en vez de un tipo ENUM de Postgres,
    # que es incómodo de modificar en migraciones. create_constraint=True crea ese CHECK.
    # values_callable guarda los valores ("client") y no los nombres ("CLIENT").
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda roles: [role.value for role in roles],
        ),
        default=UserRole.CLIENT,
        server_default=UserRole.CLIENT.value,
    )
    # timezone=True → timestamptz. La hora la pone la base de datos al insertar.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
