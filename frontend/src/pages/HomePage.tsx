import { StatusRow } from '../components/StatusRow'
import { useHealth } from '../features/health/useHealth'

export function HomePage() {
  const { data, isPending, isError } = useHealth()

  const apiStatus = isPending ? 'loading' : isError ? 'error' : 'ok'
  const dbStatus = isPending ? 'loading' : isError ? 'error' : data.database

  return (
    <section className="space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Reservas</h1>
        <p className="text-stone-600">
          Agenda citas en un negocio pequeño. Este panel confirma que el frontend, la API y la base
          de datos están conectados.
        </p>
      </div>

      <div className="rounded-xl border border-stone-200 bg-white px-5 shadow-sm">
        <ul className="divide-y divide-stone-100">
          <StatusRow label="Frontend (React)" status="ok" />
          <StatusRow label="API (FastAPI)" status={apiStatus} />
          <StatusRow label="Base de datos (PostgreSQL)" status={dbStatus} />
        </ul>
      </div>

      <p className="text-sm text-stone-500">
        Documentación de la API:{' '}
        <a className="underline hover:text-stone-800" href="http://localhost:8000/docs">
          localhost:8000/docs
        </a>
      </p>
    </section>
  )
}
