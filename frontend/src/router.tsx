import { createBrowserRouter } from 'react-router'

import { Layout } from './components/Layout'
import { RequireAdmin } from './features/auth/RequireAdmin'
import { RequireAuth } from './features/auth/RequireAuth'
import { AdminPage } from './pages/AdminPage'
import { ErrorPage } from './pages/ErrorPage'
import { LoginPage } from './pages/LoginPage'
import { MyBookingsPage } from './pages/MyBookingsPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { RegisterPage } from './pages/RegisterPage'
import { ServicesPage } from './pages/ServicesPage'

// Próximamente: /reservar...
export const router = createBrowserRouter([
  {
    element: <Layout />,
    errorElement: <ErrorPage />,
    children: [
      // La portada es la carta de servicios: en móvil no cabe un enlace más en la cabecera,
      // y el logo "Reservas" ya lleva aquí.
      { path: '/', element: <ServicesPage /> },
      { path: '/login', element: <LoginPage /> },
      { path: '/registro', element: <RegisterPage /> },
      {
        // Rutas que necesitan sesión.
        element: <RequireAuth />,
        children: [
          { path: '/mis-citas', element: <MyBookingsPage /> },
          {
            // Solo para el administrador del negocio.
            element: <RequireAdmin />,
            children: [{ path: '/admin', element: <AdminPage /> }],
          },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
