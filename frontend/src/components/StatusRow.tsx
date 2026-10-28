type Status = 'ok' | 'error' | 'loading'

const styles: Record<Status, { dot: string; text: string }> = {
  ok: { dot: 'bg-emerald-500', text: 'Funcionando' },
  error: { dot: 'bg-rose-500', text: 'Sin conexión' },
  loading: { dot: 'bg-stone-300 animate-pulse', text: 'Comprobando…' },
}

export function StatusRow({ label, status }: { label: string; status: Status }) {
  const { dot, text } = styles[status]

  return (
    <li className="flex items-center justify-between py-3">
      <span className="font-medium">{label}</span>
      <span className="flex items-center gap-2 text-sm text-stone-600">
        <span className={`size-2.5 rounded-full ${dot}`} aria-hidden />
        {text}
      </span>
    </li>
  )
}
