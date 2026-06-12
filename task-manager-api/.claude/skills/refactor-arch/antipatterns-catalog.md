# Catálogo de Anti-Patterns — Detecção e Severidade

Use este catálogo na Fase 2 para cruzar cada arquivo do projeto contra os sinais de detecção.
Para cada anti-pattern encontrado, registre: arquivo, linha exata, severidade e evidência.

---

## CRITICAL

### AP-01: God Class / God Method
**Descrição:** Um único arquivo ou classe concentra banco de dados, lógica de negócio, roteamento e validação para múltiplos domínios.

**Sinais de detecção:**
- Arquivo > 200 linhas com `SELECT`/`INSERT` E rotas (`@app.route`, `app.get(`) E lógica de negócio (`if`, `for`) no mesmo escopo
- Classe com mais de 5 métodos públicos que abrangem responsabilidades diferentes
- Nome genérico: `AppManager`, `Manager`, `Handler`, `God*`

**Exemplo:**
```python
# models.py com 300+ linhas contendo queries SQL + validação + lógica de pedidos
```

---

### AP-02: Hardcoded Credentials
**Descrição:** Senhas, chaves de API, tokens ou secrets escritos diretamente no código-fonte.

**Sinais de detecção (regex):**
- `SECRET_KEY\s*=\s*['"][^'"]{5,}['"]`
- `password\s*=\s*['"][^'"]+['"]`
- `api_key\s*=\s*['"][^'"]+['"]`
- `dbPass\s*:\s*['"][^'"]+['"]`
- `paymentGatewayKey\s*:\s*['"][^'"]+['"]`
- `smtp.*=\s*['"][^'"]+['"]`
- Qualquer string literal que contenha `senha`, `secret`, `password`, `key` com valor não-vazio

**Exemplos:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```
```javascript
dbPass: "senha_super_secreta_prod_123",
paymentGatewayKey: "pk_live_1234567890abcdef"
```

---

### AP-03: SQL Injection
**Descrição:** Queries SQL construídas via concatenação de strings ou f-strings com dados externos, sem parametrização.

**Sinais de detecção:**
- `"SELECT" + ` ou `"INSERT" + ` ou `"UPDATE" + ` (concatenação com variável)
- `f"SELECT ... {variavel}"` (f-string interpolando variável em SQL)
- `cursor.execute("... WHERE id = " + str(...))`
- Ausência de `?` ou `%s` como placeholder em queries com variáveis

**Exemplos:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("INSERT INTO produtos (nome) VALUES ('" + nome + "')")
```

---

### AP-04: Unprotected Admin Endpoints
**Descrição:** Endpoints administrativos que executam operações destrutivas sem autenticação ou autorização.

**Sinais de detecção:**
- Rota com `/admin`, `/debug`, `/internal` sem middleware de auth antes
- `cursor.execute(query)` onde `query` vem de `request.json` ou `request.args`
- Endpoint de reset de banco sem verificação de token: `"reset-db"`, `"drop"`, `"truncate"`

**Exemplo:**
```python
@app.route('/admin/query', methods=['POST'])
def admin_query():
    query = request.json.get('query')
    cursor.execute(query)  # executa qualquer SQL do usuário
```

---

## HIGH

### AP-05: Business Logic in Controller/Route
**Descrição:** Regras de negócio complexas implementadas diretamente nas funções de rota/controller, em vez de em uma camada de serviço ou modelo.

**Sinais de detecção:**
- Função de rota > 50 linhas
- Loops `for` com acumuladores de negócio dentro de handler de rota
- Cálculos de desconto, frete, status dentro de `@app.route`
- Múltiplos `if/elif` de regra de negócio antes de qualquer query

---

### AP-06: N+1 Query Problem
**Descrição:** Para cada item de uma lista, uma query adicional é executada — gerando O(n) queries quando uma seria suficiente.

**Sinais de detecção:**
- `for` loop contendo `cursor.execute(` ou `Model.query.filter(`
- Callbacks aninhados em Node.js com queries dentro de callbacks de query
- `db.get(` dentro de `db.all(` callback

**Exemplos:**
```python
pedidos = get_all_pedidos()
for pedido in pedidos:
    itens = get_itens_do_pedido(pedido['id'])  # N queries adicionais
```
```javascript
db.all('SELECT * FROM courses', (err, courses) => {
    courses.forEach(course => {
        db.all('SELECT * FROM enrollments WHERE course_id = ?', [course.id], ...)
    });
});
```

---

### AP-07: Broken or Weak Cryptography
**Descrição:** Uso de algoritmos criptográficos inadequados para armazenamento de senhas.

**Sinais de detecção:**
- `hashlib.md5(` para hashing de senha
- `hashlib.sha1(` para hashing de senha
- Função de hash customizada com operações de string (base64, repeat, slice)
- Senha armazenada em texto puro: `'password': senha_digitada`
- Sem uso de `bcrypt`, `argon2`, `scrypt` ou `pbkdf2`

**Exemplos:**
```python
hashlib.md5(pwd.encode()).hexdigest()  # MD5 é quebrado para senhas
```
```javascript
function badCrypto(input) {
    return Buffer.from(input).toString('base64').repeat(10000).slice(0, 10);
}
```

---

### AP-08: Fake or Missing Authentication
**Descrição:** Sistema de autenticação simulado que não oferece proteção real.

**Sinais de detecção:**
- Token gerado por concatenação de string: `'fake-jwt-token-' + str(user.id)`
- Rotas "protegidas" sem verificação de token
- `Authorization` header aceito sem validação de assinatura
- Ausência de qualquer middleware de auth em rotas que exigem login

**Exemplo:**
```python
return jsonify({'token': 'fake-jwt-token-' + str(user.id)})
```

---

## MEDIUM

### AP-09: Magic Strings and Magic Numbers
**Descrição:** Valores literais espalhados pelo código sem constantes ou enums nomeados.

**Sinais de detecção:**
- Mesmo valor de string aparece em 3+ lugares: `'pending'`, `'approved'`, `'enviado'`
- Números sem nome: `status == 1`, `type == 3`
- Ausência de classes `Enum` ou objetos `const` de configuração

---

### AP-10: Code Duplication
**Descrição:** Blocos de lógica idênticos ou muito similares repetidos em múltiplos locais.

**Sinais de detecção:**
- Construção manual de dicionário com os mesmos campos repetida em 2+ funções
- Cálculo de `overdue` (dias atrasados) replicado em 3+ lugares
- Bloco de tratamento de erro idêntico em cada endpoint

---

### AP-11: Debug Mode in Production Code
**Descrição:** Modo debug habilitado no código de produção, expondo stack traces e informações sensíveis.

**Sinais de detecção:**
- `app.run(debug=True)`
- `app.config["DEBUG"] = True`
- `DEBUG = True` no arquivo de configuração

---

### AP-12: Deprecated API Usage
**Descrição:** Uso de APIs que foram marcadas como deprecated em versões recentes das linguagens ou frameworks.

**Sinais de detecção:**

**Python:**
- `datetime.utcnow()` — deprecated desde Python 3.12; usar `datetime.now(timezone.utc)`
- `app.before_first_request` — removido no Flask 2.3+
- `@app.teardown_request` sem `with app.app_context()`

**Node.js:**
- `new Buffer(` — deprecated desde Node 6; usar `Buffer.from(` ou `Buffer.alloc(`
- `require('url').parse(` — substituir por `new URL(`
- Express 4: `res.json(status, body)` — substituir por `res.status(N).json(body)`
- `crypto.createCipher(` sem IV — deprecated; usar `createCipheriv(`

**SQLite3 (Node):**
- Modo callback puro sem Promises — considerar `better-sqlite3` ou `sqlite` wrapper

---

## LOW

### AP-13: Print Statements as Logging
**Descrição:** Uso de `print()` ou `console.log()` como mecanismo de logging de produção.

**Sinais de detecção:**
- `print(` em arquivo que não é `seed.py`, `cli.py` ou script de utilitário
- `console.log(` em arquivos de rota ou modelo
- Ausência de `import logging` (Python) ou `const logger = require(` (Node)

---

### AP-14: Unused Dependencies
**Descrição:** Pacotes declarados em `requirements.txt` ou `package.json` sem nenhum import no código.

**Sinais de detecção:**
- Grep por nome do pacote em todos os arquivos `.py`/`.js` retorna zero resultados
- Exemplos comuns: `marshmallow` sem `from marshmallow import`, `requests` sem `import requests`

---

### AP-15: Missing Pagination
**Descrição:** Endpoints GET de coleções que retornam todos os registros sem limite.

**Sinais de detecção:**
- `Model.query.all()` em endpoint de listagem sem `limit`/`paginate()`
- `db.all('SELECT * FROM tabela')` sem `LIMIT`/`OFFSET`
- Ausência de parâmetros `page`, `limit`, `offset` em rotas de listagem
