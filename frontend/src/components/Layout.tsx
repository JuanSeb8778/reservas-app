import { useEffect, useRef } from 'react'
import { Link, NavLink, Outlet, ScrollRestoration, useLocation } from 'react-router'

import { useLogout } from '../features/auth/useAuthMutations'
import { useSession } from '../features/auth/useSession'
import { useDelayedFlag } from '../lib/useDelayedFlag'
import { Button } from './Button'
import { buttonClasses } from './buttonStyles'
import { BrandIcon } from './icons'
import { Skeleton } from './Skeleton'

// En una SPA el navegador no mueve el foco al cambiar de página. Se lleva al título (h1) de
// la nueva página para que el lector de pantalla la anuncie y el teclado empiece desde ahí.
// Se compara con la ruta anterior (y no con "es el primer render") porque StrictMode
// ejecuta los efectos dos veces al montar.
function useFocusOnNavigation(pathname: string) {
  const previous = useRef(pathname)
  useEffect(() => {
    if (previous.current === pathname) return
    previous.current = pathname
    const target = document.querySelector<HTMLElement>('#main h1') ?? document.getElementById('main')
    target?.focus()
  }, [pathname])
}

function SessionNav() {
  const session = useSession()
  const logout = useLogout()
  const showSkeleton = useDelayedFlag(session.status === 'loading')

  // Mientras se comprueba la sesión no se muestra "Iniciar sesión" (que luego cambiaría por
  // el nombre del usuario): se reserva el sitio y, si tarda, aparece el skeleton.
  if (session.status === 'loading' || showSkeleton) {
    return (
      <div className="flex min-w-40 items-center justify-end gap-3">
        {showSkeleton && (
          <>
            <Skeleton className="h-5 w-16" />
            <Skeleton className="h-11 w-28 rounded-control" />
          </>
        )}
      </div>
    )
  }

  if (session.status === 'anonymous') {
    return (
      <nav aria-label="Principal" className="flex items-center gap-1.5 sm:gap-2">
        <NavLink to="/login" className={buttonClasses('ghost', 'px-3')}>
          <span className="sm:hidden">Entrar</span>
          <span className="hidden sm:inline">Iniciar sesión</span>
        </NavLink>
        <NavLink to="/registro" className={buttonClasses('primary', 'px-3 sm:px-4')}>
          Crear cuenta
        </NavLink>
      </nav>
    )
  }

  const firstName = session.user.full_name.split(/\s+/)[0]

  return (
    <nav aria-label="Principal" className="flex items-center gap-1 sm:gap-2">
      {session.user.role === 'admin' && (
        <NavLink to="/admin" className={buttonClasses('ghost', 'px-3')}>
          {({ isActive }) => <span className={isActive ? 'marker' : ''}>Panel</span>}
        </NavLink>
      )}
      <NavLink to="/mis-citas" className={buttonClasses('ghost', 'px-3')}>
        {({ isActive }) => <span className={isActive ? 'marker' : ''}>Mis citas</span>}
      </NavLink>
      <span className="hidden max-w-[16ch] truncate px-2 text-sm text-muted md:inline">
        Hola, {firstName}
      </span>
      <Button
        variant="secondary"
        className="px-3"
        pending={logout.isPending}
        pendingLabel="Saliendo…"
        onClick={() => logout.mutate()}
      >
        <span className="sm:hidden">Salir</span>
        <span className="hidden sm:inline">Cerrar sesión</span>
      </Button>
    </nav>
  )
}

export function Layout() {
  const location = useLocation()
  useFocusOnNavigation(location.pathname)

  return (
    <div className="flex min-h-dvh flex-col">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-4 focus:z-50 focus:rounded-control focus:bg-surface focus:px-4 focus:py-2.5 focus:font-semibold focus:shadow-sm"
      >
        Saltar al contenido
      </a>

      <header className="border-b border-line bg-surface">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-3 px-4 sm:px-6">
          <Link
            to="/"
            className="flex min-h-11 items-center gap-2 font-display text-xl font-bold tracking-tight sm:text-[1.375rem]"
          >
            <BrandIcon className="size-6 text-tinta max-[22rem]:hidden" />
            Reservas
          </Link>
          <SessionNav />
        </div>
      </header>

      {/* Cada página decide su ancho (Page para las normales, AuthLayout para el acceso).
          tabIndex -1: permite que el enlace "Saltar al contenido" le mueva el foco. */}
      <main id="main" tabIndex={-1} className="flex flex-1 flex-col">
        <Outlet />
      </main>

      <ScrollRestoration />
    </div>
  )
}
