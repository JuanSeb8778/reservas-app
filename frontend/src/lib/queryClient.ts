import { QueryClient } from '@tanstack/react-query'

import { ApiError } from './api'

// Por defecto TanStack Query reintenta 3 veces cualquier error. Un 4xx (401, 403, 404...) no
// se arregla reintentando, y reintentar un 401 volvería a pedir /auth/refresh. Solo se
// reintentan los fallos de red (status 0) y los errores del servidor (5xx).
function shouldRetry(failureCount: number, error: Error) {
  if (error instanceof ApiError && error.status >= 400 && error.status < 500) return false
  return failureCount < 2
}

// networkMode 'always': por defecto Query "pausa" las peticiones si el navegador dice estar
// sin conexión, y el botón se quedaría en "Entrando…" sin fin. Así la petición se intenta,
// falla, y apiFetch muestra el mensaje de "No se pudo conectar con el servidor".
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: shouldRetry, networkMode: 'always' },
    mutations: { retry: false, networkMode: 'always' },
  },
})
