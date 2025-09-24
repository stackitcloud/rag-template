// Bridge file for tooling that expects eslint.config.js.
// Use CommonJS to avoid requiring package.json { type: 'module' } in Node/vite contexts.
module.exports = require('./eslint.config.mjs').default
