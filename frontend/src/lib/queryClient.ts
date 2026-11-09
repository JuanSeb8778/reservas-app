import { QueryClient } from '@tanstack/react-query'

import { ApiError } from './api'

// Por defecto TanStack Query reintenta 3 veces cualquier error. Un 4xx (401, 403, 404...) no
// se arregla reintentando, y reintentar un 401 volvería a pedir /auth/refresh. Solo se
// reintentan los fallos de red (status 0) y los errores del servidor (5xx).
function shouldRetry(failureCount: number, error: Error) {
  if (error instanceof ApiError && error.status >= 400 && error.status < 500) return false
  return failureCount < 2
}

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: shouldRetry },
    mutations: { retry: false },
  },
})
