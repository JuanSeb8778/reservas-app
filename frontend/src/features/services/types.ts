// Debe coincidir con ServiceRead en backend/app/schemas/service.py
export type Service = {
  id: number
  name: string
  description: string | null
  duration_minutes: number // 5–480, múltiplo de 5
  // Decimal de Python: llega como texto ("25000.00") para no perder precisión. Solo se
  // convierte a número para mostrarlo; nunca se hacen cuentas con él en el navegador.
  price: string
  is_active: boolean
  created_at: string // fecha ISO 8601 en UTC
}
