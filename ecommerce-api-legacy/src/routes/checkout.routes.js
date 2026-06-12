/**
 * routes/checkout.routes.js
 * PT-05: Rota delgada — valida input, chama controller, propaga erros com next(err).
 */
const { Router } = require('express');
const checkoutController = require('../controllers/checkout.controller');

const router = Router();

/**
 * POST /checkout
 * Body: { userId, courseId, cc }  — mantém contrato original da API
 */
router.post('/', async (req, res, next) => {
  try {
    const result = await checkoutController.processCheckout({
      userId:     req.body.userId,
      courseId:   req.body.courseId,
      cardNumber: req.body.cc,
    });
    res.status(200).json(result);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
