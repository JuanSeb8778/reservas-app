import { Skeleton } from './Skeleton'

// waiting: cargando pero todavía no toca mostrar el skeleton (evita parpadeos).
type Status = 'ok' | 'error' | 'loading' | 'waiting'

const styles = {
  ok: { dot: 'bg-ok', text: 'Funcionando' },
  error: { dot: 'bg-danger', text: 'Sin conexión' },
} as const

export function StatusRow({ label, status }: { label: string; status: Status }) {
  return (
    <li className="flex min-h-14 items-center justify-between gap-4 py-3">
      <span className="font-medium">{label}</span>
      {status === 'loading' && <Skeleton className="h-4 w-24" />}
      {status === 'waiting' && <span className="h-4 w-24" />}
      {(status === 'ok' || status === 'error') && (
        <span className="flex items-center gap-2 text-sm text-muted">
          <span className={`size-2.5 rounded-full ${styles[status].dot}`} aria-hidden="true" />
          {styles[status].text}
        </span>
      )}
    </li>
  )
}
