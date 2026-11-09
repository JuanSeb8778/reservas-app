// La sesión vive en la caché de TanStack Query bajo una sola clave: ['auth', 'me'].
// - undefined (todavía sin datos): se está comprobando la sesión.
// - User: hay sesión.
// - null: no hay sesión (visitante anónimo).
// Así no hace falta un Context propio: Query ya es un estado global, evita peticiones
// duplicadas (también con el doble render de StrictMode) y avisa a los componentes.
import type { QueryClient } from '@tanstack/react-query'

import { ApiError, hasAccessToken, onSessionExpired, refreshSession } from '../../lib/api'
import { fetchMe } from './authApi'
import type { User } from './types'

export const sessionQueryKey = ['auth', 'me'] as const

// Se ejecuta al abrir la app. El access token se perdió al recargar (vive en memoria), así
// que primero se intenta recuperar con la cookie de refresh.
export async function loadSession(): Promise<User | null> {
  if (!hasAccessToken()) {
    const refreshed = await refreshSession()
    if (!refreshed) return null
  }
  try {
    return await fetchMe()
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null
    throw error
  }
}

// Convención: los datos de un usuario concreto (sus citas, etc.) usan claves que empiezan
// por 'me', p. ej. ['me', 'bookings']. Los datos públicos (servicios, estado de la API) no.
export const userDataKey = ['me'] as const

// Borra de la caché los datos del usuario y marca la sesión como anónima. Se usa al cerrar
// sesión y cuando la sesión caduca. Los datos públicos se conservan (no hace falta volver a
// pedirlos).
export function clearSessionData(queryClient: QueryClient) {
  queryClient.removeQueries({ queryKey: userDataKey })
  queryClient.setQueryData(sessionQueryKey, null)
}

// Si una petición descubre que la sesión caducó (no se pudo renovar el token), la caché se
// actualiza y las rutas protegidas redirigen a /login.
export function listenForSessionExpiry(queryClient: QueryClient) {
  return onSessionExpired(() => clearSessionData(queryClient))
}
