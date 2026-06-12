/**
 * middlewares/errorHandler.js
 * PT-05: Error handling centralizado — substitui os res.status(500).send() inline de AppManager.js.
 * PT-06: Usa logger estruturado.
 */
const logger = require('../utils/logger');

/**
 * Express error middleware — 4 parâmetros obrigatórios.
 * Registrado APÓS todas as rotas no app.js.
 */
// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
  const status = err.status || 500;

  if (status >= 500) {
    logger.error('Unhandled error', { message: err.message, stack: err.stack });
  }

  res.status(status).json({ error: err.message || 'Internal server error' });
}

module.exports = errorHandler;
