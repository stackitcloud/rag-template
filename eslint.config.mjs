// Root ESLint flat config delegating to services/frontend
// Ensures Nx executions from repo root pick up the frontend flat config.
import { defineConfig } from 'eslint/config'
import frontendConfig from './services/frontend/eslint.config.mjs'

export default defineConfig([
  {
    name: 'frontend/delegate',
    basePath: 'services/frontend',
    extends: frontendConfig,
  },
])
