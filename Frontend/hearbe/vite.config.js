import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    strictPort: true, // 포트 5173 번 고정 (이미 사용 중이면 에러 발생)
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/cart': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/wishlist': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/orders': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/members': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/welfare': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  }
})
