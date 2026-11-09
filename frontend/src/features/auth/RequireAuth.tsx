import { Navigate, Outlet, useLocation } from 'react-router'

import { PageSkeleton } from '../../components/Skeleton'
import { useDelayedFlag } from '../../lib/useDelayedFlag'
import { useSession } from './useSession'

// Ruta padre que protege a sus hijas: sin sesión, manda a /login y recuerda a dónde se
// quería ir. Es solo comodidad para el usuario: la seguridad real está en el backend, que
// rechaza cualquier petición sin un token válido.
export function RequireAuth() {
  const session = useSession()
  const location = useLocation()
  const showSkeleton = useDelayedFlag(session.status === 'loading')

  if (session.status === 'loading' || showSkeleton) {
    return showSkeleton ? <PageSkeleton /> : null
  }

  if (session.status === 'anonymous') {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location.pathname + location.search,
          notice: 'Inicia sesión para continuar.',
        }}
      />
    )
  }

  return <Outlet />
}
