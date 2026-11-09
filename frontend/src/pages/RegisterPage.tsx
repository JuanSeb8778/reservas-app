import { zodResolver } from '@hookform/resolvers/zod'
import { useForm, useWatch } from 'react-hook-form'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'

import { Button } from '../components/Button'
import { FormAlert } from '../components/FormAlert'
import { CheckIcon, CircleIcon } from '../components/icons'
import { PasswordField } from '../components/PasswordField'
import { TextField } from '../components/TextField'
import { AuthFormSkeleton, AuthLayout } from '../features/auth/AuthLayout'
import { PASSWORD_MIN, registerSchema, type RegisterValues } from '../features/auth/schemas'
import { AccountCreatedError, useRegister } from '../features/auth/useAuthMutations'
import { useSession } from '../features/auth/useSession'
import { ApiError } from '../lib/api'
import { getFrom, getRedirectTarget } from '../lib/navigationState'
import { useDelayedFlag } from '../lib/useDelayedFlag'
import { useDocumentTitle } from '../lib/useDocumentTitle'

const linkClasses =
  'font-semibold text-tinta underline decoration-2 underline-offset-4 hover:text-tinta-hover'

export function RegisterPage() {
  useDocumentTitle('Crear cuenta')
  const location = useLocation()
  const navigate = useNavigate()
  const session = useSession()
  const signup = useRegister()
  const showSkeleton = useDelayedFlag(session.status === 'loading')

  const {
    register,
    handleSubmit,
    setError,
    setFocus,
    getValues,
    control,
    formState: { errors },
  } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    mode: 'onTouched',
    defaultValues: { full_name: '', email: '', password: '' },
  })
  // useWatch (y no watch) para que solo este valor provoque nuevos renders.
  const password = useWatch({ control, name: 'password' })
  const passwordReady = password.length >= PASSWORD_MIN

  if (session.status === 'authenticated') {
    return <Navigate to={getRedirectTarget(location.state)} replace />
  }

  if (session.status === 'loading' || showSkeleton) {
    return <AuthLayout>{showSkeleton && <AuthFormSkeleton fields={3} />}</AuthLayout>
  }

  const from = getFrom(location.state)

  const onSubmit = handleSubmit((values) => {
    if (signup.isPending) return
    signup.mutate(values, {
      onError: (error) => {
        if (error instanceof AccountCreatedError) {
          navigate('/login', { replace: true, state: { notice: error.message, email: values.email, from } })
          return
        }
        // Correo ya registrado: el error va en el propio campo, que recibe el foco.
        if (error instanceof ApiError && error.status === 409) {
          setError('email', { type: 'conflict', message: error.message })
          setFocus('email')
        }
      },
    })
  })

  const emailConflict = errors.email?.type === 'conflict'
  const alertMessage =
    signup.error && !(signup.error instanceof ApiError && signup.error.status === 409)
      ? signup.error.message
      : null

  return (
    <AuthLayout>
      <h1 tabIndex={-1} className="text-[1.875rem] leading-[1.1] font-bold sm:text-4xl">
        Reserva sin <span className="marker">llamar</span>
      </h1>
      <p className="mt-2 text-muted">Crea tu cuenta en un minuto. Solo te pedimos lo necesario.</p>

      <FormAlert message={alertMessage} className="mt-6" />

      <form noValidate onSubmit={onSubmit} className="mt-6 grid gap-5">
        <TextField
          label="Nombre completo"
          autoComplete="name"
          readOnly={signup.isPending}
          error={errors.full_name?.message}
          {...register('full_name')}
        />
        <TextField
          label="Correo electrónico"
          type="email"
          autoComplete="email"
          inputMode="email"
          autoCapitalize="none"
          spellCheck={false}
          readOnly={signup.isPending}
          error={
            emailConflict ? (
              <>
                {errors.email?.message}.{' '}
                <Link to="/login" state={{ email: getValues('email'), from }} className={linkClasses}>
                  ¿Quieres iniciar sesión?
                </Link>
              </>
            ) : (
              errors.email?.message
            )
          }
          {...register('email')}
        />
        <PasswordField
          label="Contraseña"
          autoComplete="new-password"
          readOnly={signup.isPending}
          error={errors.password?.message}
          hint={
            // Requisito siempre visible; cambia de estado (icono + texto, no solo color) al cumplirse.
            <span aria-live="polite" className={`flex items-center gap-1.5 ${passwordReady ? 'text-ink' : ''}`}>
              {passwordReady ? (
                <CheckIcon className="size-4 shrink-0 text-ok" />
              ) : (
                <CircleIcon className="size-4 shrink-0" />
              )}
              Mínimo {PASSWORD_MIN} caracteres{passwordReady ? ' · cumplido' : ''}
            </span>
          }
          {...register('password')}
        />
        <Button type="submit" pending={signup.isPending} pendingLabel="Creando cuenta…" className="mt-1 w-full">
          Crear cuenta
        </Button>
        <p role="status" className="sr-only">
          {signup.isPending ? 'Creando tu cuenta…' : ''}
        </p>
      </form>

      <p className="mt-8 text-sm text-muted">
        ¿Ya tienes cuenta?{' '}
        <Link to="/login" state={from ? { from } : undefined} className={linkClasses}>
          Inicia sesión
        </Link>
      </p>
    </AuthLayout>
  )
}
