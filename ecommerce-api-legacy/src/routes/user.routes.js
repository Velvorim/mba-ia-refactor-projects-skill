/**
 * routes/user.routes.js
 * PT-05: Rota delgada — chama controller e propaga erros com next(err).
 */
const { Router } = require('express');
const userController = require('../controllers/user.controller');

const router = Router();

/**
 * DELETE /users/:id
 */
router.delete('/:id', async (req, res, next) => {
  try {
    const result = await userController.deleteUser(req.params.id);
    res.json(result);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
