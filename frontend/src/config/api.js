// Backend base URL. quasar.config.js defines API_BASE_URL at build time; the
// container entrypoint rewrites it at start. '/backend' is the nginx proxy path.
export const API_BASE_URL = process.env.API_BASE_URL || '/backend'

export default API_BASE_URL
