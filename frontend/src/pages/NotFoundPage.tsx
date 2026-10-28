import { Link } from 'react-router'

export function NotFoundPage() {
  return (
    <section className="space-y-4 text-center">
      <h1 className="text-2xl font-bold">Página no encontrada</h1>
      <Link to="/" className="text-stone-600 underline hover:text-stone-900">
        Volver al inicio
      </Link>
    </section>
  )
}
