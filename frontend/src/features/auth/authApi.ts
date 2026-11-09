// Llamadas a los endpoints de /api/auth. Funciones simples: el estado lo maneja TanStack Query.
import { apiFetch, setAccessToken, type TokenResponse } from '../../lib/api'
import type { LoginInput, RegisterInput, User } from './types'

export function fetchMe() {
  return apiFetch<User>('/auth/me')
}

// El login devuelve solo el token; luego se pide /me para tener los datos del usuario.
export async function login(input: LoginInput): Promise<User> {
  const tokens = await apiFetch<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  setAccessToken(tokens.access_token)
  return fetchMe()
}

export function register(input: RegisterInput) {
  return apiFetch<User>('/auth/register', { method: 'POST', body: JSON.stringify(input) })
}

export function logout() {
  return apiFetch<void>('/auth/logout', { method: 'POST' })
}
