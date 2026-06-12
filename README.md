# MBA IA — Skill de Auditoria e Refatoração Arquitetural

Skill `/refactor-arch` para Claude Code que automatiza análise, auditoria e refatoração de projetos legados para o padrão MVC, agnóstica de tecnologia.

---

## A) Análise Manual

### Projeto 1 — code-smells-project (Python/Flask — E-commerce)

| Severidade | Arquivo | Linha | Problema | Justificativa |
|-----------|---------|-------|----------|---------------|
| CRITICAL | `models.py` | 1–315 | **God Class** — queries SQL, validação, lógica de negócio e 4 domínios no mesmo arquivo | Impossível testar em isolamento; qualquer mudança afeta todos os domínios; viola SRP completamente |
| CRITICAL | `app.py` | 8 | **Hardcoded SECRET_KEY** — `"minha-chave-super-secreta-123"` no código | Qualquer acesso ao repositório permite forjar sessões Flask; o atacante pode assinar cookies |
| CRITICAL | `models.py` | 28, 48–49, 92, 109 | **SQL Injection** — concatenação de strings em queries: `"SELECT * FROM produtos WHERE id = " + str(id)` | Permite extração completa do banco, deleção de dados e escalada de privilégios |
| CRITICAL | `app.py` | 62–70 | **Admin Endpoint sem auth** — `/admin/query` executa qualquer SQL recebido via POST sem autenticação | Qualquer cliente HTTP pode deletar tabelas, ler credenciais ou corromper dados |
| HIGH | `models.py` | 171–201 | **N+1 Query** — loop `for pedido in pedidos` executa query separada por item e por produto | Com 100 pedidos × 5 itens = 501 queries por request; degrada exponencialmente |
| HIGH | `database.py` | 76 | **Senha em texto puro** no seed — `("Admin", "admin@loja.com", "admin123", "admin")` | Compromete credenciais de administrador em qualquer vazamento do banco |
| MEDIUM | `app.py` | 8 | **Debug mode em produção** — `app.config["DEBUG"] = True` | Expõe stack traces completos com variáveis locais ao usuário final |
| MEDIUM | `controllers.py` | 287–289 | **Health check expõe secrets** — retorna `db_path` e `secret_key` no JSON | Information disclosure — facilita ataque direcionado |
| LOW | `models.py` | múltiplos | **Print como logging** — 18+ chamadas `print()` em código de produção | Sem nível de severidade, sem timestamp, não pode ser desabilitado sem alterar código |
| LOW | `models.py` | múltiplos | **Magic strings** — `'pendente'`, `'aprovado'`, `'enviado'` espalhados | Typo silencioso quebra fluxo de negócio; difícil refatorar |

---

### Projeto 2 — ecommerce-api-legacy (Node.js/Express — LMS)

| Severidade | Arquivo | Linha | Problema | Justificativa |
|-----------|---------|-------|----------|---------------|
| CRITICAL | `src/AppManager.js` | 1–141 | **God Class** — init de banco, 3 endpoints, checkout, relatório e auditoria em 141 linhas | Acoplamento total: não dá para testar checkout sem subir o banco inteiro e as rotas |
| CRITICAL | `src/utils.js` | 2–5 | **Hardcoded Credentials** — `dbPass`, `paymentGatewayKey` (chave live!), `smtpUser` literais | Chave de gateway de pagamento de produção exposta no repositório — risco financeiro imediato |
| HIGH | `src/utils.js` | 17–23 | **Broken Crypto (badCrypto)** — base64 em loop 10.000× truncado para 10 chars | Base64 é reversível; o resultado tem entropia de ~72 bits comprimidos para 10 chars — senhas recuperáveis |
| HIGH | `src/AppManager.js` | 83–128 | **N+1 Query em callbacks aninhados** — para cada course, para cada enrollment, query de user + payment | 2 cursos × 50 matrículas = 201 queries por request de relatório |
| HIGH | `src/AppManager.js` | 80 | **Admin endpoint sem auth** — `GET /api/admin/financial-report` sem middleware de autenticação | PII e dados financeiros de todos os alunos acessíveis sem credenciais |
| MEDIUM | `src/utils.js` | 9–10 | **Global mutable state** — `let globalCache = {}` e `let totalRevenue = 0` exportados | Side effects invisíveis entre requests; bugs de concorrência difíceis de rastrear |
| MEDIUM | `src/AppManager.js` | 45 | **Log de PAN (cartão)** — `console.log` com número completo do cartão | Violação de PCI-DSS; dados do portador do cartão em logs = auditoria de segurança reprovada |
| LOW | `src/AppManager.js` | 135 | **Data integrity** — deleção de user deixa enrollments e payments órfãos | O próprio código comenta a inconsistência; estados órfãos corrompem relatórios futuros |

---

### Projeto 3 — task-manager-api (Python/Flask — Task Manager)

| Severidade | Arquivo | Linha | Problema | Justificativa |
|-----------|---------|-------|----------|---------------|
| CRITICAL | `models/user.py` | 29–32 | **MD5 para senhas** — `hashlib.md5(pwd.encode()).hexdigest()` | MD5 é quebrado; rainbow tables online cobrem senhas comuns em milissegundos |
| CRITICAL | `app.py` | 13 | **Hardcoded SECRET_KEY** — `'super-secret-key-123'` | Forja de sessões possível para qualquer pessoa com acesso ao código |
| CRITICAL | `services/notification_service.py` | 8–10 | **Hardcoded SMTP credentials** — `'taskmanager@gmail.com'` + `'senha123'` | Credenciais de email em repositório público: conta comprometida imediatamente |
| HIGH | `routes/user_routes.py` | 210 | **Fake JWT** — `'fake-jwt-token-' + str(user.id)` | Token sem assinatura; qualquer usuário pode forjar token de admin concatenando o ID correto |
| HIGH | `routes/report_routes.py` | 53–68 | **N+1 Query** — `User.query.all()` + `Task.query.filter_by(assigned_to=u.id)` em loop | 100 usuários = 101 queries no report; SQLAlchemy já tem `joinedload` disponível |
| MEDIUM | `models/task.py` | 52 | **datetime.utcnow() deprecated** — 12+ ocorrências em todo o projeto | Deprecated no Python 3.12; lança DeprecationWarning; comportamento undefined em futuros releases |
| MEDIUM | `routes/task_routes.py` | 30–39, 71–80, 172–180 | **Duplicação do cálculo de overdue** — mesmo bloco de 8 linhas copiado 3+ vezes | Inconsistências silenciosas: basta uma cópia divergir para o status reportado ser incorreto |
| LOW | `requirements.txt` | — | **Unused dependencies** — `marshmallow`, `requests` listados sem nenhum import no código | Aumenta superfície de ataque e tempo de instalação; confunde leitores sobre o que o projeto usa |

---

## B) Construção da Skill

### Estrutura de arquivos

A skill foi dividida em 6 arquivos para respeitar separação de responsabilidades:

```
.claude/skills/refactor-arch/
├── SKILL.md                       # Prompt de instrução (o "como fazer" em 3 fases)
├── project-analysis.md            # Heurísticas de detecção de stack e arquitetura
├── antipatterns-catalog.md        # 15 anti-patterns com sinais de detecção e severidade
├── audit-report-template.md       # Formato obrigatório do relatório de auditoria
├── mvc-architecture-guidelines.md # Estrutura-alvo MVC por tecnologia
└── refactoring-playbook.md        # 10 padrões com código antes/depois
```

**Por que separar em múltiplos arquivos?** O SKILL.md instrui o *processo*; os arquivos de referência fornecem o *conhecimento de domínio*. Isso permite atualizar o catálogo de anti-patterns sem tocar no fluxo, e vice-versa.

### Anti-patterns escolhidos

O catálogo contém 15 anti-patterns em 4 severidades:

- **CRITICAL (4):** God Class, Hardcoded Credentials, SQL Injection, Unprotected Admin Endpoints — falhas exploráveis imediatamente
- **HIGH (4):** Business Logic in Controller, N+1 Query, Broken/Weak Crypto, Fake Authentication — risco grave que requer atacante mais sofisticado
- **MEDIUM (4):** Magic Strings, Code Duplication, Debug Mode, Deprecated API — debt técnico e risco de bug silencioso
- **LOW (3):** Print as Logging, Unused Dependencies, Missing Pagination — degradação de qualidade operacional

**Por que incluir APIs deprecated (AP-12)?** Projetos Python com Flask acumulam `datetime.utcnow()` que quebra no Python 3.12+. Detectar proativamente evita falhas silenciosas em produção.

### Como a agnóstica de tecnologia foi garantida

1. **`project-analysis.md` com heurísticas por extensão e import** — a Fase 1 detecta linguagem por extensão de arquivo e framework por grep de imports; não assume nada antes de ler o código.
2. **`mvc-architecture-guidelines.md` com templates por tecnologia** — a Fase 3 seleciona o template correto (Python/Flask vs Node.js/Express) com base no resultado da Fase 1.
3. **`refactoring-playbook.md` com exemplos bilíngues** — cada padrão tem versão Python e Node.js onde aplicável (PT-06 Logger, PT-08 Async, PT-10 Deprecated API).

### Desafios encontrados

1. **Interface da API original:** O agente refatorou o checkout de `{userId, courseId, cc}` para `{name, email, courseId, cardNumber}`. Foi necessária correção manual — o SKILL.md especifica preservar response shapes mas não mencionava request bodies explicitamente. Corrigido adicionando instrução sobre contrato de request.

2. **N+1 em SQLAlchemy vs SQLite puro:** Projeto 1 usa sqlite3 raw (JOIN manual necessário), Projeto 3 usa SQLAlchemy (backref suficiente). A skill adaptou a estratégia para cada ORM — documentado no PT-04 com dois exemplos de código.

3. **Criptografia incremental:** A skill substitui md5/badCrypto por SHA-256 como passo imediato documentando a migração para bcrypt, sem instalá-lo automaticamente (evita quebra de ambientes sem build tools).

---

## C) Resultados

### Comparação antes/depois

| Projeto | LOC antes | Arquivos antes | Arquivos depois | Findings | CRITICAL resolvidos | App funciona? |
|---------|-----------|----------------|-----------------|----------|---------------------|---------------|
| code-smells-project | ~485 | 4 | 18 | 14 | 4/4 ✓ | ✓ |
| ecommerce-api-legacy | ~185 | 3 | 16 | 11 | 4/4 ✓ | ✓ |
| task-manager-api | ~600 | 12 | 24 | 13 | 3/3 ✓ | ✓ |

### Checklist de validação

#### Fase 1 — Análise

| Critério | Proj 1 | Proj 2 | Proj 3 |
|---------|--------|--------|--------|
| Linguagem detectada corretamente | ✓ Python | ✓ Node.js | ✓ Python |
| Framework detectado corretamente | ✓ Flask 3.1.1 | ✓ Express 4.18.2 | ✓ Flask 3.0.0 |
| Domínio da aplicação descrito | ✓ E-commerce | ✓ LMS | ✓ Task Manager |
| Número de arquivos condiz | ✓ 4 files | ✓ 3 files | ✓ 12 files |

#### Fase 2 — Auditoria

| Critério | Proj 1 | Proj 2 | Proj 3 |
|---------|--------|--------|--------|
| Relatório segue o template | ✓ | ✓ | ✓ |
| Cada finding tem arquivo:linha | ✓ | ✓ | ✓ |
| Findings ordenados por severidade | ✓ | ✓ | ✓ |
| Mínimo 5 findings | ✓ 14 | ✓ 11 | ✓ 13 |
| Detecção de APIs deprecated | N/A | N/A | ✓ AP-12 detectado |
| Pausa antes da Fase 3 | ✓ | ✓ | ✓ |

#### Fase 3 — Refatoração

| Critério | Proj 1 | Proj 2 | Proj 3 |
|---------|--------|--------|--------|
| Estrutura MVC criada | ✓ | ✓ | ✓ |
| Config sem hardcoded | ✓ os.environ | ✓ process.env | ✓ os.environ |
| Models para dados | ✓ | ✓ | ✓ |
| Controllers com lógica | ✓ | ✓ | ✓ |
| Views/Routes separadas | ✓ | ✓ | ✓ |
| Error handling centralizado | ✓ | ✓ | ✓ |
| Entry point claro | ✓ create_app() | ✓ app.js | ✓ create_app() |
| App inicia sem erros | ✓ | ✓ | ✓ |
| Endpoints originais respondem | ✓ /health /produtos | ✓ /checkout /financial-report /users/:id | ✓ /tasks /users /reports/summary |

### Logs de validação

**Projeto 1 (Python/Flask):**
```
✓ All 18 Python files pass syntax check
✓ /health responded: 200
✓ /produtos responded: 200
```

**Projeto 2 (Node.js/Express):**
```
✓ All 16 JS files pass syntax check
✓ GET /financial-report: 200
✓ POST /checkout: 200
✓ DELETE /users/1: 200
```

**Projeto 3 (Python/Flask):**
```
✓ All 24 Python files pass syntax check
✓ GET /tasks: 200
✓ GET /users: 200
✓ GET /reports/summary: 200
```

---

## D) Como Executar

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- pip e npm
- Claude Code CLI (`npm install -g @anthropic-ai/claude-code`)

### Projeto 1 — code-smells-project (Python/Flask)

```bash
cd code-smells-project
pip install -r requirements.txt
claude "/refactor-arch"

# Validar após refatoração
python src/app.py &
curl http://localhost:5000/health
curl http://localhost:5000/produtos
```

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

```bash
cd ecommerce-api-legacy
npm install
claude "/refactor-arch"

# Validar após refatoração
node src/app.js &
curl http://localhost:3000/financial-report
curl -X POST http://localhost:3000/checkout \
  -H "Content-Type: application/json" \
  -d '{"userId":1,"courseId":1,"cc":"4111111111111111"}'
curl -X DELETE http://localhost:3000/users/1
```

### Projeto 3 — task-manager-api (Python/Flask)

```bash
cd task-manager-api
pip install -r requirements.txt
python seed.py
claude "/refactor-arch"

# Validar após refatoração
python app.py &
curl http://localhost:5000/tasks
curl http://localhost:5000/users
curl http://localhost:5000/reports/summary
```

### Variáveis de ambiente disponíveis (pós-refatoração)

| Variável | Projetos | Default (dev) |
|----------|----------|---------------|
| `SECRET_KEY` | 1, 3 | `dev-only-change-in-prod` |
| `DEBUG` | 1, 3 | `false` |
| `DATABASE_PATH` | 1 | `database.db` |
| `ADMIN_TOKEN` | 1 | `""` (endpoint protegido) |
| `PAYMENT_GATEWAY_KEY` | 2 | `""` |
| `DB_PASS` | 2 | `""` |
| `EMAIL_USER` | 3 | `""` |
| `EMAIL_PASSWORD` | 3 | `""` |

### Iterando sobre a skill

Se a skill não detectou problemas suficientes ou a refatoração falhou:

1. Editar `antipatterns-catalog.md` para adicionar sinais de detecção mais específicos
2. Editar `refactoring-playbook.md` para adicionar o padrão de transformação correspondente
3. Executar `/refactor-arch` novamente — a skill re-lê os arquivos de referência a cada execução
