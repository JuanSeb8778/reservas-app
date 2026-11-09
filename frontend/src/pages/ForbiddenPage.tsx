import { Link } from 'react-router'

import { buttonClasses } from '../components/buttonStyles'
import { Page } from '../components/Page'
import { useDocumentTitle } from '../lib/useDocumentTitle'

export function ForbiddenPage() {
  useDocumentTitle('Acceso denegado')

  return (
    <Page className="max-w-2xl">
      <p className="text-sm font-semibold uppercase tracking-[0.14em] text-muted">Error 403</p>
      <h1 tabIndex={-1} className="mt-2 text-4xl font-bold">
        No tienes permiso para ver esta página
      </h1>
      <p className="mt-3 max-w-prose text-muted">
        Esta sección es solo para quien administra el negocio. Si crees que es un error, cierra
        sesión y entra con la cuenta de administración.
      </p>

      {/* Una hora "ocupada" de la agenda como guiño visual: el espacio está reservado. */}
      <div aria-hidden="true" className="mt-8 grid max-w-md grid-cols-[4.5rem_minmax(0,1fr)] items-center gap-3">
        <span className="text-sm text-muted tabular-nums">—</span>
        <span className="flex h-11 items-center rounded-control border border-dashed border-taken/60 px-3 text-sm text-taken line-through">
          Reservado para administración
        </span>
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <Link to="/mis-citas" className={buttonClasses('primary')}>
          Ir a Mis citas
        </Link>
        <Link to="/" className={buttonClasses('ghost')}>
          Volver al inicio
        </Link>
      </div>
    </Page>
  )
}
