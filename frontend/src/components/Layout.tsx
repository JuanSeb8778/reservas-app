import { Link, Outlet } from 'react-router'

export function Layout() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-stone-200 bg-white">
        <nav className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
          <Link to="/" className="text-lg font-semibold tracking-tight">
            Reservas
          </Link>
          <span className="text-sm text-stone-500">Fase 0</span>
        </nav>
      </header>

      {/* Cada página decide su ancho (Page para las normales, AuthLayout para el acceso). */}
      <main>
        <Outlet />
      </main>
    </div>
  )
}
