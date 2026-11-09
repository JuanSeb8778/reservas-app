import { useEffect, useRef, type ReactNode, type RefObject } from 'react'
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
  useFocusAfterRecovery(services.isError, servicesHeading)
  useFocusAfterRecovery(hours.isError, hoursHeading)

  return (
    <Page>
      <div className="mb-8 lg:mb-10">
        <h1 tabIndex={-1} className="text-[1.875rem] leading-[1.1] font-bold sm:text-4xl">
          Nuestros <span className="marker">servicios</span>
        </h1>
        <p className="mt-2 max-w-prose text-muted">Precios, duración y horario de atención.</p>
      </div>

      {notice && <Notice className="mb-8">{notice}</Notice>}

      {/* Resumen de hoy (solo móvil): en escritorio el horario completo ya está a la vista. */}
      {/* Sin horario publicado, o si algo falló, no se muestra: el panel del horario ya lo dice. */}
      {!hours.isError && !settings.isError && (hours.isPending || hours.data.ranges.length > 0) && (
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

      <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_19rem] lg:gap-12 xl:gap-16">
        <section
          aria-labelledby="services-heading"
          className="self-start overflow-hidden rounded-panel border border-line bg-surface"
        >
          <h2
            id="services-heading"
            ref={servicesHeading}
            tabIndex={-1}
            className="px-5 pt-5 font-sans text-xs font-semibold tracking-[0.14em] text-muted uppercase sm:px-8 sm:pt-6"
          >
            Servicios
          </h2>
          <div className="pb-2">
            {services.isError ? (
              <div className="px-5 py-5 sm:px-8">
                <QueryError
                  title="No pudimos cargar los servicios."
                  message={services.error.message}
                  retrying={services.isFetching}
                  onRetry={() => {
                    void services.refetch()
                    if (settings.isError) void settings.refetch()
                  }}
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

        <aside aria-labelledby="horario" className="lg:sticky lg:top-8 lg:self-start">
          <h2
            id="horario"
            ref={hoursHeading}
            tabIndex={-1}
            className="scroll-mt-6 text-xl font-bold sm:text-2xl"
          >
            Horario de atención
          </h2>
          {showTimezoneNote && timezone && (
            <p className="mt-2 flex items-start gap-1.5 text-sm text-muted">
              <InfoIcon className="mt-0.5 size-4 shrink-0 text-tinta" />
              <span>Las horas están en la zona del negocio ({timezoneLabel(timezone)}).</span>
            </p>
          )}
          <div className="mt-4 rounded-panel border border-line bg-surface px-5 py-2">
            {hours.isError ? (
              <div className="py-3">
                <QueryError
                  title="No pudimos cargar el horario."
                  message={hours.error.message}
                  retrying={hours.isFetching}
                  onRetry={() => void hours.refetch()}
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
        </aside>
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

// Si el usuario pulsó "Reintentar" y la carga salió bien, el botón desaparece y el foco se
// quedaría en el vacío (body). Se lleva al título de la zona para que el teclado y el lector
// de pantalla sigan donde estaban.
function useFocusAfterRecovery(isError: boolean, heading: RefObject<HTMLHeadingElement | null>) {
  const wasError = useRef(false)
  useEffect(() => {
    if (wasError.current && !isError && document.activeElement === document.body) {
      heading.current?.focus()
    }
    wasError.current = isError
  }, [isError, heading])
}
