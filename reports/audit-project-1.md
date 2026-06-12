```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~490 lines of code

Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 4 | LOW: 2

Findings

[CRITICAL] AP-01: God Class / God Method
File: models.py:1-314
Description: models.py com 314 linhas concentra acesso a dados, logica de negocio
             (calculo de desconto, validacao de estoque, calculo de total de pedido)
             e multiplos dominios (produtos, usuarios, pedidos, relatorios) em um unico arquivo.
Impact: Qualquer alteracao em qualquer dominio exige editar o mesmo arquivo, causando
        conflitos de merge, dificuldade de teste unitario e violacao do SRP.
Recommendation: Aplicar PT-03: separar em models/produto_model.py,
                models/usuario_model.py, models/pedido_model.py +
                controllers/produto_controller.py, controllers/usuario_controller.py,
                controllers/pedido_controller.py.

[CRITICAL] AP-02: Hardcoded Credentials
File: app.py:7
Description: SECRET_KEY definida com valor literal "minha-chave-super-secreta-123"
             diretamente no codigo-fonte.
Impact: Qualquer pessoa com acesso ao repositorio obtem a chave de sessao,
        permitindo forjar cookies de sessao Flask.
Recommendation: Aplicar PT-01: mover para os.environ.get("SECRET_KEY",
                "dev-only-change-in-prod") em config/settings.py.

[CRITICAL] AP-02: Hardcoded Credentials (secret_key exposta em resposta HTTP)
File: controllers.py:289
Description: O endpoint /health retorna o valor de secret_key ("minha-chave-super-secreta-123")
             e debug=True no body JSON da resposta HTTP.
Impact: Qualquer cliente HTTP que chame /health obtem a chave secreta de producao em texto puro.
Recommendation: Remover campos "secret_key" e "debug" do response JSON do health_check.
                Usar variaveis de ambiente via config/settings.py.

[CRITICAL] AP-03: SQL Injection — multiplas ocorrencias
File: models.py:28 (get_produto_por_id)
Description: cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
             — concatenacao direta de variavel na query SQL. Ocorrencias adicionais
             nas linhas: 47-49, 57-61, 68, 92, 109-110, 126-128, 140, 149-151,
             155-156, 157-160, 162-165, 174, 188, 192, 220, 224, 280, 290-296.
Impact: Qualquer parametro manipulado permite exfiltrar ou destruir dados do banco.
Recommendation: Aplicar PT-02 em TODAS as queries de models.py:
                substituir concatenacao/f-string por parametros posicionais (?).

[CRITICAL] AP-04: Unprotected Admin Endpoints
File: app.py:59-78 (/admin/query)
Description: Endpoint POST /admin/query aceita campo "sql" do corpo da requisicao
             e o executa diretamente com cursor.execute(query) sem nenhuma autenticacao.
Impact: Qualquer usuario anonimo pode executar SELECT, DROP, DELETE ou INSERT arbitrario
        no banco de dados de producao — Remote Code Execution via SQL.
Recommendation: Aplicar PT-09: remover o endpoint /admin/query completamente.
                Para /admin/reset-db (app.py:47-57), proteger com token via
                middleware require_admin_token.

[HIGH] AP-05: Business Logic in Controller/Route
File: models.py:133-169 (criar_pedido)
Description: A funcao criar_pedido em models.py contem logica de negocio densa:
             validacao de estoque, calculo de total, iteracao dupla sobre itens,
             atualizacao de estoque — tudo dentro da camada de dados.
Impact: Impossivel testar a logica de negocio de pedidos isoladamente sem banco de dados;
        violacao de SRP.
Recommendation: Extrair logica de negocio para controllers/pedido_controller.py;
                manter em models/pedido_model.py apenas as operacoes de CRUD puro.

[HIGH] AP-05: Business Logic in Controller/Route
File: models.py:235-273 (relatorio_vendas)
Description: relatorio_vendas em models.py calcula desconto (3 faixas de faturamento),
             ticket medio e faturamento liquido — logica de negocio pura dentro de models.py.
Impact: Regras de negocio de desconto nao podem ser testadas sem acesso ao banco.
Recommendation: Mover calculos de desconto e ticket medio para
                controllers/pedido_controller.py; manter apenas as queries em models.

[HIGH] AP-06: N+1 Query Problem
File: models.py:171-201 (get_pedidos_usuario)
Description: Para cada pedido retornado pela query principal, sao executadas:
             1 query para itens_pedido + 1 query por item para buscar nome do produto.
             Com N pedidos e M itens, sao executadas 1 + N + (N*M) queries.
Impact: Para um usuario com 10 pedidos de 5 itens cada, sao executadas 61 queries
        onde 1 seria suficiente — degradacao exponencial de performance.
Recommendation: Aplicar PT-04: substituir por JOIN unico em
                models/pedido_model.py cobrindo pedidos + itens_pedido + produtos.

[HIGH] AP-06: N+1 Query Problem
File: models.py:203-233 (get_todos_pedidos)
Description: Identico ao get_pedidos_usuario: loop sobre pedidos com queries
             aninhadas para itens_pedido e produtos dentro de cada iteracao.
Impact: Com volume de pedidos em producao, esta funcao escala como O(N*M)
        em numero de queries — inaceitavel para listagem administrativa.
Recommendation: Aplicar PT-04: JOIN unico cobrindo pedidos + itens_pedido + produtos,
                agrupar resultado em Python.

[MEDIUM] AP-07: Broken or Weak Cryptography
File: models.py:122-131 (criar_usuario) + database.py:76-83 (seed)
Description: Senhas armazenadas em texto puro: criar_usuario insere senha diretamente
             na coluna "senha"; seed insere "admin123", "123456", "senha123" sem hash.
             login_usuario compara senha digitada com valor do banco diretamente.
Impact: Qualquer vazamento do banco expoe todas as senhas dos usuarios em texto claro.
Recommendation: Usar bcrypt para hash: pip install bcrypt;
                hashear no criar_usuario antes do INSERT;
                verificar com bcrypt.checkpw no login_usuario.
                Atualizar seed com hashes pre-computados.

[MEDIUM] AP-08: Fake or Missing Authentication
File: controllers.py:167-186 (login)
Description: O login retorna apenas os dados do usuario sem gerar nenhum token
             de autenticacao (JWT, sessao). Nenhuma rota verifica autenticacao.
Impact: Qualquer endpoint (listar usuarios com senhas, criar pedidos, etc.)
        e acessivel sem autenticacao — zero controle de acesso.
Recommendation: Implementar JWT real (flask-jwt-extended) ou Flask sessions assinadas.
                Documentar que auth completa esta fora do escopo desta refatoracao
                e adicionar placeholder no middleware.

[MEDIUM] AP-09: Magic Strings
File: controllers.py:242-243 + models.py:247-254
Description: Status de pedido ("pendente", "aprovado", "enviado", "entregue", "cancelado")
             aparecem como strings literais em controllers.py:242, models.py:247,
             models.py:250, models.py:253, models.py:133:149.
Impact: Renomear ou adicionar um status exige busca manual em multiplos arquivos;
        typos silenciosos nao sao detectados em tempo de compilacao.
Recommendation: Aplicar PT-07: criar models/enums.py com class StatusPedido(Enum)
                e referenciar StatusPedido.PENDENTE.value em todos os lugares.

[MEDIUM] AP-11: Debug Mode in Production Code
File: app.py:8 + app.py:88
Description: app.config["DEBUG"] = True hardcoded na linha 8 e app.run(debug=True)
             na linha 88. Modo debug expoe stack traces completos e ativa o reloader
             interativo do Werkzeug.
Impact: Em producao, qualquer excecao expoe codigo-fonte, variaveis locais e
        estrutura interna da aplicacao para o cliente HTTP.
Recommendation: Aplicar PT-01: substituir por
                DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
                em config/settings.py.

[LOW] AP-13: Print Statements as Logging
File: controllers.py:8,11,57,61,106,161,179,182,208,209,210,219,248,250
      app.py:56,83,84,85
Description: 18 chamadas a print() espalhadas por controllers.py e app.py,
             usadas como logging de producao (eventos, erros, notificacoes).
Impact: Sem nivel de severidade, sem timestamp, sem correlacao de request —
        impossivel filtrar ou agregar logs em producao. Saida vai para stdout sem estrutura.
Recommendation: Aplicar PT-06: substituir por logging.getLogger(__name__) com
                logger.info(), logger.error(), logger.warning() conforme a severidade.

[LOW] AP-15: Missing Pagination
File: controllers.py:5-12 (listar_produtos) + controllers.py:229-235 (listar_todos_pedidos)
      + controllers.py:128-134 (listar_usuarios)
Description: Endpoints GET /produtos, GET /pedidos e GET /usuarios retornam todos os
             registros sem parametros limit/offset/page.
Impact: Com volume crescente de dados, uma unica requisicao pode retornar milhares
        de registros, esgotando memoria e degradando tempo de resposta.
Recommendation: Adicionar parametros ?limit=20&offset=0 com defaults nos endpoints
                de listagem; passar para queries SQL com LIMIT ? OFFSET ?.

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
