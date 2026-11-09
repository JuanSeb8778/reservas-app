import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router'

import { clearAccessToken } from '../../lib/api'
import { login, logout, register } from './authApi'
import { clearSessionData, sessionQueryKey, userDataKey } from './session'
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
        // El login pudo guardar el token y fallar después (en /me): se borra para no dejar
        // un token "huérfano" mientras la interfaz dice que no hay sesión.
        clearAccessToken()
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
      // Cancela las peticiones del usuario en curso para que ninguna respuesta tardía
      // rellene la caché. La de la sesión no: cancelarla la dejaría "cargando" para siempre.
      await queryClient.cancelQueries({ queryKey: userDataKey })

      let confirmed = true
      try {
        await logout()
      } catch {
        // Sin conexión: en este navegador la sesión se cierra igual, pero la cookie de
        // refresh sigue viva en el servidor y al recargar la sesión volvería. Se avisa.
        confirmed = false
      }
      clearAccessToken()

      // Primero se sale de la página actual: si se borrara la sesión estando en una ruta
      // protegida, esta redirigiría a /login en vez de ir al inicio. flushSync hace que el
      // cambio de página se pinte ya, antes de borrar la sesión.
      await navigate('/', {
        flushSync: true,
        state: {
          notice: confirmed
            ? 'Cerraste sesión.'
            : 'Saliste en este navegador, pero no pudimos confirmarlo con el servidor por un problema de conexión. Si usas un equipo compartido, cuando vuelvas a tener conexión recarga la página y cierra sesión de nuevo.',
        },
      })
      clearSessionData(queryClient)
    },
  })
}
