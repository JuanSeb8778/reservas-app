import { ClockIcon } from '../../components/icons'
import { Skeleton } from '../../components/Skeleton'
import { formatDuration, formatDurationSpoken, formatPrice, formatPriceSpoken } from './format'
import type { Service } from './types'

// "La carta del negocio": cada servicio es una línea de una lista de precios impresa,
// con el nombre, unos puntos guía y el precio. No hay tarjetas: es una sola hoja con filas.
export function ServiceList({ services, currency }: { services: Service[]; currency?: string }) {
  return (
    <ul>
      {services.map((service) => (
        <ServiceItem key={service.id} service={service} currency={currency} />
      ))}
    </ul>
  )
}

const ROW = 'border-t border-line px-5 py-5 first:border-t-0 sm:px-8'

function ServiceItem({ service, currency }: { service: Service; currency?: string }) {
  return (
    <li className={ROW}>
      {/* items-end: si el nombre ocupa dos líneas, los puntos y el precio van en la última,
          como en una carta impresa. */}
      <div className="flex items-end gap-2">
        <h3 className="min-w-0 text-lg leading-snug font-bold [overflow-wrap:anywhere] sm:text-xl">
          {service.name}
        </h3>
        <span
          aria-hidden="true"
          className="mb-[0.4em] min-w-4 flex-1 border-b-2 border-dotted border-field/50"
        />
        {/* El precio visual ("$ 25.000") se oculta a los lectores de pantalla, que leen la
            versión con el nombre de la moneda ("25.000 pesos colombianos"). */}
        <span className="shrink-0 text-base font-semibold whitespace-nowrap tabular-nums sm:text-lg">
          <span aria-hidden="true">{formatPrice(service.price, currency)}</span>
          <span className="sr-only">{formatPriceSpoken(service.price, currency)}</span>
        </span>
      </div>
      {service.description && (
        // pre-line respeta los saltos de línea que escribió el administrador.
        <p className="mt-1.5 max-w-prose text-[0.9375rem] leading-relaxed whitespace-pre-line text-muted [overflow-wrap:anywhere]">
          {service.description}
        </p>
      )}
      <p className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-muted tabular-nums">
        <ClockIcon className="size-4 shrink-0" />
        <span aria-hidden="true">{formatDuration(service.duration_minutes)}</span>
        <span className="sr-only">Duración: {formatDurationSpoken(service.duration_minutes)}</span>
      </p>
    </li>
  )
}

// Anchos distintos en cada fila para que el skeleton no parezca un sello repetido.
const SKELETON_NAMES = ['w-40', 'w-52', 'w-32', 'w-44']

export function ServiceListSkeleton() {
  return (
    <div>
      {SKELETON_NAMES.map((width, index) => (
        <div key={width} className={`${ROW} ${index === 0 ? 'border-t-0' : ''}`}>
          <div className="flex items-end gap-4">
            <Skeleton className={`h-6 max-w-[60%] ${width}`} />
            <span className="flex-1" />
            <Skeleton className="h-6 w-20" />
          </div>
          {index % 2 === 0 && <Skeleton className="mt-2.5 h-4 w-full max-w-sm" />}
          <Skeleton className="mt-3.5 h-4 w-16" />
        </div>
      ))}
    </div>
  )
}

// Hoja vacía: unas líneas de carta sin rellenar, como eco de la agenda en blanco de "Mis citas".
export function ServiceListEmpty() {
  return (
    <div>
      <div className="px-5 pt-1 sm:px-8">
        <h3 className="text-xl font-bold">Aún no hay servicios</h3>
        <p className="mt-2 max-w-prose text-muted">
          El negocio todavía está preparando su carta. Vuelve pronto.
        </p>
      </div>
      <ul aria-hidden="true" className="mt-5">
        {['w-1/3', 'w-1/2', 'w-1/4'].map((width) => (
          <li key={width} className="flex h-12 items-end gap-2 border-t border-line px-5 pb-3 sm:px-8">
            <span className={`h-3 rounded-[4px] bg-line ${width}`} />
            <span className="mb-0.5 flex-1 border-b-2 border-dotted border-line" />
            <span className="h-3 w-12 rounded-[4px] bg-line" />
          </li>
        ))}
      </ul>
    </div>
  )
}
