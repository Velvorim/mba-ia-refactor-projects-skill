/**
 * config/settings.js
 * PT-01: Todas as credenciais e configurações via process.env com defaults seguros.
 * NUNCA hardcode secrets aqui — use variáveis de ambiente em produção.
 */
module.exports = {
  // Banco de dados
  dbPath:   process.env.DB_PATH  || ':memory:',
  dbUser:   process.env.DB_USER  || '',
  dbPass:   process.env.DB_PASS  || '',

  // Gateway de pagamento
  // PT-01: chave de API movida de utils.js linha 4 para variável de ambiente
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',

  // SMTP
  smtpUser: process.env.SMTP_USER || '',

  // Servidor
  port: parseInt(process.env.PORT || '3000', 10),
};
