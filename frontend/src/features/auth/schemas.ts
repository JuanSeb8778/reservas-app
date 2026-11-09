import { z } from 'zod'

// Mismas reglas que backend/app/schemas/user.py y auth.py. Validar también aquí permite
// mostrar el error al momento, junto al campo, sin esperar a la API.

export const PASSWORD_MIN = 8
const PASSWORD_MAX = 128

const email = z
  .string()
  .trim()
  .min(1, 'Escribe tu correo.')
  .pipe(z.email({ error: 'Ese correo no parece válido. Revisa que tenga la forma nombre@dominio.com.' }))

export const loginSchema = z.object({
  email,
  // En el login solo se pide que no esté vacía (igual que el backend).
  password: z
    .string()
    .min(1, 'Escribe tu contraseña.')
    .max(PASSWORD_MAX, `La contraseña no puede tener más de ${PASSWORD_MAX} caracteres.`),
})

export const registerSchema = z.object({
  full_name: z
    .string()
    .trim()
    .min(1, 'Escribe tu nombre.')
    .max(100, 'El nombre no puede tener más de 100 caracteres.')
    // \p{Cc} = caracteres de control (saltos de línea, tabuladores, \0...). El backend los rechaza.
    .regex(/^\P{Cc}*$/u, 'El nombre tiene caracteres no permitidos.'),
  email,
  password: z
    .string()
    .min(PASSWORD_MIN, `La contraseña necesita al menos ${PASSWORD_MIN} caracteres.`)
    .max(PASSWORD_MAX, `La contraseña no puede tener más de ${PASSWORD_MAX} caracteres.`),
})

export type LoginValues = z.infer<typeof loginSchema>
export type RegisterValues = z.infer<typeof registerSchema>
