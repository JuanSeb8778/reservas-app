# Plan del proyecto: Reservas

App fullstack para que un negocio pequeño (barbería, consultorio, cancha...) gestione citas.
Los clientes ven horarios libres y reservan; el administrador gestiona servicios, horarios y citas.

## Roles

- **client**: se registra, ve servicios, reserva, cancela o reprograma sus propias citas.
- **admin**: crea y edita servicios, define el horario del negocio, ve y gestiona todas las citas.

## Modelo de datos (Fase 1)

Supuesto inicial: el negocio atiende **una cita a la vez** (un solo profesional).
Más adelante se puede añadir una tabla `staff` para varios profesionales.

| Tabla | Campos principales |
| --- | --- |
| `users` | id, email (único), hashed_password, full_name, role (`client`/`admin`), created_at |
| `services` | id, name, description, duration_minutes, price (Numeric), is_active |
| `business_hours` | id, weekday (0=lunes … 6=domingo), opens_at, closes_at |
| `bookings` | id, client_id → users, service_id → services, starts_at, ends_at, status (`confirmed`/`cancelled`), created_at |

Reglas importantes:
- Fechas y horas se guardan como `timestamptz` en UTC. La zona horaria del negocio va en la
  configuración (`BUSINESS_TIMEZONE`) y se usa para calcular los horarios disponibles.
- **No puede haber dos citas confirmadas que se solapen.** Se garantiza en la base de datos con
  una restricción de exclusión de PostgreSQL (extensión `btree_gist`):
  `EXCLUDE USING gist (tstzrange(starts_at, ends_at) WITH &&) WHERE (status = 'confirmed')`.
  La API además valida antes de insertar para dar un mensaje de error claro (409 Conflict).

## Autenticación

Implementada a mano para aprender cómo funciona:
- Hash de contraseñas con **Argon2** (`pwdlib[argon2]`). Nunca se guarda la contraseña en texto plano.
- **Access token** JWT (`PyJWT`), dura 15 minutos, se devuelve en el JSON del login y el frontend
  lo guarda **solo en memoria** (no en localStorage). Se envía en `Authorization: Bearer <token>`.
- **Refresh token** JWT, dura 7 días, va en una cookie `httpOnly`, `SameSite=Lax`, `path=/api/auth`.
  Cuando el access token expira, el frontend llama a `/api/auth/refresh` y obtiene uno nuevo.
- Endpoints: `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/refresh`,
  `POST /api/auth/logout`, `GET /api/auth/me`.
- Dependencias de FastAPI: `get_current_user` y `require_admin`.

## Fases

### Fase 0 – Preparación ✅
- [x] Monorepo con `backend/` y `frontend/`
- [x] Docker Compose con PostgreSQL, API y frontend
- [x] FastAPI con configuración, conexión a BD, Alembic y `GET /api/health`
- [x] React + Vite + TypeScript + Tailwind + React Router + TanStack Query consumiendo `/api/health`
- [x] Test del endpoint de salud

### Fase 1 – Versión mínima
- [x] Infraestructura de tests: base de datos `*_test` separada, recreada y migrada en cada
      ejecución; cada test en una transacción que se deshace (`tests/conftest.py`)
- [ ] Modelo `User` + migración
- [ ] Autenticación completa (registro, login, refresh, logout, me) + tests
- [ ] Páginas de registro e inicio de sesión (React Hook Form + Zod), contexto de sesión y rutas protegidas
- [ ] Modelos `Service` y `BusinessHours` + CRUD solo para admin + tests
- [ ] Página pública de servicios
- [ ] Endpoint `GET /api/availability?service_id=&date=` que devuelve los horarios libres + tests
- [ ] Modelo `Booking` con restricción de exclusión + `POST /api/bookings` + tests de solapamiento
- [ ] Flujo de reserva en el frontend (elegir servicio → día → hora → confirmar)
- [ ] Página "Mis citas" para el cliente

### Fase 2 – Funcionalidad completa
- [ ] Panel de administración con vista de calendario (día/semana)
- [ ] Cancelar y reprogramar citas (cliente y admin), con reglas (p. ej. no cancelar con menos de 2 h)
- [ ] Bloqueos de horario (vacaciones, festivos)
- [ ] Correos de confirmación y cancelación (Resend o similar), enviados en segundo plano
- [ ] Script de datos de ejemplo (`seed`) con un admin y servicios de prueba

### Fase 3 – Calidad y despliegue
- [ ] Cobertura de tests razonable en el backend; tests de componentes clave en el frontend (Vitest)
- [ ] GitHub Actions: lint + tests en cada push y pull request
- [ ] Despliegue: backend + Postgres en Render o Railway, frontend en Vercel
- [ ] README final con capturas, enlace a la demo, diagrama de arquitectura y decisiones técnicas

### Fase 4 – Extras para destacar
- [ ] Recordatorios automáticos 24 h antes de la cita (tarea programada)
- [ ] Iniciar sesión con Google (OAuth)
- [ ] Panel de estadísticas (reservas por semana, servicios más pedidos, horas pico)
- [ ] Pagos en modo de prueba (Stripe o Mercado Pago)
- [ ] Varios profesionales (tabla `staff`)
