import { useLocation } from 'react-router'

import { Notice } from '../components/Notice'
import { Page } from '../components/Page'
import { StatusRow } from '../components/StatusRow'
import { useHealth } from '../features/health/useHealth'
import { getNotice } from '../lib/navigationState'
import { useDelayedFlag } from '../lib/useDelayedFlag'
import { useDocumentTitle } from '../lib/useDocumentTitle'

export function HomePage() {
  useDocumentTitle('Inicio')
  const notice = getNotice(useLocation().state)
  const { data, isPending, isError } = useHealth()
  const showSkeleton = useDelayedFlag(isPending)

  const pending = showSkeleton ? 'loading' : 'waiting'
  const apiStatus = isPending ? pending : isError ? 'error' : 'ok'
  const dbStatus = isPending ? pending : isError ? 'error' : data.database

  return (
    <Page className="space-y-8">
      <div className="space-y-2">
        <h1 tabIndex={-1} className="text-4xl font-bold">
          Reservas
        </h1>
        <p className="max-w-prose text-muted">
          Agenda citas en un negocio pequeño. Este panel confirma que el frontend, la API y la base
          de datos están conectados.
        </p>
      </div>

      {notice && <Notice>{notice}</Notice>}

      <div
        className="rounded-panel border border-line bg-surface px-5"
        aria-busy={isPending || undefined}
      >
        {showSkeleton && (
          <span role="status" className="sr-only">
            Comprobando la conexión…
          </span>
        )}
        <ul className="divide-y divide-line">
          <StatusRow label="Frontend (React)" status="ok" />
          <StatusRow label="API (FastAPI)" status={apiStatus} />
          <StatusRow label="Base de datos (PostgreSQL)" status={dbStatus} />
        </ul>
      </div>

      <p className="text-sm text-muted">
        Documentación de la API:{' '}
        <a
          className="font-medium text-tinta underline underline-offset-4 hover:text-tinta-hover"
          href="http://localhost:8000/docs"
        >
          localhost:8000/docs
        </a>
      </p>
    </Page>
  )
}
