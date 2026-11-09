import { useQuery } from '@tanstack/react-query'

import { fetchBusinessHours, fetchBusinessSettings } from './businessApi'

// Datos públicos del negocio (no empiezan por 'me': sobreviven al cierre de sesión).
export const businessSettingsQueryKey = ['business', 'settings'] as const
export const businessHoursQueryKey = ['business', 'hours'] as const

// La configuración y el horario casi nunca cambian: 5 minutos sin volver a pedirlos.
const FIVE_MINUTES = 5 * 60_000

export function useBusinessSettings() {
  return useQuery({
    queryKey: businessSettingsQueryKey,
    queryFn: fetchBusinessSettings,
    staleTime: FIVE_MINUTES,
  })
}

export function useBusinessHours() {
  return useQuery({
    queryKey: businessHoursQueryKey,
    queryFn: fetchBusinessHours,
    staleTime: FIVE_MINUTES,
  })
}
