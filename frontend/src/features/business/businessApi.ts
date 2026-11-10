// Llamadas públicas a la configuración y al horario del negocio.
import { apiFetch } from '../../lib/api'
import type { BusinessHoursWeek, BusinessSettings } from './types'

export function fetchBusinessSettings() {
  return apiFetch<BusinessSettings>('/business-settings')
}

export function fetchBusinessHours() {
  return apiFetch<BusinessHoursWeek>('/business-hours')
}
