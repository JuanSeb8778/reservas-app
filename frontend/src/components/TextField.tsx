import { useId, type InputHTMLAttributes, type ReactNode, type Ref } from 'react'

import { AlertIcon } from './icons'

export type TextFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string
  hint?: ReactNode
  error?: ReactNode
  // Contenido dentro del campo, a la derecha (p. ej. el botón de mostrar contraseña).
  trailing?: ReactNode
  ref?: Ref<HTMLInputElement>
}

// Campo con etiqueta visible, texto de ayuda y error enlazados al input
// (aria-describedby), para que un lector de pantalla los lea al llegar al campo.
export function TextField({
  label,
  hint,
  error,
  trailing,
  id,
  className = '',
  ...inputProps
}: TextFieldProps) {
  const generatedId = useId()
  const inputId = id ?? generatedId
  const hintId = `${inputId}-hint`
  const errorId = `${inputId}-error`
  const describedBy = [hint ? hintId : null, error ? errorId : null].filter(Boolean).join(' ')

  return (
    <div className={`grid gap-1.5 ${className}`}>
      <label htmlFor={inputId} className="text-sm font-semibold">
        {label}
      </label>
      <div className="relative">
        <input
          id={inputId}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy || undefined}
          className={`block min-h-12 w-full rounded-control border bg-surface px-3.5 text-base text-ink transition-colors duration-150 placeholder:text-muted focus-visible:border-tinta read-only:bg-paper ${
            error ? 'border-danger' : 'border-field hover:border-ink'
          } ${trailing ? 'pr-14' : ''}`}
          {...inputProps}
        />
        {trailing && <div className="absolute inset-y-0 right-0.5 flex items-center">{trailing}</div>}
      </div>
      {hint && (
        <div id={hintId} className="text-sm text-muted">
          {hint}
        </div>
      )}
      {error && (
        <p id={errorId} className="flex items-start gap-1.5 text-sm font-medium text-danger">
          <AlertIcon className="mt-0.5 size-4 shrink-0" />
          <span>{error}</span>
        </p>
      )}
    </div>
  )
}
