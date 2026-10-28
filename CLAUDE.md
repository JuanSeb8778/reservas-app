# Reservas — instrucciones para Claude Code

App fullstack de reservas de citas para negocios pequeños. Es un proyecto de **portafolio y de
aprendizaje**: el desarrollador está aprendiendo Python (FastAPI) y React. El plan completo, el
modelo de datos y el diseño de la autenticación están en @docs/PLAN.md.

## Cómo trabajar conmigo

- Responde en **español**. Código, nombres de variables, funciones, tablas y commits en **inglés**;
  comentarios en el código y textos de la interfaz en **español**.
- Estoy aprendiendo: cuando tomes una decisión de diseño no obvia, explícala en 1–3 frases
  (qué alternativa había y por qué elegiste esta). No hace falta explicar lo trivial.
- Trabaja por pasos pequeños: una funcionalidad a la vez, con sus tests, y verifica antes de seguir.
- Antes de una tarea grande (un modelo nuevo, la autenticación, un flujo completo), propón un plan
  corto y espera mi visto bueno.
- Al terminar una tarea del plan, marca su casilla en `docs/PLAN.md`.
- No añadas dependencias nuevas sin decirme cuál y por qué.

## Stack

- **Backend** (`backend/`): Python 3.13, FastAPI, SQLAlchemy 2 (estilo tipado con `Mapped[]`),
  Alembic, Pydantic v2, pydantic-settings, PostgreSQL 17 (driver `psycopg` v3), pytest, ruff.
- **Frontend** (`frontend/`): React 19 + TypeScript, Vite, Tailwind CSS v4, React Router
  (`createBrowserRouter`), TanStack Query para datos del servidor, oxlint.
  Para formularios usaremos React Hook Form + Zod (se instalan en la Fase 1).
- **Infra**: Docker Compose (`db`, `backend`, `frontend`).

## Comandos

```bash
# Todo con Docker (desde la raíz)
docker compose up --build              # frontend :5173, API :8000 (/docs), Postgres :5432
docker compose exec backend pytest     # tests del backend
docker compose exec backend alembic revision --autogenerate -m "describe change"
docker compose exec backend alembic upgrade head

# Backend sin Docker (desde backend/, con el venv activado)
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest
ruff check . && ruff format .

# Frontend sin Docker (desde frontend/)
npm install
npm run dev
npm run build      # incluye la comprobación de tipos (tsc)
npm run lint
```

## Estructura y convenciones

### Backend
- `app/main.py`: crea la app, CORS y registra los routers. Todas las rutas van bajo `/api`.
- `app/core/config.py`: configuración con `Settings` (variables de entorno). Nunca leas
  `os.environ` directamente; usa `get_settings()`.
- `app/db/`: `Base` de SQLAlchemy y la sesión (`get_db`).
- `app/models/`: un archivo por modelo. **Importa cada modelo nuevo en `app/models/__init__.py`**
  o Alembic no lo detectará.
- `app/schemas/`: modelos Pydantic de entrada/salida (p. ej. `UserCreate`, `UserRead`).
  Nunca devuelvas un modelo de SQLAlchemy directamente ni expongas `hashed_password`.
- `app/api/routes/`: un router por recurso (`auth.py`, `services.py`, `bookings.py`...).
- `app/services/`: lógica de negocio (cálculo de disponibilidad, reglas de reserva). Los routers
  deben ser delgados: validar, llamar al servicio y devolver la respuesta.
- Usa `Annotated[..., Depends(...)]` para las dependencias.
- Cambios en la base de datos **siempre** con una migración de Alembic; revisa el archivo
  generado antes de aplicarlo.
- Errores de la API con `HTTPException` y códigos correctos (400, 401, 403, 404, 409, 422).
- Tests en `backend/tests/`, usando una base de datos de pruebas separada (no la de desarrollo).

### Frontend
- `src/lib/api.ts`: `apiFetch` es el único punto que habla con la API.
- `src/features/<dominio>/`: hooks de datos (`useQuery`/`useMutation`) y componentes de ese dominio.
- `src/pages/`: una página por ruta; `src/components/`: componentes reutilizables.
- `src/router.tsx`: todas las rutas.
- Los tipos de TypeScript que reflejan respuestas de la API deben coincidir con los esquemas de
  Pydantic del backend.
- Estilos solo con clases de Tailwind. Interfaz accesible (labels en formularios, foco visible).

## Seguridad

- Nunca subas `.env` ni secretos al repositorio. Las variables nuevas van también en `.env.example`.
- El access token se guarda solo en memoria en el frontend, nunca en `localStorage`.
- Comprueba siempre en el backend que el usuario tiene permiso para el recurso (un cliente solo
  ve y modifica sus propias citas).
