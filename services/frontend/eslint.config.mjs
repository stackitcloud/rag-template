// Flat ESLint config for Vue 3 + TypeScript (ESLint 9)
// Aligns with @vue/eslint-config-typescript v14 and Nx linting

import js from '@eslint/js'
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from '@vue/eslint-config-typescript'
import pluginVue from 'eslint-plugin-vue'
import { defineConfig } from 'eslint/config'
// Nx plugin for module boundaries; supports both @nx/eslint-plugin and @nrwl/eslint-plugin-nx
import nxPlugin from '@nx/eslint-plugin'
import tsParser from '@typescript-eslint/parser'
import vueParser from 'vue-eslint-parser'

export default defineConfigWithVueTs(
  // Global ignores
  defineConfig([
    {
      name: 'global-ignores',
      ignores: [
        'node_modules',
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
      languageOptions: {
        sourceType: 'module',
        ecmaVersion: 'latest',
      },
    },
  ]),

  // Ensure TypeScript files are parsed with @typescript-eslint/parser
  defineConfig([
    {
      files: ['**/*.ts', '**/*.tsx', '**/*.d.ts'],
      languageOptions: {
        parser: tsParser,
        sourceType: 'module',
        ecmaVersion: 'latest',
      },
    },
  ]),

  // Ensure Vue SFCs are parsed with vue-eslint-parser and TS inside scripts
  defineConfig([
    {
      files: ['**/*.vue'],
      languageOptions: {
        parser: vueParser,
        parserOptions: {
          parser: tsParser,
          sourceType: 'module',
          ecmaVersion: 'latest',
          extraFileExtensions: ['.vue'],
        },
      },
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
      plugins: {
        '@nx': nxPlugin,
      },
      rules: {
        'vue/multi-word-component-names': 'off',
        // Keep Nx module boundaries checks
        '@nx/enforce-module-boundaries': [
          'error',
          {
            enforceBuildableLibDependency: true,
            allow: [],
            depConstraints: [
              {
                sourceTag: '*',
                onlyDependOnLibsWithTags: ['*'],
              },
            ],
          },
        ],
      },
    },
  ])
)
