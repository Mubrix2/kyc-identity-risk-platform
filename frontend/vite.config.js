import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5174,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/health': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Recharts is large — split it into its own chunk loaded separately
          'recharts': ['recharts'],
          // React core — always cached after first visit
          'react-vendor': ['react', 'react-dom'],
        },
      },
    },
    // Raise warning threshold slightly — 600kB is reasonable for a
    // dashboard with charting libraries
    chunkSizeWarningLimit: 600,
  },
})