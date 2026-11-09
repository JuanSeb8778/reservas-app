// Panel decorativo de las páginas de acceso (solo en pantallas grandes): una página de la
// agenda de un negocio con horas ocupadas, libres y "tu cita" marcada con resaltador.
// Muestra lo que hace la app con contenido realista en vez de una ilustración genérica.
// Es aria-hidden e inert: no es interactivo y los lectores de pantalla lo saltan.

type Row =
  | { time: string; state: 'free' }
  | { time: string; state: 'taken'; service: string; client: string }
  | { time: string; state: 'mine'; service: string }

const rows: Row[] = [
  { time: '09:00', state: 'taken', service: 'Corte clásico', client: 'Luis R.' },
  { time: '09:30', state: 'free' },
  { time: '10:00', state: 'taken', service: 'Corte y barba', client: 'Andrés M.' },
  { time: '10:30', state: 'mine', service: 'Arreglo de barba' },
  { time: '11:00', state: 'free' },
  { time: '11:30', state: 'taken', service: 'Corte infantil', client: 'Tomás G.' },
  { time: '12:00', state: 'free' },
]

function Slot({ row }: { row: Row }) {
  if (row.state === 'free') {
    return <span className="flex h-11 items-center px-3 text-sm text-muted">Libre</span>
  }
  if (row.state === 'taken') {
    return (
      <span className="flex h-11 items-center truncate rounded-control border border-dashed border-taken/60 px-3 text-sm text-taken line-through decoration-taken/70">
        {row.service} · {row.client}
      </span>
    )
  }
  return (
    <span className="flex h-11 items-center justify-between gap-3 rounded-control border border-highlight-edge bg-highlight-soft px-3 text-sm font-semibold">
      {row.service}
      <span className="text-xs font-bold uppercase tracking-[0.08em]">Tu cita</span>
    </span>
  )
}

export function AgendaPreview() {
  return (
    <aside
      aria-hidden="true"
      inert
      className="hidden border-l border-line bg-surface lg:flex lg:items-center lg:px-12 xl:px-20"
    >
      <div className="w-full max-w-md">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">
          Barbería del barrio · Agenda
        </p>
        <p className="mt-2 font-display text-3xl font-bold tracking-tight">Jueves 12 de noviembre</p>

        <ol className="mt-8 border-b border-line">
          {rows.map((row) => (
            <li
              key={row.time}
              className="grid grid-cols-[4rem_minmax(0,1fr)] items-center gap-3 border-t border-line py-2"
            >
              <span
                className={`text-sm tabular-nums ${row.state === 'mine' ? 'font-bold' : 'text-muted'}`}
              >
                {row.state === 'mine' ? <span className="marker">{row.time}</span> : row.time}
              </span>
              <Slot row={row} />
            </li>
          ))}
        </ol>

        <p className="mt-6 max-w-sm text-sm text-muted">
          Tu hora queda apartada al instante, sin llamadas ni mensajes de ida y vuelta.
        </p>
      </div>
    </aside>
  )
}
