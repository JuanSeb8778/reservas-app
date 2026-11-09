// Formato de precios y duraciones de los servicios. Funciones puras (sin React) para poder
// probarlas por separado.

const LOCALE = 'es-CO'

// Crear un Intl.NumberFormat es caro: se guardan los ya creados.
const formatters = new Map<string, Intl.NumberFormat>()

function getFormatter(key: string, options: Intl.NumberFormatOptions) {
  let formatter = formatters.get(key)
  if (!formatter) {
    formatter = new Intl.NumberFormat(LOCALE, options)
    formatters.set(key, formatter)
  }
  return formatter
}

// Los precios enteros se muestran sin decimales ("$ 25.000") y los demás con dos
// ("$ 25.000,50"). Sin esto, Intl redondearía los decimales en monedas como el peso.
function fractionDigits(amount: number): Intl.NumberFormatOptions {
  return Number.isInteger(amount)
    ? { minimumFractionDigits: 0, maximumFractionDigits: 0 }
    : { minimumFractionDigits: 2, maximumFractionDigits: 2 }
}

function format(price: string, currency: string | undefined, display: 'symbol' | 'name') {
  const amount = Number(price)
  const digits = fractionDigits(amount)
  const mode = digits.maximumFractionDigits
  if (currency) {
    try {
      return getFormatter(`${currency}|${display}|${mode}`, {
        style: 'currency',
        currency,
        currencyDisplay: display,
        ...digits,
      }).format(amount)
    } catch {
      // Código de moneda que el navegador no acepta: se muestra el número con el código.
      return `${getFormatter(`plain|${mode}`, digits).format(amount)} ${currency}`
    }
  }
  // Sin moneda (no se pudo cargar la configuración): solo el número.
  return getFormatter(`plain|${mode}`, digits).format(amount)
}

export function isFree(price: string) {
  return Number(price) === 0
}

// Para la vista: "$ 25.000".
export function formatPrice(price: string, currency?: string) {
  return isFree(price) ? 'Sin costo' : format(price, currency, 'symbol')
}

// Para lectores de pantalla: "25.000 pesos colombianos" (el símbolo "$" es ambiguo).
export function formatPriceSpoken(price: string, currency?: string) {
  return isFree(price) ? 'Sin costo' : format(price, currency, 'name')
}

function splitMinutes(minutes: number) {
  return { hours: Math.floor(minutes / 60), rest: minutes % 60 }
}

// "45 min", "1 h", "1 h 30 min".
export function formatDuration(minutes: number) {
  const { hours, rest } = splitMinutes(minutes)
  if (hours === 0) return `${rest} min`
  return rest === 0 ? `${hours} h` : `${hours} h ${rest} min`
}

// "45 minutos", "1 hora", "2 horas 30 minutos".
export function formatDurationSpoken(minutes: number) {
  const { hours, rest } = splitMinutes(minutes)
  const parts = []
  if (hours > 0) parts.push(`${hours} ${hours === 1 ? 'hora' : 'horas'}`)
  if (rest > 0) parts.push(`${rest} ${rest === 1 ? 'minuto' : 'minutos'}`)
  return parts.join(' ')
}
