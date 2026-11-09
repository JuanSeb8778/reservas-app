import { useQuery } from '@tanstack/react-query'

import { fetchServices } from './servicesApi'

// Dato público: la clave no empieza por 'me', así que se conserva al cerrar sesión
// (ver clearSessionData en features/auth/session.ts).
export const servicesQueryKey = ['services'] as const

export function useServices() {
  return useQuery({
    queryKey: servicesQueryKey,
    queryFn: fetchServices,
    staleTime: 60_000, // el catálogo cambia poco: no se vuelve a pedir durante 1 minuto
  })
}
