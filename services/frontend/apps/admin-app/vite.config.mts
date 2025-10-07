/// <reference types="vitest" />
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite';
import { nxViteTsPaths } from '@nx/vite/plugins/nx-tsconfig-paths.plugin';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath } from 'url';
import { defineConfig, loadEnv } from 'vite';
const CWD = process.cwd();

export default defineConfig(({ mode }) => {
  const envs = loadEnv(mode, CWD);
  return {
    ...envs,
    // Ensure Vite uses the app directory as root
    root: fileURLToPath(new URL('./', import.meta.url)),
    cacheDir: '../../node_modules/.vite/admin-app',
    server: {
      port: 4300,
      host: 'localhost',

      fs: {
        allow: [
          '../../libs/i18n'
        ],
      },
    },
    build: {
      rollupOptions: {
        // Explicit entry to resolve index.html correctly when building via Nx
        input: fileURLToPath(new URL('./index.html', import.meta.url)),
      },
    },
    plugins: [
      vue(),
      nxViteTsPaths(),
      VueI18nPlugin({
        include: '../../libs/i18n/admin/locales/**',
      }),
    ],

    resolve: {
      alias: {
        '@admin-app/i18n': fileURLToPath(
          new URL('../../libs/i18n/admin/index.ts', import.meta.url)
        ),
        '@shared/style': fileURLToPath(
          new URL('../../libs/shared/global.css', import.meta.url)
        ),
      },
    },
  }
});
