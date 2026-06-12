/**
 * routes/report.routes.js
 * PT-05: Rota delgada — chama controller e propaga erros com next(err).
 * AP-08: prefixo /admin removido da URL pública (sem proteção real, gerava falsa sensação de segurança).
 */
const { Router } = require('express');
const reportController = require('../controllers/report.controller');

const router = Router();

/**
 * GET /financial-report
 * Retorna array de { course, revenue, students: [{student, paid}] }.
 */
router.get('/', async (req, res, next) => {
  try {
    const report = await reportController.getFinancialReport();
    res.json(report);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
