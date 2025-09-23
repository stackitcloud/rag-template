// Flat ESLint config for Vue 3 + TypeScript (ESLint 9)
// Aligns with @vue/eslint-config-typescript v14 and Nx linting

import { defineConfig } from 'eslint/config'
import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from '@vue/eslint-config-typescript'

export default defineConfigWithVueTs(
  // Global ignores
  defineConfig([
    {
      name: 'global-ignores',
      ignores: [
        '**/dist/**',
        '**/build/**',
        '**/coverage/**',
        '**/.output/**',
        '**/.cache/**',
        '**/.vite/**',
      ],
    },
  ]),

  // Base JS recommended
  defineConfig([
    {
      files: ['**/*.js', '**/*.cjs', '**/*.mjs'],
      ...js.configs.recommended,
    },
  ]),

  // Vue essential rules
  pluginVue.configs['flat/essential'],

  // TS recommended (syntax only)
  vueTsConfigs.recommended,

  // Project-specific tweaks
  defineConfig([
    {
      files: ['**/*.vue', '**/*.ts', '**/*.tsx'],
      rules: {
        'vue/multi-word-component-names': 'off',
      },
    },
  ])
)
