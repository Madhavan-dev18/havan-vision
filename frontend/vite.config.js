import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'generate-redirects',
      writeBundle() {
        // This tells Vercel/Netlify to route ALL traffic to index.html
        fs.writeFileSync('dist/_redirects', '/* /index.html 200\n');
      }
    }
  ],
  test: {
    environment: 'jsdom',
    globals: true,
  },
});