import { buttonClasses } from '../components/buttonStyles'
import { BrandIcon } from '../components/icons'
import { useDocumentTitle } from '../lib/useDocumentTitle'

// Se muestra si algo falla de forma inesperada al renderizar una ruta (errorElement), en vez
// de la pantalla de error por defecto de React Router. Reemplaza al Layout entero, así que
// no depende de la sesión ni de nada que pueda ser lo que falló.
export function ErrorPage() {
  useDocumentTitle('Algo salió mal')

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-2xl flex-col justify-center px-4 py-14 sm:px-6">
      <p className="flex items-center gap-2 font-display text-xl font-bold tracking-tight">
        <BrandIcon className="size-6 text-tinta" />
        Reservas
      </p>
      <h1 className="mt-10 text-4xl font-bold">Algo salió mal</h1>
      <p className="mt-3 max-w-prose text-muted">
        Ocurrió un error inesperado al mostrar esta página. Vuelve al inicio e inténtalo de nuevo.
      </p>
      {/* Enlace normal (no <Link>): recarga la app desde cero, por si el error dejó algo roto. */}
      <a href="/" className={buttonClasses('primary', 'mt-8 self-start')}>
        Volver al inicio
      </a>
    </main>
  )
}
