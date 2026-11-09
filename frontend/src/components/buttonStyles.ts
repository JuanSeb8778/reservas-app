// Clases de botón compartidas por <Button> y por enlaces que se ven como botones (<Link>).
export type ButtonVariant = 'primary' | 'secondary' | 'ghost'

const base =
  'relative inline-flex min-h-11 cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-control px-4 text-[0.9375rem] font-semibold transition-colors duration-150 aria-disabled:cursor-progress'

const variants: Record<ButtonVariant, string> = {
  primary: 'bg-tinta text-white hover:bg-tinta-hover',
  secondary: 'border border-field bg-surface text-ink hover:bg-paper',
  ghost: 'text-ink hover:bg-ink/5',
}

export function buttonClasses(variant: ButtonVariant = 'primary', className = '') {
  return `${base} ${variants[variant]} ${className}`
}
