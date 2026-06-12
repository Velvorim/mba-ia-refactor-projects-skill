/**
 * models/course.model.js
 * PT-03: Acesso a dados exclusivo de courses e enrollments.
 * Sem lógica de negócio, sem HTTP.
 */
const { dbGet, dbAll, dbRun } = require('../database');

/** Retorna um curso ativo pelo id. */
async function findActiveById(id) {
  return dbGet('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
}

/**
 * PT-04: Retorna todos os cursos com suas matrículas, usuários e pagamentos
 * em uma única query JOIN — elimina o N+1 do financial report.
 */
async function findAllWithEnrollments() {
  return dbAll(`
    SELECT
      c.id          AS course_id,
      c.title       AS course_title,
      e.id          AS enrollment_id,
      u.name        AS student_name,
      p.amount      AS payment_amount,
      p.status      AS payment_status
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    LEFT JOIN users       u ON u.id = e.user_id
    LEFT JOIN payments    p ON p.enrollment_id = e.id
    ORDER BY c.id
  `);
}

/** Insere uma nova matrícula; retorna o id gerado. */
async function createEnrollment(userId, courseId) {
  const result = await dbRun(
    'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
    [userId, courseId]
  );
  return result.lastID;
}

module.exports = { findActiveById, findAllWithEnrollments, createEnrollment };
