import { nxViteTsPaths } from '@nx/vite/plugins/nx-tsconfig-paths.plugin'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [
    vue(),
    nxViteTsPaths(), // Nx monorepo TS path aliases
    tailwindcss(),   // Tailwind v4 (Vite plugin)
  ],
})
