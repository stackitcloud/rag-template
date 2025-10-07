// Flat ESLint config for Vue 3 + TypeScript (ESLint 9)
// Minimal explicit setup to ensure proper parsers for TS and Vue.

import js from '@eslint/js'
import nxPlugin from '@nx/eslint-plugin'
import tsPlugin from '@typescript-eslint/eslint-plugin'
import tsParser from '@typescript-eslint/parser'
import vuePlugin from 'eslint-plugin-vue'
import globals from 'globals'
import vueParser from 'vue-eslint-parser'

export default [
  // Global ignores
  {
    name: 'ignores',
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/coverage/**',
      '**/.output/**',
      '**/.cache/**',
      '**/.vite/**',
      '**/.nx/**',
    ],
  },

  // Global language options
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.es2024,
      },
    },
  },

  // Base JS recommended
  js.configs.recommended,

  // TS/JS files
  {
    files: ['**/*.{ts,tsx,js,cjs,mjs,mts,cts}', '**/*.d.ts'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    plugins: { '@typescript-eslint': tsPlugin, '@nx': nxPlugin },
    rules: {
      // Prefer TS rule over base rule
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
      'no-undef': 'off',
      // Nx module boundaries
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

  // Vue SFCs
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tsParser,
        ecmaVersion: 'latest',
        sourceType: 'module',
        extraFileExtensions: ['.vue'],
      },
    },
    plugins: { vue: vuePlugin, '@typescript-eslint': tsPlugin },
    rules: {
      // Include Vue 3 recommended set to get correct SFC behavior
      ...(vuePlugin.configs['vue3-recommended']?.rules ?? {}),
      'vue/multi-word-component-names': 'off',
      // Prefer TS rule for script blocks inside SFCs
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
    },
  },
]
