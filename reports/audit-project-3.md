================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3 + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Files:   12 analyzed | ~600 lines of code

Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 3

Findings

[CRITICAL] AP-07: Broken or Weak Cryptography
File: models/user.py:29-32
Description: Senhas armazenadas com MD5 (hashlib.md5). MD5 é criptograficamente quebrado e vulnerável a rainbow table attacks. Usado tanto em set_password() (linha 29) quanto em check_password() (linha 32).
Impact: Qualquer atacante com acesso ao banco consegue reverter todas as senhas em segundos usando tabelas pré-computadas. Compliance com OWASP A02:2021 violado.
Recommendation: Substituir hashlib.md5 por hashlib.sha256 como passo imediato; migrar para bcrypt (pip install bcrypt) na iteração seguinte. Aplicar PT-01 do playbook para gestão via variável de ambiente da pepper se necessário.

[CRITICAL] AP-02: Hardcoded Credentials — SECRET_KEY
File: app.py:13
Description: app.config['SECRET_KEY'] = 'super-secret-key-123' está escrita diretamente no código-fonte versionado.
Impact: Qualquer pessoa com acesso ao repositório pode forjar tokens de sessão e assumir identidades de usuários em produção.
Recommendation: Extrair para os.environ.get('SECRET_KEY', 'dev-only-insecure-key') em config/settings.py. Aplicar PT-01.

[CRITICAL] AP-02: Hardcoded Credentials — Email SMTP
File: services/notification_service.py:8-10
Description: Credenciais SMTP hardcoded: email_user = 'taskmanager@gmail.com' e email_password = 'senha123' escritos diretamente no construtor da classe.
Impact: Credenciais de email expostas no repositório. Risco de vazamento de dados, uso indevido da conta e bloqueio pelo provedor.
Recommendation: Mover para variáveis de ambiente: os.environ.get('EMAIL_USER') e os.environ.get('EMAIL_PASSWORD'). Aplicar PT-01.

[HIGH] AP-08: Fake or Missing Authentication
File: routes/user_routes.py:210
Description: Token de autenticação gerado por concatenação de string: 'fake-jwt-token-' + str(user.id). Não há assinatura criptográfica, validação de expiração ou qualquer proteção real.
Impact: Qualquer cliente pode forjar um token para qualquer user_id sem conhecer credenciais. O sistema não oferece proteção de autenticação real.
Recommendation: Substituir por token baseado em secrets.token_hex(32) vinculado à sessão do usuário. Para JWT real, usar PyJWT. Documentar que auth completa está fora do escopo atual. Aplicar padrão PT-01 para SECRET_KEY usada na assinatura.

[HIGH] AP-06: N+1 Query Problem — user_productivity no report
File: routes/report_routes.py:53-68
Description: Loop sobre todos os usuários (User.query.all()) executando Task.query.filter_by(user_id=u.id).all() para cada um — gerando 1 + N queries onde N = número de usuários.
Impact: Performance degrada linearmente com o número de usuários. Com 1.000 usuários, o endpoint /reports/summary executa 1.001 queries em vez de 1.
Recommendation: Substituir pelo padrão PT-04: usar JOIN único com GROUP BY para obter contagem de tarefas por usuário em uma única query. Mover para controller/model dedicado.

[HIGH] AP-05: Business Logic in Route — task_routes duplicação e lógica inline
File: routes/task_routes.py:13-299
Description: Arquivo com 299 linhas concentrando: validações de negócio (status, priority, title length), cálculo de overdue duplicado 3 vezes (linhas 30-39, 71-80, 283-287), queries N+1 para User e Category (linhas 41-57), e múltiplas responsabilidades sem separação de camadas.
Impact: Manutenção difícil — qualquer mudança na regra de overdue exige 3 alterações. Testabilidade zero sem framework HTTP. Violação do princípio Single Responsibility.
Recommendation: Extrair lógica de negócio para controllers/task_controller.py. Extrair cálculo de overdue para função auxiliar. Aplicar PT-03 e PT-04.

[MEDIUM] AP-09: Magic Strings — Status values
File: routes/task_routes.py:110, 177, 277-279 | routes/report_routes.py:19-22, 35-36, 53-67 | models/task.py:39, 53-54 | utils/helpers.py:75
Description: Strings 'pending', 'in_progress', 'done', 'cancelled' espalhadas em pelo menos 8 locais distintos sem enum centralizado. Também presentes em routes/user_routes.py:171.
Impact: Qualquer typo em uma das ocorrências cria um bug silencioso. Renomear um status requer busca manual em todo o código.
Recommendation: Criar models/enums.py com class StatusTarefa(Enum) e class StatusUsuario(Enum). Aplicar PT-07.

[MEDIUM] AP-10: Code Duplication — cálculo de overdue
File: routes/task_routes.py:30-39, 71-80, 283-287 | routes/user_routes.py:171-180 | routes/report_routes.py:33-37, 132-135
Description: O bloco de lógica para calcular se uma tarefa está atrasada (comparar due_date com datetime.utcnow() e verificar status != 'done'/'cancelled') está duplicado em 6 locais distintos.
Impact: Qualquer correção nessa lógica precisa ser aplicada em 6 lugares. Risco alto de inconsistência entre endpoints.
Recommendation: Extrair para método is_overdue() do modelo Task (já existe parcialmente em models/task.py:50-60) e usá-lo consistentemente. Centralizar no controller.

[MEDIUM] AP-12: Deprecated API — datetime.utcnow()
File: models/task.py:15-16 | models/user.py:14 | models/category.py:11 | routes/task_routes.py:31, 72, 215, 285 | routes/report_routes.py:35, 45, 46, 71 | services/notification_service.py:35 | utils/helpers.py:38
Description: datetime.utcnow() está deprecated desde Python 3.12 (PEP 615). Usado em pelo menos 12 locais, incluindo defaults de colunas SQLAlchemy e comparações de data.
Impact: DeprecationWarning em Python 3.12+. Comportamento futuro incerto nas versões seguintes. O método retorna datetime naive sem timezone, causando ambiguidades.
Recommendation: Substituir por datetime.now(timezone.utc) em todo o código. Para defaults SQLAlchemy, usar lambda: datetime.now(timezone.utc). Aplicar PT-10.

[MEDIUM] AP-11: Debug Mode in Production Code
File: app.py:34
Description: app.run(debug=True, host='0.0.0.0', port=5000) — debug=True hardcoded no entry point da aplicação.
Impact: Em produção, debug=True expõe stack traces completos nas respostas HTTP, habilita o Werkzeug debugger interativo (execução de código arbitrário via PIN) e recarrega automaticamente o código.
Recommendation: Substituir por debug=settings.DEBUG onde settings.DEBUG lê os.environ.get('DEBUG', 'false').lower() == 'true'. Aplicar PT-01.

[LOW] AP-13: Print Statements as Logging
File: routes/task_routes.py:149, 153, 219, 234 | routes/user_routes.py:83, 89, 147 | services/notification_service.py:21, 24 | utils/helpers.py:39-40
Description: 10 ocorrências de print() em arquivos de produção (routes e services). Ausência completa de import logging em qualquer arquivo de rota ou serviço.
Impact: Logs não estruturados, sem nível, sem timestamp, sem possibilidade de filtro ou redirecionamento para sistemas de observabilidade.
Recommendation: Substituir todos os print() por logger = logging.getLogger(__name__) com logger.info() / logger.error(). Aplicar PT-06.

[LOW] AP-14: Unused Dependencies
File: requirements.txt:4-6
Description: Três pacotes declarados sem nenhum import no código-fonte: marshmallow==3.20.1 (grep retorna zero ocorrências), requests==2.31.0 (zero ocorrências), python-dotenv==1.0.0 (zero ocorrências de load_dotenv ou dotenv).
Impact: Aumenta a superfície de ataque (mais pacotes = mais CVEs potenciais), torna o ambiente de produção mais pesado e confunde desenvolvedores sobre dependências reais.
Recommendation: Remover marshmallow e requests do requirements.txt. Manter python-dotenv mas utilizá-lo em config/settings.py com load_dotenv() para suporte a arquivo .env em desenvolvimento.

[LOW] AP-15: Missing Pagination
File: routes/task_routes.py:13 (GET /tasks) | routes/user_routes.py:10 (GET /users) | routes/report_routes.py:158 (GET /categories)
Description: Endpoints de listagem retornam todos os registros sem parâmetros limit/offset/page: Task.query.all(), User.query.all(), Category.query.all().
Impact: Com crescimento de dados, endpoints retornam payloads gigantescos, aumentando latência e consumo de memória. Risco de timeout e OOM em produção.
Recommendation: Adicionar parâmetros opcionais page (default=1) e per_page (default=20) usando .paginate() do Flask-SQLAlchemy nos endpoints de listagem.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
