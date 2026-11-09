import type { ReactNode } from 'react'

import { InfoIcon } from './icons'

// Aviso informativo que llega al navegar (p. ej. "Cerraste sesión").
export function Notice({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <p
      role="status"
      className={`flex items-start gap-2.5 rounded-control border-l-4 border-tinta bg-surface px-3.5 py-3 text-sm text-ink ${className}`}
    >
      <InfoIcon className="mt-0.5 size-4 shrink-0 text-tinta" />
      <span>{children}</span>
    </p>
  )
}
