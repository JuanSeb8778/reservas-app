import { Link } from 'react-router'

import { buttonClasses } from '../components/buttonStyles'
import { Page } from '../components/Page'
import { useDocumentTitle } from '../lib/useDocumentTitle'

export function NotFoundPage() {
  useDocumentTitle('Página no encontrada')

  return (
    <Page className="max-w-2xl">
      <p className="text-sm font-semibold uppercase tracking-[0.14em] text-muted">Error 404</p>
      <h1 tabIndex={-1} className="mt-2 text-4xl font-bold">
        Esta página no está en la agenda
      </h1>
      <p className="mt-3 max-w-prose text-muted">
        Puede que el enlace esté mal escrito o que la página ya no exista.
      </p>
      <Link to="/" className={buttonClasses('primary', 'mt-8')}>
        Volver al inicio
      </Link>
    </Page>
  )
}
