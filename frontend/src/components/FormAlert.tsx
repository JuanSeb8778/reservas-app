import { AlertIcon } from './icons'

// Error general de un formulario (p. ej. "Correo o contraseña incorrectos").
// El contenedor role="alert" existe siempre, vacío si no hay error: así el lector de pantalla
// anuncia el mensaje en cuanto aparece. `empty:` evita que ocupe espacio mientras está vacío.
export function FormAlert({ message, className = '' }: { message?: string | null; className?: string }) {
  return (
    <div role="alert" className={`empty:hidden ${className}`}>
      {message && (
        <p className="flex items-start gap-2.5 rounded-control border-l-4 border-danger bg-danger-soft px-3.5 py-3 text-sm text-ink">
          <AlertIcon className="mt-0.5 size-4 shrink-0 text-danger" />
          <span>{message}</span>
        </p>
      )}
    </div>
  )
}
