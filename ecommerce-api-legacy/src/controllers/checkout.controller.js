/**
 * controllers/checkout.controller.js
 * PT-03: Lógica de negócio de checkout separada da rota e do model.
 * PT-08: async/await em vez de callbacks aninhados.
 * PT-06: logger estruturado em vez de console.log.
 */
const courseModel = require('../models/course.model');
const userModel   = require('../models/user.model');
const { dbRun }   = require('../database');
const settings    = require('../config/settings');
const logger      = require('../utils/logger');

/**
 * Processa o checkout de um curso.
 * @param {object} data - { name, email, password, courseId, cardNumber }
 * @returns {object} { msg, enrollment_id }
 * @throws {Error} com .status 400/404 para erros de negócio
 */
async function processCheckout({ userId, courseId, cardNumber }) {
  // Validação de entrada — mantém contrato original: userId, courseId, cc (mapeado para cardNumber)
  if (!userId || !courseId || !cardNumber) {
    const err = new Error('Bad Request: userId, courseId e cc são obrigatórios');
    err.status = 400;
    throw err;
  }

  // Verificar se curso existe e está ativo
  const course = await courseModel.findActiveById(courseId);
  if (!course) {
    const err = new Error('Curso não encontrado');
    err.status = 404;
    throw err;
  }

  // Verificar se usuário existe
  const user = await userModel.findById(userId);
  if (!user) {
    const err = new Error('Usuário não encontrado');
    err.status = 404;
    throw err;
  }

  // Simular gateway de pagamento
  // AP-08 note: autenticação real está fora do escopo desta refatoração
  // PT-06: logar apenas os últimos 4 dígitos do cartão — nunca o PAN completo (compliance PCI-DSS)
  logger.info('Processando pagamento', {
    cardLastFour: cardNumber.slice(-4),
    gatewayConfigured: !!settings.paymentGatewayKey,
  });

  const paymentStatus = cardNumber.startsWith('4') ? 'PAID' : 'DENIED';

  if (paymentStatus === 'DENIED') {
    const err = new Error('Pagamento recusado');
    err.status = 400;
    throw err;
  }

  // Criar matrícula
  const enrollmentId = await courseModel.createEnrollment(user.id, courseId);

  // Registrar pagamento
  await userModel.createPayment(enrollmentId, course.price, paymentStatus);

  // Registrar auditoria
  await dbRun(
    "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
    [`Checkout curso ${courseId} por usuário ${user.id}`]
  );

  logger.info('Checkout concluído', { userId: user.id, courseId, enrollmentId, courseTitle: course.title });

  return { msg: 'Sucesso', enrollment_id: enrollmentId };
}

module.exports = { processCheckout };
