import type { ReactNode } from 'react'

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
