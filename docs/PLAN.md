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
| `business_settings` | id (siempre 1), timezone (IANA, p. ej. `America/Bogota`), currency (ISO 4217, p. ej. `COP`) |
| `services` | id, name (único sin distinguir mayúsculas), description, duration_minutes (5–480, múltiplo de 5), price (Numeric), is_active, created_at |
| `business_hours` | id, weekday (0=lunes … 6=domingo), opens_at, closes_at (hora local del negocio; sin tramos solapados ni contiguos, garantizado con `EXCLUDE`) |
| `bookings` | id, client_id → users, service_id → services, starts_at, ends_at, status (`confirmed`/`cancelled`), created_at |

Reglas importantes:
- Fechas y horas se guardan como `timestamptz` en UTC. La zona horaria del negocio vive en la
  tabla `business_settings` (la elige el administrador desde la app, no es una variable de
  entorno) y se usa para calcular los horarios disponibles. Los clientes ven siempre la hora
  del negocio; si su equipo está en otra zona, la interfaz lo indica ("hora de Bogotá").
- La moneda también la elige el administrador. Cambiarla **no convierte** los precios.
- Los servicios no se borran: se archivan con `is_active = false` (las citas los referencian).
- `time` no puede representar 24:00: el cierre más tardío de un tramo es 23:59.
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

Limitaciones conocidas y pendientes (decididas al implementar la autenticación):
- Los tokens no se guardan en la base de datos: el logout solo borra la cookie y un refresh token
  robado vale hasta que caduca. Revocación real (tabla de `jti` o `token_version` en `users`)
  → Fase 4.
- Sin límite de intentos en `/login` y `/register` (rate limiting) → Fase 3.
- El registro devuelve 409 si el email existe, lo que permite saber qué emails están registrados.
  Es lo habitual en este tipo de app; se acepta.
- Sin sincronización entre pestañas: cerrar sesión en una no afecta a otra hasta que su token
  caduca (15 min). Mejora opcional: `BroadcastChannel`.
- Si el access token caducó y la renovación también falla (p. ej. se cerró sesión en otra
  pestaña), `GET /api/services` responde 401 una vez y la portada muestra un error; "Reintentar"
  ya funciona porque la sesión quedó cerrada. Mejora opcional: que `apiFetch` repita las
  peticiones públicas sin token tras una renovación fallida.
- Si el logout no llega al servidor (sin conexión), la cookie sigue viva: la interfaz avisa al
  usuario de que vuelva a cerrar sesión cuando tenga conexión.
- **Despliegue:** con frontend y API en dominios distintos (Vercel + Render), `SameSite=Lax`
  impide enviar la cookie. Habrá que servir la API bajo el mismo dominio (rewrite de `/api` en
  Vercel) o usar `SameSite=None; Secure` con protección CSRF.

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
- [x] Modelo `User` + migración
- [x] Autenticación completa (registro, login, refresh, logout, me) + tests
- [x] Sistema de diseño "Tinta y resaltador" (tokens, tipografías, skeletons) → `docs/DESIGN.md`
- [x] Páginas de registro e inicio de sesión (React Hook Form + Zod), sesión con TanStack Query
      (`['auth','me']`, sin Context propio), renovación del token al recibir 401 y rutas
      protegidas (`RequireAuth`, `RequireAdmin`)
- [x] Modelos `Service` y `BusinessHours` + CRUD solo para admin + tests (más
      `BusinessSettings` con zona horaria y moneda, y `OptionalUser` para rutas públicas que
      muestran más a un admin)
- [x] Página pública de servicios: es la portada (`/`). Carta de precios con la moneda del
      negocio y horario semanal con el día de hoy (en la zona del negocio); aviso de zona
      horaria solo si el reloj del visitante marca otra hora. Reemplaza al panel de salud
- [ ] Endpoint `GET /api/availability?service_id=&date=` que devuelve los horarios libres + tests
- [ ] Modelo `Booking` con restricción de exclusión + `POST /api/bookings` + tests de solapamiento
- [ ] Flujo de reserva en el frontend (elegir servicio → día → hora → confirmar)
- [ ] Página "Mis citas" para el cliente

### Fase 2 – Funcionalidad completa
- [ ] Panel de administración con vista de calendario (día/semana)
- [ ] Pantallas de admin para servicios, horario y configuración del negocio. Zona horaria con
      un botón "Detectar" que la sugiere con `Intl.DateTimeFormat().resolvedOptions().timeZone`
      (sin pedir la ubicación) y el admin confirma o cambia; listas de zonas y monedas con
      `Intl.supportedValuesOf`. Avisar de que cambiar la zona mueve la hora local en que se
      muestran las citas y que cambiar la moneda no convierte los precios
- [ ] Cancelar y reprogramar citas (cliente y admin), con reglas (p. ej. no cancelar con menos de 2 h)
- [ ] Bloqueos de horario (vacaciones, festivos)
- [ ] Correos de confirmación y cancelación (Resend o similar), enviados en segundo plano
- [ ] Script de datos de ejemplo (`seed`) con un admin y servicios de prueba

### Fase 3 – Calidad y despliegue
- [ ] Cobertura de tests razonable en el backend; tests de componentes clave en el frontend (Vitest).
      Empezar por la renovación del token de `src/lib/api.ts` y los esquemas de Zod (ya
      verificados a mano con scripts en la Fase 1)
- [x] GitHub Actions: lint + tests en cada push y pull request (adelantado a la Fase 1,
      `.github/workflows/ci.yml`)
- [ ] Despliegue: backend + Postgres en Render o Railway, frontend en Vercel
- [ ] README final con capturas, enlace a la demo, diagrama de arquitectura y decisiones técnicas

### Fase 4 – Extras para destacar
- [ ] Recordatorios automáticos 24 h antes de la cita (tarea programada)
- [ ] Iniciar sesión con Google (OAuth)
- [ ] Panel de estadísticas (reservas por semana, servicios más pedidos, horas pico)
- [ ] Pagos en modo de prueba (Stripe o Mercado Pago)
- [ ] Varios profesionales (tabla `staff`)
