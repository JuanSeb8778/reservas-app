import { Button } from './Button'
import { AlertIcon } from './icons'

// Error al cargar datos de una zona de la página, con un botón para volver a intentarlo.
// Va dentro de la misma hoja que el contenido, así el resto de la página sigue usable.
export function QueryError({
  title,
  message,
  onRetry,
  retrying,
}: {
  title: string // "No pudimos cargar los servicios."
  message: string // el mensaje de apiFetch (sin conexión, error del servidor…)
  onRetry: () => void
  retrying: boolean
}) {
  return (
    <div className="grid justify-items-start gap-3">
      <p
        role="alert"
        className="flex w-full items-start gap-2.5 rounded-control border-l-4 border-danger bg-danger-soft px-3.5 py-3 text-sm text-ink"
      >
        <AlertIcon className="mt-0.5 size-4 shrink-0 text-danger" />
        <span>
          <span className="font-semibold">{title}</span> {message}
        </span>
      </p>
      <Button variant="secondary" pending={retrying} pendingLabel="Reintentando…" onClick={onRetry}>
        Reintentar
      </Button>
    </div>
  )
}
