import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

import path from 'path';
import fs from 'fs';

function loadSharedEnv(envPath: string): Record<string, string> {
  const envFile = fs.readFileSync(envPath, 'utf-8');
  const lines = envFile.split('\n');

  const mapped: Record<string, string> = {};
  for (const line of lines) {
    if (!line.trim() || line.trim().startsWith('#')) continue;
    const [key, value] = line.split('=');
    if (key && value) {
      mapped[`VITE_${key.trim()}`] = value.trim();
    }
  }
  return mapped;
}


export default defineConfig(({mode}) => {
  const sharedEnv = loadSharedEnv(path.resolve(__dirname, '../.env'));

  return {
    plugins: [react(), tailwindcss()],
    server: {
      watch: {
        usePolling: true
      }
    },
    define: {
      // 'process.env.BACKEND_PORT': parseInt(sharedEnv.VITE_BACKEND_PORT) || 8000,
      'process.env.API_BASE': JSON.stringify(`http://localhost:${sharedEnv.VITE_BACKEND_PORT || '8000'}/api`),
        'process.env.GOOGLE_CLIENT_ID': JSON.stringify(sharedEnv.VITE_GOOGLE_CLIENT_ID || ''),
    },
  };
});


// resolve: {
//   alias: {
//     '@': path.resolve(__dirname, '.'),
//   }
// }
