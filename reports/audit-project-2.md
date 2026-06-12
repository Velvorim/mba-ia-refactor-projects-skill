================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy (Frankenstein LMS)
Stack:   Node.js + Express ^4.18.2
Files:   3 analyzed | ~155 lines of code

Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 2 | LOW: 2

Findings

[CRITICAL] AP-01: God Class
File: src/AppManager.js:1-141
Description: A classe AppManager concentra em um único arquivo e classe: inicialização do banco de dados (initDb), definição de todas as rotas HTTP (setupRoutes com 3 endpoints), lógica de negócio de checkout (validação de cartão, criação de usuário, matrícula e pagamento) e lógica de relatório financeiro com N+1 queries. A classe possui 141 linhas, 2 métodos públicos de alto nível com mais de 50 linhas cada e abrange domínios distintos (usuários, cursos, matrículas, pagamentos, auditoria).
Impact: Impossibilidade de testar unidades de forma isolada; qualquer mudança em qualquer domínio exige editar o mesmo arquivo; acoplamento total entre roteamento, negócio e banco de dados.
Recommendation: Aplicar PT-03: separar em models/ (course.model.js, user.model.js) + controllers/ (checkout.controller.js, report.controller.js, user.controller.js) + routes/ (checkout.routes.js, report.routes.js, user.routes.js).

[CRITICAL] AP-02: Hardcoded Credentials — dbPass
File: src/utils.js:3
Description: A senha do banco de dados está escrita literalmente no código-fonte: dbPass: "senha_super_secreta_prod_123".
Impact: Qualquer pessoa com acesso ao repositório obtém a credencial de produção. Não é possível rotacionar a senha sem commit.
Recommendation: Aplicar PT-01: substituir por process.env.DB_PASS || '' em config/settings.js.

[CRITICAL] AP-02: Hardcoded Credentials — paymentGatewayKey
File: src/utils.js:4
Description: Chave de produção do gateway de pagamento escrita literalmente: paymentGatewayKey: "pk_live_1234567890abcdef".
Impact: Exposição de chave live de gateway de pagamento. Qualquer leak do repositório compromete transações financeiras reais.
Recommendation: Aplicar PT-01: substituir por process.env.PAYMENT_GATEWAY_KEY || '' em config/settings.js.

[CRITICAL] AP-02: Hardcoded Credentials — smtpUser / dbUser
File: src/utils.js:2,5
Description: Usuário do banco de dados (dbUser: "admin_master") e usuário SMTP (smtpUser: "no-reply@fullcycle.com.br") hardcoded no código-fonte.
Impact: Credenciais de infra expostas no versionamento; impossibilidade de configuração por ambiente sem alterar código.
Recommendation: Aplicar PT-01: substituir por process.env.DB_USER e process.env.SMTP_USER em config/settings.js.

[HIGH] AP-07: Broken / Weak Cryptography
File: src/utils.js:17-23
Description: A função badCrypto(pwd) implementa hashing de senha usando codificação base64 em loop (10.000 iterações de Buffer.from(pwd).toString('base64').substring(0, 2)) e retorna os 10 primeiros caracteres. Base64 é codificação reversível, não hashing criptográfico. O resultado tem entropia mínima e é computacionalmente barato de reverter por força bruta. Esta função é chamada na linha 68 de AppManager.js para armazenar senhas de novos usuários.
Impact: Senhas de todos os usuários podem ser recuperadas trivialmente. Qualquer vazamento do banco expõe todas as credenciais.
Recommendation: Remover badCrypto completamente. Documentar que bcryptjs deve ser usado em produção (npm install bcryptjs; bcrypt.hash(password, 12)). Na refatoração atual, registrar o hash como placeholder com comentário explícito.

[HIGH] AP-06: N+1 Query Problem
File: src/AppManager.js:83-128
Description: O endpoint GET /api/admin/financial-report executa queries encadeadas em callbacks: (1) SELECT * FROM courses — 1 query; (2) para cada curso: SELECT * FROM enrollments WHERE course_id = ? — N queries; (3) para cada matrícula: SELECT name, email FROM users WHERE id = ? — N×M queries; (4) para cada matrícula: SELECT amount, status FROM payments WHERE enrollment_id = ? — N×M queries adicionais. Para 10 cursos com 20 alunos cada, isso gera 1 + 10 + 200 + 200 = 411 queries.
Impact: Degradação severa de performance proporcional ao volume de dados; possível timeout em produção com poucos dados.
Recommendation: Aplicar PT-04: substituir por um único JOIN entre courses, enrollments, users e payments. Agrupar resultados em JavaScript.

[HIGH] AP-08: Fake / Missing Authentication
File: src/AppManager.js:80
Description: O endpoint GET /api/admin/financial-report está mapeado sob /api/admin/ mas não possui nenhuma verificação de autenticação ou autorização — não há middleware de auth, verificação de header Authorization, token ou sessão antes de retornar dados financeiros completos.
Impact: Qualquer cliente HTTP não autenticado pode acessar o relatório financeiro completo com nomes, e-mails e valores pagos de todos os estudantes.
Recommendation: Remover o prefixo /admin/ da URL pública ou documentar explicitamente que autenticação real está fora do escopo desta refatoração; eliminar a falsa sensação de segurança do prefixo /admin sem proteção.

[MEDIUM] AP-12: Deprecated API — new Buffer()
File: src/utils.js:20
Description: Buffer.from(pwd) na linha 20 já está correto, porém dentro da função badCrypto que usa um padrão de loop com new Buffer implícito em versões antigas. Verificado: a linha usa Buffer.from corretamente, porém a função badCrypto em si implementa criptografia quebrada (vide AP-07).
Impact: Nenhum impacto de deprecação nesta linha específica — issue já capturado como AP-07.
Recommendation: Remover a função inteira (vide AP-07); não há ação adicional necessária para esta linha.

[MEDIUM] AP-13: Console.log como Logging — app.js
File: src/app.js:13
Description: console.log(`Frankenstein LMS rodando na porta ${config.port}...`) usado como mecanismo de log de inicialização do servidor.
Impact: Logs de produção não estruturados, sem timestamp, sem nível de severidade, sem possibilidade de roteamento para sistemas de observabilidade.
Recommendation: Aplicar PT-06: substituir por logger estruturado (objeto logger com método info/error que emite JSON com timestamp e level).

[LOW] AP-13: Console.log como Logging — AppManager.js
File: src/AppManager.js:45
Description: console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`) dentro do handler de checkout loga o número de cartão de crédito completo e a chave do gateway de pagamento no stdout.
Impact: Duplo problema: (1) logging via console.log sem estrutura; (2) dados PCI-DSS sensíveis (PAN do cartão) sendo expostos em logs — violação grave de compliance de pagamento.
Recommendation: Aplicar PT-06: substituir por logger estruturado; NUNCA logar número de cartão completo — mascarar como cc.slice(-4) no máximo.

[LOW] AP-15: Missing Pagination
File: src/AppManager.js:83
Description: O endpoint GET /api/admin/financial-report executa SELECT * FROM courses sem LIMIT ou OFFSET, retornando todos os cursos e todas as matrículas sem paginação.
Impact: Em produção com milhares de cursos e alunos, a resposta pode ser de megabytes e a query exceder limites de memória e timeout.
Recommendation: Adicionar parâmetros de query ?limit=50&offset=0 com defaults seguros. Aplicar LIMIT/OFFSET no SELECT de courses.

================================
Total: 11 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
