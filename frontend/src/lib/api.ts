// Cliente HTTP mínimo para hablar con la API.
// - Todas las rutas empiezan por /api (el proxy de Vite las envía al backend).
// - `credentials: 'include'` hace que el navegador envíe las cookies
//   (lo necesitaremos para el token de refresco en la Fase 1).

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    credentials: 'include',
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new ApiError(response.status, body?.detail ?? response.statusText)
  }

  return response.json() as Promise<T>
}
