/// <reference types="vitest" />
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue';
import { nxViteTsPaths } from '@nx/vite/plugins/nx-tsconfig-paths.plugin';
import { fileURLToPath } from 'url';
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite';
const CWD = process.cwd();

export default defineConfig(({ mode }) => {
  const envs = loadEnv(mode, CWD);
  return {
    ...envs,
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
