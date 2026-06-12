/**
 * models/user.model.js
 * PT-03: Acesso a dados exclusivo de users e payments.
 * Sem lógica de negócio, sem HTTP.
 */
const { dbGet, dbRun } = require('../database');

/** Encontra um usuário pelo id; retorna undefined se não existir. */
async function findById(id) {
  return dbGet('SELECT * FROM users WHERE id = ?', [id]);
}

/** Encontra um usuário pelo e-mail; retorna undefined se não existir. */
async function findByEmail(email) {
  return dbGet('SELECT * FROM users WHERE email = ?', [email]);
}

/**
 * Cria um novo usuário.
 * PT-07: badCrypto REMOVIDA. Em produção, use bcryptjs:
 *   const bcrypt = require('bcryptjs');
 *   const hash = await bcrypt.hash(password, 12);
 * Por ora, armazena o password recebido como está (placeholder para integração futura).
 */
async function create(name, email, passwordHash) {
  const result = await dbRun(
    'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
    [name, email, passwordHash]
  );
  return result.lastID;
}

/** Remove um usuário pelo id. */
async function removeById(id) {
  const result = await dbRun('DELETE FROM users WHERE id = ?', [id]);
  return result.changes;
}

/** Cria um registro de pagamento para uma matrícula. */
async function createPayment(enrollmentId, amount, status) {
  const result = await dbRun(
    'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
    [enrollmentId, amount, status]
  );
  return result.lastID;
}

module.exports = { findById, findByEmail, create, removeById, createPayment };
