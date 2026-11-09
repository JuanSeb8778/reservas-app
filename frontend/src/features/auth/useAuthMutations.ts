import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router'

import { clearAccessToken } from '../../lib/api'
import { login, logout, register } from './authApi'
import { clearSessionData, sessionQueryKey } from './session'
import type { LoginInput, RegisterInput, User } from './types'

// La cuenta se creó pero el inicio de sesión automático falló (p. ej. se cortó la conexión).
// La página lo distingue de un error del registro para no decir "falló" cuando no es así.
export class AccountCreatedError extends Error {
  constructor() {
    super('Tu cuenta está creada. Inicia sesión para continuar.')
    this.name = 'AccountCreatedError'
  }
}

// Al terminar, guarda el usuario en la caché de la sesión. La redirección la hace la página
// al ver que ya hay sesión (un solo sitio decide a dónde ir).
export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: LoginInput) => login(input),
    onSuccess: (user) => queryClient.setQueryData<User | null>(sessionQueryKey, user),
  })
}

// Registro + inicio de sesión automático con los mismos datos.
export function useRegister() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (input: RegisterInput) => {
      await register(input)
      try {
        return await login({ email: input.email, password: input.password })
      } catch {
        throw new AccountCreatedError()
      }
    },
    onSuccess: (user) => queryClient.setQueryData<User | null>(sessionQueryKey, user),
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  return useMutation({
    mutationFn: async () => {
      // Cancela peticiones en curso para que ninguna respuesta tardía rellene la caché.
      await queryClient.cancelQueries()
      try {
        await logout()
      } catch {
        // Aunque falle (sin conexión), en este navegador la sesión se cierra igual.
      }
      clearAccessToken()
      // Primero se sale de la página actual: si se borrara la sesión estando en una ruta
      // protegida, esta redirigiría a /login en vez de ir al inicio.
      await navigate('/', { state: { notice: 'Cerraste sesión.' } })
      clearSessionData(queryClient)
    },
  })
}
