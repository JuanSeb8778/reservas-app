// Formato del horario semanal y de la zona horaria del negocio. Funciones puras (sin React).
import type { BusinessHoursRange } from './types'

// Mismo orden que el backend: 0 = lunes … 6 = domingo. Ojo: Date.getDay() empieza en domingo,
// por eso no se usa para saber qué día es.
export const WEEKDAY_NAMES = [
  'lunes',
  'martes',
  'miércoles',
  'jueves',
  'viernes',
  'sábado',
  'domingo',
] as const

export function capitalize(text: string) {
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export type DayHours = {
  weekday: number
  name: string // "lunes"
  ranges: BusinessHoursRange[] // vacío = cerrado
}

// Siempre 7 días, de lunes a domingo, con sus tramos ordenados por hora de apertura.
// Las horas "HH:MM" se comparan como texto: con dos dígitos el orden alfabético es el horario.
export function groupHoursByDay(ranges: BusinessHoursRange[]): DayHours[] {
  return WEEKDAY_NAMES.map((name, weekday) => ({
    weekday,
    name,
    ranges: ranges
      .filter((range) => range.weekday === weekday)
      .sort((a, b) => a.opens_at.localeCompare(b.opens_at)),
  }))
}

const SHORT_WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

// Día de la semana (0 = lunes) en la zona del negocio. "Hoy" es el día del negocio, no el del
// visitante: a las 23:00 en Madrid ya es otro día que en Bogotá. null si la zona no es válida.
export function weekdayInTimezone(timeZone: string, date = new Date()): number | null {
  try {
    const short = new Intl.DateTimeFormat('en-US', { timeZone, weekday: 'short' }).format(date)
    const index = SHORT_WEEKDAYS.indexOf(short)
    return index === -1 ? null : index
  } catch {
    return null
  }
}

// Desfase respecto a UTC en un instante, p. ej. "GMT-05:00" (o "GMT" para UTC).
function utcOffset(timeZone: string | undefined, date: Date) {
  return new Intl.DateTimeFormat('en-US', { timeZone, timeZoneName: 'longOffset' })
    .formatToParts(date)
    .find((part) => part.type === 'timeZoneName')?.value
}

// ¿El reloj del visitante marca otra hora que el del negocio? Se compara el desfase y no el
// nombre: "America/Lima" y "America/Bogota" son nombres distintos con la misma hora. Así
// también se tiene en cuenta el horario de verano de cada zona en la fecha dada.
export function deviceClockDiffers(
  businessTimeZone: string,
  date = new Date(),
  deviceTimeZone?: string,
): boolean {
  try {
    return utcOffset(businessTimeZone, date) !== utcOffset(deviceTimeZone, date)
  } catch {
    return false // zona desconocida para el navegador: mejor no avisar que avisar mal
  }
}

// Nombre de la zona en español, p. ej. "hora estándar de Colombia". Lo traduce el navegador,
// así no hace falta mantener una lista propia. Si no lo sabe, se usa el nombre IANA.
export function timezoneLabel(timeZone: string, date = new Date()): string {
  try {
    const name = new Intl.DateTimeFormat('es', { timeZone, timeZoneName: 'longGeneric' })
      .formatToParts(date)
      .find((part) => part.type === 'timeZoneName')?.value
    return name ?? timeZone
  } catch {
    return timeZone
  }
}
