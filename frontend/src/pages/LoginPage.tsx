import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useLocation } from 'react-router'

import { Button } from '../components/Button'
import { FormAlert } from '../components/FormAlert'
import { Notice } from '../components/Notice'
import { PasswordField } from '../components/PasswordField'
import { TextField } from '../components/TextField'
import { AuthFormSkeleton, AuthLayout } from '../features/auth/AuthLayout'
import { loginSchema, type LoginValues } from '../features/auth/schemas'
import { useLogin } from '../features/auth/useAuthMutations'
import { useSession } from '../features/auth/useSession'
import { ApiError } from '../lib/api'
import { getEmail, getFrom, getNotice, getRedirectTarget } from '../lib/navigationState'
import { useDelayedFlag } from '../lib/useDelayedFlag'
import { useDocumentTitle } from '../lib/useDocumentTitle'

export function LoginPage() {
  useDocumentTitle('Iniciar sesión')
  const location = useLocation()
  const session = useSession()
  const login = useLogin()
  const showSkeleton = useDelayedFlag(session.status === 'loading')

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    // Valida al salir de cada campo y, desde entonces, mientras se escribe.
    mode: 'onTouched',
    defaultValues: { email: getEmail(location.state) ?? '', password: '' },
  })

  // Único sitio que decide a dónde ir tras entrar: si hay sesión (recién iniciada o ya
  // existente), se vuelve a la página de origen.
  if (session.status === 'authenticated') {
    return <Navigate to={getRedirectTarget(location.state)} replace />
  }

  if (session.status === 'loading' || showSkeleton) {
    return <AuthLayout>{showSkeleton && <AuthFormSkeleton fields={2} />}</AuthLayout>
  }

  const onSubmit = handleSubmit((values) => {
    if (login.isPending) return
    login.mutate(values, {
      onError: (error) => {
        // Credenciales incorrectas: se borra la contraseña y se deja el correo. El foco no
        // se mueve: así el lector de pantalla lee la alerta completa sin interrupciones.
        if (error instanceof ApiError && error.status === 401) {
          setValue('password', '')
        }
      },
    })
  })

  const notice = getNotice(location.state)
  const from = getFrom(location.state)

  return (
    <AuthLayout>
      <h1 tabIndex={-1} className="text-[1.875rem] leading-[1.1] font-bold sm:text-4xl">
        Vuelve a tu <span className="marker">agenda</span>
      </h1>
      <p className="mt-2 text-muted">Entra para ver y gestionar tus citas.</p>

      {notice && <Notice className="mt-6">{notice}</Notice>}
      <FormAlert message={login.error?.message} className="mt-6" />

      <form noValidate onSubmit={onSubmit} className="mt-6 grid gap-5">
        <TextField
          label="Correo electrónico"
          type="email"
          autoComplete="email"
          inputMode="email"
          autoCapitalize="none"
          spellCheck={false}
          readOnly={login.isPending}
          error={errors.email?.message}
          {...register('email')}
        />
        <PasswordField
          label="Contraseña"
          autoComplete="current-password"
          readOnly={login.isPending}
          error={errors.password?.message}
          {...register('password')}
        />
        <Button type="submit" pending={login.isPending} pendingLabel="Entrando…" className="mt-1 w-full">
          Entrar
        </Button>
        <p role="status" className="sr-only">
          {login.isPending ? 'Entrando…' : ''}
        </p>
      </form>

      <p className="mt-8 text-sm text-muted">
        ¿Aún no tienes cuenta?{' '}
        <Link
          to="/registro"
          state={from ? { from } : undefined}
          className="font-semibold text-tinta underline decoration-2 underline-offset-4 hover:text-tinta-hover"
        >
          Crea una en un minuto
        </Link>
      </p>
    </AuthLayout>
  )
}
