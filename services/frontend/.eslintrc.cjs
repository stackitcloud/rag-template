/* Classic ESLint config for Nx executor compatibility (ESLint 8/9)
 * Mirrors the flat config to ensure proper parsing of TS and Vue files
 */

module.exports = {
  root: true,
  ignorePatterns: ['dist', 'coverage', 'node_modules'],
  overrides: [
    // TypeScript & JavaScript files
    {
      files: ['**/*.{ts,tsx,js,cjs,mjs,mts,cts}'],
      parser: '@typescript-eslint/parser',
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        project: null,
        tsconfigRootDir: __dirname,
      },
      plugins: ['@typescript-eslint', '@nx'],
      extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
      rules: {
        'no-undef': 'off',
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

    // Vue Single File Components
    {
      files: ['**/*.vue'],
      parser: 'vue-eslint-parser',
      parserOptions: {
        parser: '@typescript-eslint/parser',
        ecmaVersion: 'latest',
        sourceType: 'module',
        extraFileExtensions: ['.vue'],
      },
      plugins: ['vue', '@typescript-eslint'],
      extends: ['plugin:vue/vue3-recommended', 'plugin:@typescript-eslint/recommended'],
      rules: {
        'vue/multi-word-component-names': 'off',
      },
      env: {
        'vue/setup-compiler-macros': true,
      },
    },

    // Declaration files
    {
      files: ['**/*.d.ts'],
      parser: '@typescript-eslint/parser',
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
      rules: {},
    },
  ],
}
