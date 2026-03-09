import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: mode === 'production' ? 'http://orchestrator:8080' : 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: mode !== 'production',
    minify: mode === 'production' ? 'esbuild' : false,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/'],
    },
  },
}));
