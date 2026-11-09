import { AlertIcon } from './icons'

// Error general de un formulario (p. ej. "Correo o contraseña incorrectos").
// El contenedor role="alert" existe siempre (vacío si no hay error) y nunca se oculta con
// display:none: así el lector de pantalla anuncia el mensaje en cuanto aparece. Vacío mide
// 0 px de alto, por eso el margen va en el mensaje y no en el contenedor.
export function FormAlert({ message, className = '' }: { message?: string | null; className?: string }) {
  return (
    <div role="alert">
      {message && (
        <p
          className={`flex items-start gap-2.5 rounded-control border-l-4 border-danger bg-danger-soft px-3.5 py-3 text-sm text-ink ${className}`}
        >
          <AlertIcon className="mt-0.5 size-4 shrink-0 text-danger" />
          <span>{message}</span>
        </p>
      )}
    </div>
  )
}
