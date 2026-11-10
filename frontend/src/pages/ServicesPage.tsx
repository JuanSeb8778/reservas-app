import { useRef, useState, type ReactNode, type RefObject } from 'react'
import { useLocation } from 'react-router'

import { Notice } from '../components/Notice'
import { Page } from '../components/Page'
import { QueryError } from '../components/QueryError'
import { LoadingRegion, Skeleton } from '../components/Skeleton'
import { InfoIcon } from '../components/icons'
import { TodaySummary, WeekHours, WeekHoursSkeleton } from '../features/business/BusinessHours'
import { deviceClockDiffers, timezoneLabel, weekdayInTimezone } from '../features/business/format'
import { useBusinessHours, useBusinessSettings } from '../features/business/useBusiness'
import { ServiceList, ServiceListEmpty, ServiceListSkeleton } from '../features/services/ServiceList'
import { useServices } from '../features/services/useServices'
import { getNotice } from '../lib/navigationState'
import { useDelayedFlag } from '../lib/useDelayedFlag'
import { useDocumentTitle } from '../lib/useDocumentTitle'

// Título de cada hoja: una etiqueta pequeña dentro del panel, como el encabezado de una agenda.
const SHEET_HEADING =
  'scroll-mt-6 font-sans text-xs font-semibold tracking-[0.14em] text-muted uppercase'

// Portada pública: la carta de servicios y el horario del negocio. Se pide todo en paralelo;
// cada zona tiene su propio skeleton y su propio error, así un fallo en el horario no impide
// ver los servicios.
export function ServicesPage() {
  useDocumentTitle('Servicios')
  const notice = getNotice(useLocation().state)
  const services = useServices()
  const settings = useBusinessSettings()
  const hours = useBusinessHours()

  // La moneda y la zona horaria vienen de la configuración. Mientras llega, las zonas que la
  // usan siguen "cargando" para no mostrar un precio sin símbolo y cambiarlo un instante después.
  // Si la configuración falla, se muestran igual: precios sin símbolo y sin resaltar "hoy".
  const settingsPending = settings.isPending
  const timezone = settings.data?.timezone
  const today = timezone ? weekdayInTimezone(timezone) : null
  const showTimezoneNote = timezone ? deviceClockDiffers(timezone) : false

  const servicesHeading = useRef<HTMLHeadingElement>(null)
  const hoursHeading = useRef<HTMLHeadingElement>(null)
  const servicesRetry = useZoneError(services, servicesHeading, () =>
    Promise.all([services.refetch(), settings.isError ? settings.refetch() : null]).then(
      ([result]) => result,
    ),
  )
  const hoursRetry = useZoneError(hours, hoursHeading, () => hours.refetch())
  const servicesError = servicesRetry.error
  const hoursError = hoursRetry.error

  return (
    <Page className="max-w-6xl">
      <div className="mb-8 lg:mb-10">
        <h1 tabIndex={-1} className="text-[1.875rem] leading-[1.1] font-bold sm:text-4xl">
          Nuestros <span className="marker">servicios</span>
        </h1>
        <p className="mt-2 max-w-prose text-muted">Precios, duración y horario de atención.</p>
      </div>

      {notice && <Notice className="mb-8">{notice}</Notice>}

      {/* Resumen de hoy (solo móvil): en escritorio el horario completo ya está a la vista.
          Sin horario publicado, o si algo falló, no se muestra: el panel del horario ya lo dice. */}
      {!hoursError && !settings.isError && (hours.isPending || (hours.data?.ranges.length ?? 0) > 0) && (
        <div className="mb-8 flex min-h-11 flex-wrap items-center gap-x-3 gap-y-1 lg:hidden">
          <Loadable
            pending={hours.isPending || settingsPending}
            label="Cargando el horario de hoy…"
            skeleton={<Skeleton className="h-5 w-64 max-w-full" />}
          >
            {hours.data && today !== null && (
              <>
                <TodaySummary ranges={hours.data.ranges} today={today} />
                <a
                  href="#horario"
                  className="inline-flex min-h-11 items-center text-[0.9375rem] font-medium text-tinta underline decoration-2 underline-offset-4 hover:text-tinta-hover"
                >
                  Ver horario
                </a>
              </>
            )}
          </Loadable>
        </div>
      )}

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-12 xl:gap-16">
        <section
          aria-labelledby="services-heading"
          className="self-start overflow-hidden rounded-panel border border-line bg-surface"
        >
          <h2
            id="services-heading"
            ref={servicesHeading}
            tabIndex={-1}
            className={`${SHEET_HEADING} px-5 pt-5 sm:px-8 sm:pt-6`}
          >
            Servicios
          </h2>
          <div className="pb-2">
            {servicesError ? (
              <div className="px-5 py-5 sm:px-8">
                <QueryError
                  title="No pudimos cargar los servicios."
                  message={servicesError.message}
                  retrying={servicesRetry.retrying}
                  onRetry={servicesRetry.retry}
                />
              </div>
            ) : (
              <Loadable
                pending={services.isPending || settingsPending}
                label="Cargando servicios…"
                skeleton={<ServiceListSkeleton />}
              >
                {services.data &&
                  (services.data.length === 0 ? (
                    <div className="py-4">
                      <ServiceListEmpty />
                    </div>
                  ) : (
                    <ServiceList services={services.data} currency={settings.data?.currency} />
                  ))}
              </Loadable>
            )}
          </div>
        </section>

        <section
          aria-labelledby="horario"
          className="self-start rounded-panel border border-line bg-surface px-5 pt-5 pb-2 sm:pt-6 lg:sticky lg:top-8"
        >
          <h2 id="horario" ref={hoursHeading} tabIndex={-1} className={SHEET_HEADING}>
            Horario de atención
          </h2>
          {showTimezoneNote && timezone && (
            <p className="mt-2 flex items-start gap-1.5 text-sm text-muted">
              <InfoIcon className="mt-0.5 size-4 shrink-0 text-tinta" />
              <span>Las horas están en la zona del negocio ({timezoneLabel(timezone)}).</span>
            </p>
          )}
          <div className="mt-2">
            {hoursError ? (
              <div className="py-3">
                <QueryError
                  title="No pudimos cargar el horario."
                  message={hoursError.message}
                  retrying={hoursRetry.retrying}
                  onRetry={hoursRetry.retry}
                />
              </div>
            ) : (
              <Loadable
                pending={hours.isPending || settingsPending}
                label="Cargando horario…"
                skeleton={<WeekHoursSkeleton />}
              >
                {hours.data && <WeekHours ranges={hours.data.ranges} today={today} />}
              </Loadable>
            )}
          </div>
        </section>
      </div>
    </Page>
  )
}

// Zona que carga: durante los primeros 200 ms no se ve nada (si la API responde rápido, no
// hay parpadeo), pero el skeleton ya ocupa su sitio de forma invisible para que la página no
// salte cuando aparezca.
function Loadable({
  pending,
  label,
  skeleton,
  children,
}: {
  pending: boolean
  label: string
  skeleton: ReactNode
  children: ReactNode
}) {
  const showSkeleton = useDelayedFlag(pending)
  if (showSkeleton) return <LoadingRegion label={label}>{skeleton}</LoadingRegion>
  if (pending) return <div className="invisible">{skeleton}</div>
  return children
}

type ZoneQuery = { data: unknown; error: Error | null; isFetching: boolean }

// Error de una zona y su botón "Reintentar".
// - Si ya hay datos y falla una recarga en segundo plano, se siguen mostrando los datos.
// - Al volver a pedir una consulta que nunca tuvo datos (con el botón o sola, al volver a la
//   pestaña), TanStack Query la devuelve a "pending" y borra el error: el mensaje y el botón
//   desaparecerían a mitad de la carga y el foco caería en el vacío. Por eso se recuerda el
//   último error mientras dura la carga: el botón sigue ahí ("Reintentando…", con el foco)
//   hasta saber el resultado.
// - Si el reintento con el botón sale bien, el botón desaparece y el foco pasa al título de la
//   zona; si falla, se queda en el botón.
function useZoneError(
  query: ZoneQuery,
  heading: RefObject<HTMLHeadingElement | null>,
  refetch: () => Promise<{ isSuccess: boolean }>,
) {
  const current = query.data === undefined ? query.error : null
  const [lastError, setLastError] = useState<Error | null>(null)
  // Ajuste de estado durante el render (patrón recomendado por React en vez de un efecto):
  // se guarda cada error nuevo y se olvida cuando la carga termina sin error.
  if (current && current !== lastError) setLastError(current)
  if (!current && !query.isFetching && lastError) setLastError(null)

  const error = current ?? (query.isFetching ? lastError : null)

  async function retry() {
    const result = await refetch()
    if (result.isSuccess) heading.current?.focus()
  }

  return { error, retrying: error !== null && query.isFetching, retry }
}
