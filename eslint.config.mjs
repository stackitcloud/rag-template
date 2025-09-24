// Root ESLint flat config
// Delegate to the frontend flat config by re-exporting it directly so Nx (running from repo root)
// picks up the correct Vue + TypeScript parsers and rules.
import frontendConfig from './services/frontend/eslint.config.mjs'

export default frontendConfig
