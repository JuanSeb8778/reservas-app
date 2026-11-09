// Datos que una página pasa a otra al navegar: navigate(to, { state }).
// Llegan como `unknown` (el historial del navegador puede traer cualquier cosa), así que se
// validan antes de usarlos.

function readString(state: unknown, key: string): string | undefined {
  if (typeof state !== 'object' || state === null) return undefined
  const value = (state as Record<string, unknown>)[key]
  return typeof value === 'string' ? value : undefined
}

// Mensaje para mostrar al llegar (p. ej. "Cerraste sesión").
export function getNotice(state: unknown) {
  return readString(state, 'notice')
}

// Correo para rellenar el formulario de login (p. ej. al venir del registro).
export function getEmail(state: unknown) {
  return readString(state, 'email')
}

// Página a la que volver después de iniciar sesión. Solo se aceptan rutas internas:
// "/mis-citas" sí; "https://otra.web", "//otra.web" o "/\t/otra.web" no. Así un enlace
// manipulado no puede llevar al usuario a otra web justo después de entrar (open redirect).
// En vez de buscar patrones peligrosos (siempre se escapa alguno), se deja que el propio
// navegador interprete la ruta con URL y se comprueba que siga en este mismo sitio.
export function getFrom(state: unknown): string | undefined {
  const from = readString(state, 'from')
  // Espacios, caracteres de control y "\" no aparecen en rutas legítimas de la app.
  if (!from || !from.startsWith('/') || /[\s\\\p{Cc}]/u.test(from)) return undefined
  try {
    const url = new URL(from, window.location.origin)
    if (url.origin !== window.location.origin) return undefined
    if (/^\/(login|registro)\/?$/.test(url.pathname)) return undefined
    return url.pathname + url.search + url.hash
  } catch {
    return undefined
  }
}

export function getRedirectTarget(state: unknown) {
  return getFrom(state) ?? '/mis-citas'
}
