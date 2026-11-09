import type { ReactNode } from 'react'

import { Page } from './Page'

// Bloque gris con un brillo que lo recorre. Es decorativo (aria-hidden): quien anuncia la
// carga es el LoadingRegion que lo envuelve. Con "reducir movimiento" queda estático.
export function Skeleton({ className = '' }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={`relative block overflow-hidden rounded-[4px] bg-skeleton after:absolute after:inset-0 after:-translate-x-full after:bg-linear-to-r after:from-transparent after:via-white/70 after:to-transparent after:content-[''] motion-safe:after:animate-shimmer motion-reduce:after:hidden ${className}`}
    />
  )
}

// Contenedor de una zona que está cargando: marca aria-busy y deja un único texto para
// lectores de pantalla, en vez de que cada bloque se anuncie por separado.
export function LoadingRegion({
  label,
  className = '',
  children,
}: {
  label: string
  className?: string
  children: ReactNode
}) {
  return (
    <div aria-busy="true" className={className}>
      <span role="status" className="sr-only">
        {label}
      </span>
      {children}
    </div>
  )
}

// Página protegida mientras se comprueba la sesión: título, subtítulo y una hoja de agenda.
export function PageSkeleton() {
  return (
    <Page className="max-w-3xl">
      <LoadingRegion label="Cargando…" className="grid gap-8">
        <div className="grid gap-3">
          <Skeleton className="h-10 w-56" />
          <Skeleton className="h-4 w-80 max-w-full" />
        </div>
        <div className="grid gap-4 rounded-panel border border-line bg-surface p-5 sm:p-8">
          <Skeleton className="h-7 w-3/4" />
          {[0, 1, 2, 3].map((row) => (
            <div key={row} className="grid grid-cols-[4.5rem_minmax(0,1fr)] items-center gap-3">
              <Skeleton className="h-4 w-12" />
              <Skeleton className="h-4 w-full" />
            </div>
          ))}
        </div>
      </LoadingRegion>
    </Page>
  )
}
