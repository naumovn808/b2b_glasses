import react, { reactCompilerPreset } from '@vitejs/plugin-react';

import babel from '@rolldown/plugin-babel';
import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import svgr from 'vite-plugin-svgr';

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: '0.0.0.0',
  },
  resolve: {
    alias: {
      '@': path.resolve(path.dirname(fileURLToPath(import.meta.url)), 'src'),
    },
  },
  plugins: [react(), svgr({}), babel({ presets: [reactCompilerPreset()] })],
});
