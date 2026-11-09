// Iconos SVG en línea (trazo de 2 px, estilo Lucide) para no añadir una dependencia.
// Son decorativos (aria-hidden): el texto que los acompaña es el que da el significado.

type IconProps = { className?: string }

const svgProps = {
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  'aria-hidden': true,
  focusable: 'false',
} as const

export function AlertIcon({ className = 'size-4' }: IconProps) {
  return (
    <svg {...svgProps} className={className}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7.5v5" />
      <path d="M12 16.5h.01" />
    </svg>
  )
}

export function InfoIcon({ className = 'size-4' }: IconProps) {
  return (
    <svg {...svgProps} className={className}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5" />
      <path d="M12 7.5h.01" />
    </svg>
  )
}

export function EyeIcon({ className = 'size-5' }: IconProps) {
  return (
    <svg {...svgProps} className={className}>
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

export function EyeOffIcon({ className = 'size-5' }: IconProps) {
  return (
    <svg {...svgProps} className={className}>
      <path d="M10.6 5.1A10.9 10.9 0 0 1 12 5c6.5 0 10 7 10 7a17.6 17.6 0 0 1-2.1 3.1" />
      <path d="M6.6 6.6C3.8 8.4 2 12 2 12s3.5 7 10 7a10 10 0 0 0 5.4-1.6" />
      <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
      <path d="m2 2 20 20" />
    </svg>
  )
}

export function CheckIcon({ className = 'size-4' }: IconProps) {
  return (
    <svg {...svgProps} className={className}>
      <path d="m5 12.5 4.5 4.5L19 7.5" />
    </svg>
  )
}

export function CircleIcon({ className = 'size-4' }: IconProps) {
  return (
    <svg {...svgProps} className={className}>
      <circle cx="12" cy="12" r="7" />
    </svg>
  )
}

export function ClockIcon({ className = 'size-4' }: IconProps) {
  return (
    <svg {...svgProps} className={className}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </svg>
  )
}

// Marca: una hoja de agenda con la hora confirmada.
export function BrandIcon({ className = 'size-6' }: IconProps) {
  return (
    <svg {...svgProps} className={className}>
      <rect x="3" y="4.5" width="18" height="16" rx="2.5" />
      <path d="M8 2.5v4M16 2.5v4M3 10h18" />
      <path d="m9 15 2 2 4-4" />
    </svg>
  )
}
