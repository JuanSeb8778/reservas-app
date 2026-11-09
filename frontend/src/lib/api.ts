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

// ---------------------------------------------------------------------------------------------
// Access token: vive solo en esta variable (en memoria). Nunca en localStorage: un script
// inyectado (XSS) podría leerlo de ahí. Al recargar la página se pierde y se recupera con
// /auth/refresh, que usa la cookie httpOnly.
// ---------------------------------------------------------------------------------------------

// Debe coincidir con TokenResponse en backend/app/schemas/auth.py
export type TokenResponse = {
  access_token: string
  token_type: 'bearer'
  expires_in: number
}

let accessToken: string | null = null
// "Época" de la sesión: sube cada vez que se cierra sesión. Una renovación que termina después
// de un logout ve que la época cambió y descarta su token, para no "resucitar" la sesión.
let sessionEpoch = 0
// Renovación en curso, compartida: si varias peticiones reciben 401 a la vez, todas esperan
// la misma llamada a /auth/refresh en vez de lanzar una cada una.
let refreshInFlight: Promise<boolean> | null = null
const sessionExpiredListeners = new Set<() => void>()

// Rutas que no deben intentar renovar el token al recibir 401: su 401 significa otra cosa
// (credenciales incorrectas, no hay sesión) o renovar crearía un bucle.
const NO_REFRESH_PATHS = new Set(['/auth/login', '/auth/register', '/auth/refresh', '/auth/logout'])

export function hasAccessToken() {
  return accessToken !== null
}

export function setAccessToken(token: string) {
  accessToken = token
}

export function clearAccessToken() {
  accessToken = null
  sessionEpoch += 1
}

// Permite que la capa de sesión (TanStack Query) se entere de que la sesión caducó.
export function onSessionExpired(listener: () => void): () => void {
  sessionExpiredListeners.add(listener)
  return () => sessionExpiredListeners.delete(listener)
}

function expireSession() {
  clearAccessToken()
  sessionExpiredListeners.forEach((listener) => listener())
}

// Pide un access token nuevo usando la cookie. Devuelve true si lo consiguió y false si no
// hay sesión válida (401). Un fallo de red lanza ApiError(0): no es lo mismo que una sesión
// caducada y no debe cerrar la sesión del usuario.
export function refreshSession(): Promise<boolean> {
  if (refreshInFlight) return refreshInFlight

  const epoch = sessionEpoch
  refreshInFlight = (async () => {
    try {
      const data = await request<TokenResponse>('/auth/refresh', { method: 'POST' })
      if (epoch !== sessionEpoch) return false
      accessToken = data.access_token
      return true
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) return false
      throw error
    } finally {
      refreshInFlight = null
    }
  })()
  return refreshInFlight
}

// Una sola petición, sin lógica de renovación.
async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  // Solo se declara JSON cuando de verdad se envía un cuerpo.
  if (init.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  if (accessToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${accessToken}`)
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

// Petición a la API. Si responde 401 porque el access token caducó, lo renueva una vez y
// repite la petición. Si no se puede renovar, avisa de que la sesión caducó.
export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const epoch = sessionEpoch
  try {
    return await request<T>(path, init)
  } catch (error) {
    const canRefresh = error instanceof ApiError && error.status === 401 && !NO_REFRESH_PATHS.has(path)
    if (!canRefresh) throw error

    const refreshed = await refreshSession()
    if (!refreshed) {
      expireSession()
      throw error
    }
    // Si se cerró sesión mientras se renovaba, no se repite la petición.
    if (epoch !== sessionEpoch) throw error
    return request<T>(path, init)
  }
}
