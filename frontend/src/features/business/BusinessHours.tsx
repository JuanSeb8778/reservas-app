import { Skeleton } from '../../components/Skeleton'
import { capitalize, groupHoursByDay, type DayHours } from './format'
import type { BusinessHoursRange } from './types'

// "09:00 – 13:00". El guion es solo visual: el lector de pantalla oye "09:00 a 13:00".
function TimeRange({ range }: { range: BusinessHoursRange }) {
  return (
    <span className="whitespace-nowrap">
      <time>{range.opens_at}</time>
      <span aria-hidden="true"> – </span>
      <span className="sr-only"> a </span>
      <time>{range.closes_at}</time>
    </span>
  )
}

const ROW =
  'grid grid-cols-[minmax(0,1fr)_auto] items-start gap-x-4 border-t border-line py-2.5 first:border-t-0'

// Semana completa, de lunes a domingo. `today` (0 = lunes) se calcula en la zona del negocio;
// null si no se sabe (p. ej. no se pudo cargar la configuración) y entonces no se resalta.
export function WeekHours({ ranges, today }: { ranges: BusinessHoursRange[]; today: number | null }) {
  if (ranges.length === 0) {
    return <p className="py-3 text-muted">El negocio aún no ha publicado su horario.</p>
  }

  return (
    <dl className="text-[0.9375rem]">
      {groupHoursByDay(ranges).map((day) => (
        <DayRow key={day.weekday} day={day} isToday={day.weekday === today} />
      ))}
    </dl>
  )
}

function DayRow({ day, isToday }: { day: DayHours; isToday: boolean }) {
  const closed = day.ranges.length === 0
  // Hoy: el mismo tratamiento de resaltador que "Tu cita" en la agenda. Además del color,
  // lleva la etiqueta "Hoy" en texto (nunca solo el color).
  const todayStyles = isToday
    ? '-mx-3 rounded-control border border-highlight-edge bg-highlight-soft px-3'
    : ''

  return (
    <div className={`${ROW} ${todayStyles}`} aria-current={isToday ? 'date' : undefined}>
      <dt className={`font-medium ${closed ? 'text-muted' : ''}`}>
        {capitalize(day.name)}
        {isToday && (
          <span className="ml-2 text-xs font-bold tracking-[0.08em] uppercase">Hoy</span>
        )}
      </dt>
      <dd className="grid justify-items-end gap-0.5 tabular-nums">
        {closed ? (
          <span className="text-muted">Cerrado</span>
        ) : (
          day.ranges.map((range) => <TimeRange key={range.opens_at} range={range} />)
        )}
      </dd>
    </div>
  )
}

export function WeekHoursSkeleton() {
  return (
    <div>
      {[0, 1, 2, 3, 4, 5, 6].map((row) => (
        <div key={row} className={`${ROW} py-3.5`}>
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-24" />
        </div>
      ))}
    </div>
  )
}

// Resumen para móvil, encima de la carta: "Hoy, martes: 09:00 – 13:00 y 14:00 – 19:00".
export function TodaySummary({ ranges, today }: { ranges: BusinessHoursRange[]; today: number }) {
  const day = groupHoursByDay(ranges)[today]

  return (
    <p className="text-[0.9375rem]">
      <span className="font-semibold">Hoy, {day.name}:</span>{' '}
      {day.ranges.length === 0
        ? 'cerrado'
        : day.ranges.map((range, index) => (
            <span key={range.opens_at}>
              {index > 0 && ' y '}
              <TimeRange range={range} />
            </span>
          ))}
    </p>
  )
}
