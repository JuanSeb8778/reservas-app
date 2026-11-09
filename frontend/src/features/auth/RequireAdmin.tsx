import { Outlet } from 'react-router'

import { ForbiddenPage } from '../../pages/ForbiddenPage'
import { useSession } from './useSession'

// Va siempre dentro de RequireAuth, así que aquí ya hay sesión. Si el usuario no es admin
// se muestra el 403 en la misma URL (sin redirigir), para que se entienda qué pasó.
// Igual que RequireAuth, es solo interfaz: el backend comprueba el rol en cada endpoint.
export function RequireAdmin() {
  const session = useSession()
  if (session.status !== 'authenticated') return null
  if (session.user.role !== 'admin') return <ForbiddenPage />
  return <Outlet />
}
