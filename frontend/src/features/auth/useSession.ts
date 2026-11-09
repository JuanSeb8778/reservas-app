import { useQuery } from '@tanstack/react-query'

import { loadSession, sessionQueryKey } from './session'
import type { User } from './types'

export type Session =
  | { status: 'loading'; user: null }
  | { status: 'anonymous'; user: null }
  | { status: 'authenticated'; user: User }

export function useSession(): Session {
  const query = useQuery({
    queryKey: sessionQueryKey,
    queryFn: loadSession,
    // La sesión no "caduca" en la caché: solo cambia con login, logout o si la API dice que
    // el token ya no vale. Sin esto, Query volvería a pedir /me cada vez que se enfoca la pestaña.
    staleTime: Infinity,
    gcTime: Infinity,
  })

  if (query.isPending) return { status: 'loading', user: null }
  if (query.data) return { status: 'authenticated', user: query.data }
  // null o un error (p. ej. sin conexión al abrir la app): se trata como visitante.
  return { status: 'anonymous', user: null }
}
