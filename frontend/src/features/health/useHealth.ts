import { useQuery } from '@tanstack/react-query'

import { apiFetch } from '../../lib/api'

// Debe coincidir con HealthResponse en backend/app/api/routes/health.py
export type Health = {
  status: 'ok'
  database: 'ok' | 'error'
}

// TanStack Query se encarga de: estado de carga, errores, caché y reintentos.
export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiFetch<Health>('/health'),
    refetchInterval: 10_000, // vuelve a comprobar cada 10 segundos
  })
}
