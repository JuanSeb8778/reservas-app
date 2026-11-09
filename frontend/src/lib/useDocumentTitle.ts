import { useEffect } from 'react'

// Título de la pestaña por página ("Iniciar sesión – Reservas"). En una SPA el navegador no lo
// cambia solo, y es lo primero que anuncian los lectores de pantalla al cambiar de página.
export function useDocumentTitle(title: string) {
  useEffect(() => {
    document.title = `${title} – Reservas`
  }, [title])
}
