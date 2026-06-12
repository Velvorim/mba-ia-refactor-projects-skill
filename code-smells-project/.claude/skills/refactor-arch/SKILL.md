# Skill: refactor-arch
# Auditoria e Refatoração Arquitetural para Padrão MVC

Você é um especialista em arquitetura de software. Quando esta skill for invocada, execute as 3 fases abaixo em sequência, trabalhando no projeto do diretório atual.

**Arquivos de referência disponíveis nesta pasta:**
- `project-analysis.md` — heurísticas de detecção de stack e arquitetura
- `antipatterns-catalog.md` — catálogo de 15 anti-patterns com sinais de detecção e severidade
- `audit-report-template.md` — template obrigatório do relatório de auditoria
- `mvc-architecture-guidelines.md` — estrutura-alvo MVC por tecnologia
- `refactoring-playbook.md` — 10 padrões de transformação com código antes/depois

---

## FASE 1 — ANÁLISE DO PROJETO

**Objetivo:** detectar stack, mapear arquitetura atual e imprimir resumo estruturado.

### Passos:

1. Leia `project-analysis.md` para entender as heurísticas de detecção.

2. Varrer o projeto atual:
   - Listar todos os arquivos `.py`, `.js`, `.ts` (excluir `node_modules/`, `venv/`, `.git/`)
   - Ler o arquivo `requirements.txt` ou `package.json` para obter versões
   - Ler todos os arquivos de código-fonte para entender a estrutura

3. Determinar:
   - **Linguagem** e **Framework** (com versão)
   - **Dependências principais**
   - **Domínio da aplicação** (inferido de nomes de tabelas, rotas, variáveis)
   - **Arquitetura atual** (monolítica, camadas, etc.)
   - **Número de arquivos** analisados
   - **Tabelas do banco** (via `CREATE TABLE` ou classes de modelo)

4. Imprimir o bloco abaixo preenchido:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework versão>
Dependencies:  <lista principal>
Domain:        <domínio inferido>
Architecture:  <descrição em 1 frase>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas>
================================
```

---

## FASE 2 — AUDITORIA DE CÓDIGO

**Objetivo:** identificar anti-patterns, gerar relatório estruturado e aguardar confirmação antes de qualquer modificação.

### Passos:

1. Leia `antipatterns-catalog.md` completamente.

2. Para cada arquivo de código-fonte analisado na Fase 1:
   - Cruzar o conteúdo contra **cada anti-pattern** do catálogo
   - Para cada ocorrência encontrada, registrar: arquivo, linha(s) exata(s), severidade, evidência (trecho de código)

3. Ordenar os findings: CRITICAL → HIGH → MEDIUM → LOW

4. Leia `audit-report-template.md` e preencha o template com todos os findings encontrados.
   - Cada finding DEVE ter: arquivo:linha, descrição factual, impacto, recomendação específica
   - Referenciar o padrão do playbook quando aplicável (ex: "Aplicar PT-02")

5. Imprimir o relatório completo.

6. **PARAR AQUI.** Imprimir a linha:
   ```
   Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
   ```
   **Aguardar a resposta do usuário. NÃO modificar nenhum arquivo antes da confirmação `y`.**

---

## FASE 3 — REFATORAÇÃO PARA MVC

**Execute esta fase SOMENTE após confirmação explícita `y` do usuário na Fase 2.**

**Objetivo:** reestruturar o projeto para o padrão MVC, aplicando os padrões do playbook, mantendo todos os endpoints originais funcionando.

### Passos:

1. Leia `mvc-architecture-guidelines.md` para entender a estrutura-alvo para a tecnologia detectada.

2. Leia `refactoring-playbook.md` para conhecer os padrões de transformação disponíveis.

3. Planejar a nova estrutura de arquivos baseada na tecnologia:

   **Python/Flask:**
   ```
   src/
   ├── config/settings.py
   ├── models/<dominio>_model.py    (um por domínio detectado)
   ├── controllers/<dominio>_controller.py
   ├── views/routes.py
   ├── middlewares/error_handler.py
   └── app.py
   ```

   **Node.js/Express:**
   ```
   src/
   ├── config/settings.js
   ├── models/<dominio>.model.js
   ├── controllers/<dominio>.controller.js
   ├── routes/<dominio>.routes.js
   ├── middlewares/errorHandler.js
   └── app.js
   ```

4. Para cada finding CRITICAL e HIGH da Fase 2, aplicar o padrão correspondente do playbook:
   - AP-01 God Class → PT-03 (Separar em Model + Controller)
   - AP-02 Hardcoded Credentials → PT-01 (Extrair para variável de ambiente)
   - AP-03 SQL Injection → PT-02 (Parâmetros posicionais)
   - AP-04 Admin Endpoints → PT-09 (Remover ou proteger)
   - AP-06 N+1 Query → PT-04 (JOIN único)
   - AP-07 Weak Crypto → substituir por `bcrypt` (Python) ou `bcryptjs` (Node)
   - AP-08 Fake Auth → remover token falso; documentar que auth real está fora do escopo
   - AP-12 Deprecated API → PT-10 (Migrar utcnow / Buffer)

5. Para findings MEDIUM e LOW:
   - AP-09 Magic Strings → PT-07 (Enum)
   - AP-10 Code Duplication → extrair função auxiliar
   - AP-11 Debug Mode → PT-01 (variável de ambiente)
   - AP-13 Print → PT-06 (Logger)
   - AP-14 Unused deps → remover do requirements.txt/package.json
   - AP-15 Missing Pagination → adicionar parâmetros `limit`/`offset` com defaults

6. Criar os arquivos na nova estrutura, garantindo:
   - Todos os endpoints originais existem com as mesmas URLs
   - Response shapes são idênticos aos originais
   - Sem regressões de funcionalidade

7. Atualizar o entry point (`app.py` / `app.js`) para importar da nova estrutura.

8. **Validar a aplicação:**

   **Python/Flask:**
   ```bash
   pip install -r requirements.txt
   python src/app.py
   # Em outro terminal: curl http://localhost:5000/health (ou equivalente)
   ```

   **Node.js/Express:**
   ```bash
   npm install
   node src/app.js
   # Em outro terminal: curl http://localhost:3000/ (ou equivalente)
   ```

9. Imprimir o relatório final:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
src/
├── config/settings.<ext>
├── models/
│   └── <lista dos model files>
├── controllers/
│   └── <lista dos controller files>
├── views/ (ou routes/)
│   └── routes.<ext>
├── middlewares/error_handler.<ext>
└── app.<ext>

Anti-patterns resolved:
  ✓ <AP-01: God Class — separado em N models + controllers>
  ✓ <AP-02: Hardcoded Credentials — movidos para variáveis de ambiente>
  ... (um por finding corrigido)

Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero CRITICAL anti-patterns remaining
================================
```

---

## Regras Gerais

- **Agnóstica de tecnologia:** as fases 1 e 2 funcionam para qualquer linguagem/framework. A Fase 3 usa o template correto detectado na Fase 1.
- **Preservar funcionalidade:** nunca remover endpoints existentes — apenas reorganizá-los.
- **Confirmação obrigatória:** a Fase 3 jamais deve iniciar sem `y` explícito do usuário.
- **Arquivos originais:** manter os arquivos originais na raiz até a Fase 3 estar completa e validada; depois podem ser removidos ou mantidos como referência.
- **Sem over-engineering:** não adicionar funcionalidades além das existentes; apenas reorganizar e corrigir os problemas encontrados.
