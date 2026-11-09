import type { ReactNode } from 'react'

import { LoadingRegion, Skeleton } from '../../components/Skeleton'
import { AgendaPreview } from './AgendaPreview'

// Estructura de /login y /registro.
// - Móvil y tablet: una columna con el formulario y una tira de tres horas como guiño visual.
// - Escritorio (≥1024 px): formulario a la izquierda y la agenda decorativa a la derecha.
export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid lg:min-h-[calc(100dvh-4rem)] lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
      <div className="flex justify-center px-4 pt-8 pb-16 sm:px-6 sm:pt-14 lg:items-center lg:justify-end lg:px-16 xl:px-24">
        <div className="w-full max-w-md lg:max-w-sm">
          <SlotStrip />
          {children}
        </div>
      </div>
      <AgendaPreview />
    </div>
  )
}

// Versión mínima de la agenda para pantallas pequeñas: ocupada, tu hora y libre.
function SlotStrip() {
  return (
    <div aria-hidden="true" className="mb-7 flex gap-2 lg:hidden">
      <span className="rounded-control border border-dashed border-taken/60 px-2.5 py-1 text-sm text-taken tabular-nums line-through">
        10:00
      </span>
      <span className="rounded-control border border-highlight-edge bg-highlight-soft px-2.5 py-1 text-sm font-bold tabular-nums">
        10:30
      </span>
      <span className="rounded-control border border-line bg-surface px-2.5 py-1 text-sm text-muted tabular-nums">
        11:00
      </span>
    </div>
  )
}

// Mientras se comprueba si ya hay sesión: la forma del formulario que va a aparecer.
export function AuthFormSkeleton({ fields }: { fields: number }) {
  return (
    <LoadingRegion label="Comprobando tu sesión…" className="grid gap-5">
      <div className="grid gap-3">
        <Skeleton className="h-9 w-4/5" />
        <Skeleton className="h-4 w-3/5" />
      </div>
      {Array.from({ length: fields }, (_, index) => (
        <div key={index} className="grid gap-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-12 w-full rounded-control" />
        </div>
      ))}
      <Skeleton className="h-11 w-full rounded-control" />
    </LoadingRegion>
  )
}
