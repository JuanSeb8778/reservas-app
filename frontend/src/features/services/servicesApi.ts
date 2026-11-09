// Llamadas a /api/services. Sin sesión devuelve los servicios activos.
import { apiFetch } from '../../lib/api'
import type { Service } from './types'

export function fetchServices() {
  return apiFetch<Service[]>('/services')
}
