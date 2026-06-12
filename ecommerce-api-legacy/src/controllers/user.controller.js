/**
 * controllers/user.controller.js
 * PT-03: Lógica de deleção de usuário isolada.
 * PT-08: async/await.
 */
const userModel = require('../models/user.model');

/**
 * Remove um usuário pelo id.
 * Nota: as matrículas e pagamentos associados permanecem no banco
 * (comportamento idêntico ao original — limpeza de dados órfãos
 * deve ser implementada via CASCADE ou job de manutenção).
 * @param {string|number} id
 * @returns {object} { msg }
 */
async function deleteUser(id) {
  await userModel.removeById(id);
  return { msg: 'Usuário deletado. Atenção: matrículas e pagamentos associados permanecem no banco.' };
}

module.exports = { deleteUser };
