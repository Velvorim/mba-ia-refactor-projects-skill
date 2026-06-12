/**
 * controllers/report.controller.js
 * PT-03: Lógica de relatório financeiro isolada da rota.
 * PT-04: N+1 eliminado — agora usa JOIN único via courseModel.findAllWithEnrollments().
 * PT-08: async/await.
 */
const courseModel = require('../models/course.model');

/**
 * Gera o relatório financeiro agrupando cursos e alunos.
 * @returns {Array} Lista de { course, revenue, students: [{student, paid}] }
 */
async function getFinancialReport() {
  // PT-04: uma única query JOIN substitui as N+1 queries aninhadas
  const rows = await courseModel.findAllWithEnrollments();

  // Agregar resultados em memória
  const coursesMap = {};

  for (const row of rows) {
    if (!coursesMap[row.course_id]) {
      coursesMap[row.course_id] = {
        course:   row.course_title,
        revenue:  0,
        students: [],
      };
    }

    if (row.enrollment_id) {
      const paid = row.payment_status === 'PAID' ? (row.payment_amount || 0) : 0;
      coursesMap[row.course_id].revenue += paid;
      coursesMap[row.course_id].students.push({
        student: row.student_name || 'Unknown',
        paid:    row.payment_amount || 0,
      });
    }
  }

  return Object.values(coursesMap);
}

module.exports = { getFinancialReport };
