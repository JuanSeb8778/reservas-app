import { Page } from '../components/Page'
import { useSession } from '../features/auth/useSession'
import { useDocumentTitle } from '../lib/useDocumentTitle'

// Horas de ejemplo para dibujar la hoja vacía de la agenda (decorativas).
const EMPTY_ROWS = ['09:00', '09:30', '10:00', '10:30']

// Página protegida. Por ahora solo muestra el estado vacío; las citas llegan con el
// modelo Booking (ver docs/PLAN.md).
export function MyBookingsPage() {
  useDocumentTitle('Mis citas')
  const { user } = useSession()
  const firstName = user?.full_name.split(/\s+/)[0]

  return (
    <Page className="max-w-3xl">
      <h1 tabIndex={-1} className="text-4xl font-bold">
        Mis citas
      </h1>
      <p className="mt-2 text-muted">
        {firstName ? `Hola, ${firstName}. ` : ''}Aquí verás las citas que reserves.
      </p>

      <section
        aria-labelledby="empty-bookings"
        className="mt-8 overflow-hidden rounded-panel border border-line bg-surface"
      >
        <div className="px-5 pt-6 sm:px-8 sm:pt-8">
          <h2 id="empty-bookings" className="text-2xl font-bold">
            Todavía no tienes <span className="marker">ninguna</span> cita
          </h2>
          <p className="mt-2 max-w-prose text-muted">
            Pronto podrás elegir un servicio, ver las horas libres y apartar la tuya desde aquí.
          </p>
        </div>
        {/* Hoja de agenda en blanco: refuerza que el espacio está listo para tus citas. */}
        <ol aria-hidden="true" className="mt-6">
          {EMPTY_ROWS.map((time) => (
            <li
              key={time}
              className="grid h-12 grid-cols-[4.5rem_minmax(0,1fr)] items-center border-t border-line px-5 sm:px-8"
            >
              <span className="text-sm text-muted tabular-nums">{time}</span>
              <span className="border-t border-dashed border-line" />
            </li>
          ))}
        </ol>
      </section>
    </Page>
  )
}
