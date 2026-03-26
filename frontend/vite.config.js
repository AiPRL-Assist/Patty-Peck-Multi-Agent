import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/apps': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/run_sse': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/list-apps': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/debug': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
