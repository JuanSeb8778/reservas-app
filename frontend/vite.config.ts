import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// En desarrollo, las peticiones a /api se reenvían al backend (proxy).
// Así el frontend y la API parecen estar en el mismo origen y no hay problemas de CORS ni de cookies.
// Dentro de Docker, el backend se llama "backend"; fuera de Docker, "localhost".
const apiTarget = process.env.API_PROXY_TARGET ?? 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': { target: apiTarget, changeOrigin: true },
    },
  },
})
