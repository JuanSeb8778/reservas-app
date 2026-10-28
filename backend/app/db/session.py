"""Conexión a PostgreSQL.

- `engine`: el "motor" que maneja el pool de conexiones a la base de datos.
- `SessionLocal`: fábrica de sesiones; cada petición HTTP usa su propia sesión.
- `get_db`: dependencia de FastAPI que abre una sesión y la cierra al terminar.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

engine = create_engine(get_settings().database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
