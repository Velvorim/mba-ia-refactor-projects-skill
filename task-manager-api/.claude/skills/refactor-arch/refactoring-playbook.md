# Refactoring Playbook — Padrões de Transformação

Cada padrão abaixo corresponde a um ou mais anti-patterns do catálogo.
Aplicar o padrão correspondente ao finding identificado na Fase 2.

---

## PT-01: Extrair Config para Variável de Ambiente

**Anti-pattern:** AP-02 (Hardcoded Credentials)
**Aplicar em:** qualquer valor literal de secret, chave ou credencial

**Python — ANTES:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
DATABASE = "banco.db"
```

**Python — DEPOIS:**
```python
# config/settings.py
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-prod")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
DATABASE_PATH = os.environ.get("DATABASE_PATH", "banco.db")
```

**Node.js — ANTES:**
```javascript
const config = {
  dbPass: "senha_super_secreta_prod_123",
  paymentGatewayKey: "pk_live_1234567890abcdef",
};
```

**Node.js — DEPOIS:**
```javascript
// config/settings.js
module.exports = {
  dbPass: process.env.DB_PASS || '',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
};
```

---

## PT-02: Corrigir SQL Injection com Parâmetros Posicionais

**Anti-pattern:** AP-03 (SQL Injection)
**Aplicar em:** toda query que use concatenação de string ou f-string

**Python — ANTES:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("INSERT INTO produtos (nome, preco) VALUES ('" + nome + "', " + str(preco) + ")")
```

**Python — DEPOIS:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (nome, preco))
```

**Regra:** sempre usar `?` (sqlite3) ou `%s` (psycopg2) — nunca interpolar variáveis diretamente na string SQL.

---

## PT-03: Separar God Class em Model + Controller

**Anti-pattern:** AP-01 (God Class), AP-05 (Business Logic in Controller)
**Aplicar em:** arquivo monolítico com queries + lógica + rotas misturadas

**ANTES — models.py (tudo junto):**
```python
def criar_produto(nome, descricao, preco, estoque, categoria):
    if not nome or preco <= 0:
        return {"erro": "Dados inválidos"}
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (nome, preco))
    conn.commit()
    print("Produto criado: " + nome)
    return {"id": cursor.lastrowid}
```

**DEPOIS — models/produto_model.py:**
```python
def inserir(nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria)
    )
    conn.commit()
    return cursor.lastrowid
```

**DEPOIS — controllers/produto_controller.py:**
```python
import logging
from models import produto_model

logger = logging.getLogger(__name__)

def criar_produto(dados: dict) -> dict:
    if not dados.get("nome") or dados.get("preco", 0) <= 0:
        raise ValueError("Nome e preço válido são obrigatórios")
    id_ = produto_model.inserir(
        dados["nome"], dados.get("descricao", ""),
        dados["preco"], dados.get("estoque", 0), dados.get("categoria", "")
    )
    logger.info("Produto criado: id=%d nome=%s", id_, dados["nome"])
    return produto_model.get_by_id(id_)
```

---

## PT-04: Eliminar N+1 com Query de JOIN

**Anti-pattern:** AP-06 (N+1 Query Problem)
**Aplicar em:** loops que executam queries dentro de cada iteração

**Python — ANTES:**
```python
pedidos = get_all_pedidos()
resultado = []
for pedido in pedidos:
    itens = get_itens_do_pedido(pedido['id'])   # 1 query por pedido
    for item in itens:
        produto = get_produto(item['produto_id'])  # 1 query por item
        item['produto'] = produto
    pedido['itens'] = itens
    resultado.append(pedido)
```

**Python — DEPOIS:**
```python
cursor.execute("""
    SELECT
        p.id AS pedido_id, p.status, p.total,
        i.produto_id, i.quantidade, i.preco_unitario,
        pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    ORDER BY p.id
""")
rows = cursor.fetchall()
# agrupar em Python — 1 query total
pedidos = {}
for row in rows:
    pid = row['pedido_id']
    if pid not in pedidos:
        pedidos[pid] = {'id': pid, 'status': row['status'], 'itens': []}
    if row['produto_id']:
        pedidos[pid]['itens'].append({
            'produto_id': row['produto_id'],
            'nome': row['produto_nome'],
            'quantidade': row['quantidade'],
        })
return list(pedidos.values())
```

**Node.js — ANTES (callback hell + N+1):**
```javascript
db.all('SELECT * FROM courses', (err, courses) => {
    courses.forEach(course => {
        db.all('SELECT * FROM enrollments WHERE course_id = ?', [course.id], (err, enrs) => {
            enrs.forEach(enr => {
                db.get('SELECT * FROM users WHERE id = ?', [enr.user_id], ...)
            });
        });
    });
});
```

**Node.js — DEPOIS (async/await + JOIN):**
```javascript
const rows = await dbAll(`
    SELECT c.id AS course_id, c.title,
           e.id AS enrollment_id, u.name AS user_name, p.amount
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    LEFT JOIN users u ON u.id = e.user_id
    LEFT JOIN payments p ON p.enrollment_id = e.id
`);
// agrupar em JS
const courses = {};
for (const row of rows) {
    if (!courses[row.course_id]) {
        courses[row.course_id] = { id: row.course_id, title: row.title, enrollments: [] };
    }
    if (row.enrollment_id) {
        courses[row.course_id].enrollments.push({
            user: row.user_name, amount: row.amount
        });
    }
}
return Object.values(courses);
```

---

## PT-05: Centralizar Error Handling em Middleware

**Anti-pattern:** AP-05 (lógica de erro duplicada em cada rota)
**Aplicar em:** `try/except` ou `try/catch` repetidos em todos os endpoints

**Python — ANTES:**
```python
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    try:
        produtos = produto_model.get_all()
        return jsonify(produtos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pedidos', methods=['GET'])
def listar_pedidos():
    try:
        pedidos = pedido_model.get_all()
        return jsonify(pedidos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

**Python — DEPOIS:**
```python
# middlewares/error_handler.py
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error("Unhandled: %s", e, exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# views/routes.py — sem try/except
@bp.route('/produtos', methods=['GET'])
def listar_produtos():
    return jsonify(produto_controller.listar())
```

**Node.js — DEPOIS:**
```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    const status = err.status || 500;
    res.status(status).json({ error: err.message || 'Internal server error' });
}
module.exports = errorHandler;

// routes — usar next(err) em vez de res.status(500)
router.get('/', async (req, res, next) => {
    try {
        res.json(await controller.listar());
    } catch (err) { next(err); }
});
```

---

## PT-06: Substituir Print por Logger

**Anti-pattern:** AP-13 (Print Statements as Logging)
**Aplicar em:** todo `print(` em arquivos de produção

**Python — ANTES:**
```python
print("Listando " + str(len(produtos)) + " produtos")
print("Erro ao criar produto: " + str(e))
```

**Python — DEPOIS:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Listando %d produtos", len(produtos))
logger.error("Erro ao criar produto: %s", e, exc_info=True)
```

**Configuração no app.py:**
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s"
)
```

**Node.js — ANTES:**
```javascript
console.log('Produto criado: ' + nome);
console.error('Erro: ' + err.message);
```

**Node.js — DEPOIS:**
```javascript
// utils/logger.js
const logger = {
    info: (msg, meta) => console.log(JSON.stringify({ level: 'info', msg, ...meta, ts: new Date() })),
    error: (msg, meta) => console.error(JSON.stringify({ level: 'error', msg, ...meta, ts: new Date() })),
};
module.exports = logger;
```

---

## PT-07: Substituir Magic Strings por Enum

**Anti-pattern:** AP-09 (Magic Strings)
**Aplicar em:** status values, tipos e categorias repetidos como strings literais

**Python — ANTES:**
```python
if pedido['status'] == 'pendente':
    ...
if pedido['status'] == 'aprovado':
    ...
if tarefa['status'] == 'in_progress':
    ...
```

**Python — DEPOIS:**
```python
# models/enums.py
from enum import Enum

class StatusPedido(Enum):
    PENDENTE = 'pendente'
    APROVADO = 'aprovado'
    ENVIADO = 'enviado'
    CANCELADO = 'cancelado'

class StatusTarefa(Enum):
    PENDENTE = 'pending'
    EM_PROGRESSO = 'in_progress'
    CONCLUIDA = 'done'
    CANCELADA = 'cancelled'

# uso
if pedido['status'] == StatusPedido.PENDENTE.value:
    ...
```

---

## PT-08: Callback Hell → async/await (Node.js)

**Anti-pattern:** AP-01 (God Method com callbacks aninhados), AP-06 (N+1 em callbacks)
**Aplicar em:** funções com 3+ níveis de callbacks aninhados

**ANTES:**
```javascript
db.get('SELECT * FROM users WHERE id = ?', [userId], (err, user) => {
    if (err) return res.status(500).send('Erro');
    db.all('SELECT * FROM enrollments WHERE user_id = ?', [userId], (err2, enrs) => {
        if (err2) return res.status(500).send('Erro');
        enrs.forEach(enr => {
            db.get('SELECT * FROM payments WHERE enrollment_id = ?', [enr.id], (err3, pay) => {
                // mais níveis...
            });
        });
    });
});
```

**DEPOIS:**
```javascript
const { promisify } = require('util');

// Criar helpers Promise-based uma vez
function dbGet(db, sql, params = []) {
    return new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => err ? reject(err) : resolve(row));
    });
}

function dbAll(db, sql, params = []) {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => err ? reject(err) : resolve(rows));
    });
}

// Handler limpo
async function getUser(req, res, next) {
    try {
        const user = await dbGet(db, 'SELECT * FROM users WHERE id = ?', [req.params.id]);
        if (!user) return res.status(404).json({ error: 'User not found' });
        const enrollments = await dbAll(db, 'SELECT * FROM enrollments WHERE user_id = ?', [user.id]);
        res.json({ user, enrollments });
    } catch (err) { next(err); }
}
```

---

## PT-09: Remover ou Proteger Endpoint Admin

**Anti-pattern:** AP-04 (Unprotected Admin Endpoints)
**Aplicar em:** rotas `/admin`, `/debug`, `/internal` sem autenticação

**ANTES:**
```python
@app.route('/admin/query', methods=['POST'])
def admin_query():
    query = request.json.get('query')
    cursor.execute(query)  # executa qualquer SQL
    return jsonify(cursor.fetchall())

@app.route('/admin/reset-db', methods=['POST'])
def reset_db():
    init_db()
    return jsonify({"status": "reset"})
```

**DEPOIS — remover rotas de execução arbitrária de SQL completamente.**
Se manutenção de reset for necessária, proteger com token:
```python
# middlewares/admin_auth.py
import os
from functools import wraps
from flask import request, jsonify

def require_admin_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Admin-Token', '')
        if not token or token != os.environ.get('ADMIN_TOKEN', ''):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# views/admin_routes.py — apenas reset, sem query arbitrária
@admin_bp.route('/reset-db', methods=['POST'])
@require_admin_token
def reset_db():
    init_db()
    return jsonify({"status": "reset"})
```

---

## PT-10: Migrar datetime.utcnow() — API Deprecated

**Anti-pattern:** AP-12 (Deprecated API Usage)
**Aplicar em:** todo uso de `datetime.utcnow()` em Python 3.12+

**ANTES:**
```python
from datetime import datetime
created_at = datetime.utcnow()
updated_at = datetime.utcnow()
```

**DEPOIS:**
```python
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
updated_at = datetime.now(timezone.utc)
```

**Node.js — Buffer deprecated:**
```javascript
// ANTES (deprecated desde Node 6)
const buf = new Buffer(data);

// DEPOIS
const buf = Buffer.from(data);
```

**Express — res.json com status:**
```javascript
// ANTES (deprecated no Express 5)
res.json(404, { error: 'Not found' });

// DEPOIS
res.status(404).json({ error: 'Not found' });
```
