// Bridge file so tools that look specifically for eslint.config.js can load the flat config.
// Re-export the existing ESM flat config from eslint.config.mjs
import config from './eslint.config.mjs'
export default config
