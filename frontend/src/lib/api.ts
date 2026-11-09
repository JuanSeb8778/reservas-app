// Cliente HTTP para hablar con la API. Es el único punto del frontend que llama a `fetch`.
// - Todas las rutas empiezan por /api (el proxy de Vite las envía al backend).
// - `credentials: 'include'` hace que el navegador envíe las cookies (el refresh token).

export class ApiError extends Error {
  // 0 = no hubo respuesta (sin conexión, servidor caído).
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

const NETWORK_ERROR = 'No se pudo conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.'
// Los mensajes de validación de Pydantic vienen en inglés y pensados para desarrolladores.
// Los formularios validan lo mismo con Zod antes de enviar, así que un 422 es raro: basta un
// mensaje general en español.
const VALIDATION_ERROR = 'Algunos datos no son válidos. Revísalos e inténtalo de nuevo.'

function toApiError(response: Response, body: unknown): ApiError {
  const detail = (body as { detail?: unknown } | undefined)?.detail
  if (typeof detail === 'string') return new ApiError(response.status, detail)
  if (response.status === 422) return new ApiError(response.status, VALIDATION_ERROR)
  return new ApiError(response.status, response.statusText || 'Ocurrió un error inesperado.')
}

// Lee el cuerpo sin romperse con respuestas vacías (p. ej. 204 No Content del logout).
async function readBody(response: Response): Promise<unknown> {
  if (response.status === 204) return undefined
  const text = await response.text()
  if (!text) return undefined
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  // Solo se declara JSON cuando de verdad se envía un cuerpo.
  if (init.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  let response: Response
  try {
    response = await fetch(`/api${path}`, { ...init, headers, credentials: 'include' })
  } catch (error) {
    // Una petición cancelada no es un error de red: se deja pasar tal cual.
    if (error instanceof DOMException && error.name === 'AbortError') throw error
    throw new ApiError(0, NETWORK_ERROR)
  }

  const body = await readBody(response)
  if (!response.ok) throw toApiError(response, body)
  return body as T
}
