/// <reference types="vitest" />
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite';
import { nxViteTsPaths } from '@nx/vite/plugins/nx-tsconfig-paths.plugin';
import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath } from 'node:url';
import { defineConfig, loadEnv } from 'vite';

const CWD = process.cwd();

export default defineConfig(({ mode }) => {
  const envs = loadEnv(mode, CWD);
  return {
    ...envs,
    root: fileURLToPath(new URL('./', import.meta.url)),
    cacheDir: '../../node_modules/.vite/chat-app',
    server: {
      port: 4200,
      host: 'localhost',
      fs: {
        allow: ['../../libs/i18n'],
      },
    },
    build: {
      rollupOptions: {
        input: fileURLToPath(new URL('./index.html', import.meta.url)),
      },
    },
    plugins: [
      vue(),
      nxViteTsPaths(),
      VueI18nPlugin({
        include: '../../libs/i18n/chat/**/*.json',
      }),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '@chat-app/i18n': fileURLToPath(
          new URL('../../libs/i18n/chat/index.ts', import.meta.url)
        ),
        '@shared/style': fileURLToPath(
          new URL('../../libs/shared/global.css', import.meta.url)
        ),
      },
    },
  };
});
