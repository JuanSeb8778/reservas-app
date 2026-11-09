// Deben coincidir con backend/app/schemas/business_settings.py y business_hours.py

// BusinessSettingsRead
export type BusinessSettings = {
  timezone: string // nombre IANA, p. ej. "America/Bogota"
  currency: string // código ISO 4217 en mayúsculas, p. ej. "COP"
}

// BusinessHoursRange: hora local del negocio, "HH:MM" en formato de 24 h.
export type BusinessHoursRange = {
  weekday: number // 0 = lunes … 6 = domingo
  opens_at: string
  closes_at: string
}

// BusinessHoursWeek: un día sin tramos está cerrado.
export type BusinessHoursWeek = {
  ranges: BusinessHoursRange[]
}
