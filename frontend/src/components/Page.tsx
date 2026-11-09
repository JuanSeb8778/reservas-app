import type { ReactNode } from 'react'

// Contenedor estándar de una página: ancho máximo y márgenes laterales (16 px en móvil).
export function Page({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`mx-auto w-full max-w-5xl px-4 py-10 sm:px-6 sm:py-14 ${className}`}>
      {children}
    </div>
  )
}
