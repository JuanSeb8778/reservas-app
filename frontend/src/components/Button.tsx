import type { ButtonHTMLAttributes, MouseEvent } from 'react'

import { buttonClasses, type ButtonVariant } from './buttonStyles'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant
  pending?: boolean
  pendingLabel?: string
}

// Mientras `pending`, el botón no usa `disabled`: con disabled el foco se pierde y los
// lectores de pantalla dejan de encontrarlo. Se marca aria-disabled y se ignoran los clics
// (también el envío con Enter, que el navegador convierte en un clic en el botón).
export function Button({
  variant = 'primary',
  pending = false,
  pendingLabel,
  className = '',
  type = 'button',
  onClick,
  children,
  ...props
}: ButtonProps) {
  function handleClick(event: MouseEvent<HTMLButtonElement>) {
    if (pending) {
      event.preventDefault()
      return
    }
    onClick?.(event)
  }

  return (
    <button
      {...props}
      type={type}
      aria-disabled={pending || undefined}
      onClick={handleClick}
      className={buttonClasses(variant, className)}
    >
      {/* Las dos etiquetas ocupan la misma celda: el botón no cambia de ancho al cambiar el texto. */}
      <span className="grid">
        <span className={`col-start-1 row-start-1 ${pending && pendingLabel ? 'invisible' : ''}`}>
          {children}
        </span>
        {pendingLabel && (
          <span className={`col-start-1 row-start-1 ${pending ? '' : 'invisible'}`}>
            {pendingLabel}
          </span>
        )}
      </span>
      {pending && (
        <span aria-hidden="true" className="absolute inset-x-0 bottom-0 h-0.5 overflow-hidden">
          <span className="block h-full w-full bg-linear-to-r from-transparent via-white/90 to-transparent motion-safe:animate-shimmer" />
        </span>
      )}
    </button>
  )
}
