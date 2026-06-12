/**
 * app.js — Composition Root
 * PT-03: Apenas registra rotas, middlewares e inicializa o banco.
 * PT-05: Error handler centralizado registrado por último.
 * PT-06: Logger estruturado substitui console.log de startup.
 * PT-10: Sem APIs deprecated (Buffer.from já correto, res.status(N).json() nas rotas).
 *
 * Endpoints mantidos (contrato original preservado):
 *   POST   /checkout
 *   GET    /financial-report
 *   DELETE /users/:id
 */
const express      = require('express');
const settings     = require('./config/settings');
const { initDb }   = require('./database/init');
const logger       = require('./utils/logger');
const errorHandler = require('./middlewares/errorHandler');

const checkoutRoutes = require('./routes/checkout.routes');
const reportRoutes   = require('./routes/report.routes');
const userRoutes     = require('./routes/user.routes');

const app = express();
app.use(express.json());

// Registrar rotas — mantendo os mesmos prefixos do contrato original
app.use('/checkout',         checkoutRoutes);    // POST   /checkout
app.use('/financial-report', reportRoutes);      // GET    /financial-report
app.use('/users',            userRoutes);        // DELETE /users/:id

// PT-05: error handler centralizado — DEVE ser o último middleware
app.use(errorHandler);

// Inicializar banco e subir servidor
initDb()
  .then(() => {
    app.listen(settings.port, () => {
      // PT-06: logger estruturado em vez de console.log
      logger.info('Servidor iniciado', { port: settings.port });
    });
  })
  .catch((err) => {
    logger.error('Falha ao inicializar banco de dados', { message: err.message });
    process.exit(1);
  });

module.exports = app;
