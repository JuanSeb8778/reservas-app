# Reservas

App fullstack para agendar citas en negocios pequeños: los clientes ven horarios libres y reservan,
y el administrador gestiona servicios, horarios y citas.

> 🚧 En desarrollo. Plan y progreso en [`docs/PLAN.md`](docs/PLAN.md).

## Stack

| Capa | Tecnologías |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Pydantic |
| Base de datos | PostgreSQL 17 |
| Infra | Docker Compose |

## Cómo ejecutarlo

Requisitos: [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- API y documentación interactiva: http://localhost:8000/docs

Si todo está bien, la página de inicio muestra los tres servicios en verde.

### Tests

```bash
docker compose exec backend pytest
```

## Estructura

```
reservas-app/
├── backend/          # API con FastAPI
│   ├── app/
│   │   ├── api/routes/   # endpoints
│   │   ├── core/         # configuración
│   │   ├── db/           # conexión y Base de SQLAlchemy
│   │   └── models/       # modelos de la base de datos
│   ├── alembic/      # migraciones
│   └── tests/
├── frontend/         # React + Vite
│   └── src/
│       ├── components/
│       ├── features/
│       ├── lib/
│       └── pages/
├── docs/PLAN.md      # plan por fases
├── CLAUDE.md         # contexto para Claude Code
└── docker-compose.yml
```
