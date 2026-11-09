import { QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Desde 'react-router/dom' (y no 'react-router'): esta versión usa ReactDOM.flushSync, sin el
// cual la opción navigate(..., { flushSync: true }) del logout no tendría efecto.
import { RouterProvider } from 'react-router/dom'

import { listenForSessionExpiry } from './features/auth/session'
import './index.css'
import { queryClient } from './lib/queryClient'
import { router } from './router'

listenForSessionExpiry(queryClient)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
)
