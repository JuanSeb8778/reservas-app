import { Page } from '../components/Page'
import { useDocumentTitle } from '../lib/useDocumentTitle'

// Marcador de la futura zona de administración (Fase 2). Existe ya para probar RequireAdmin.
export function AdminPage() {
  useDocumentTitle('Panel del negocio')

  return (
    <Page className="max-w-3xl">
      <h1 tabIndex={-1} className="text-4xl font-bold">
        Panel del negocio
      </h1>
      <p className="mt-2 max-w-prose text-muted">
        Muy pronto podrás gestionar aquí los servicios, el horario y todas las citas del negocio.
      </p>
    </Page>
  )
}
