# MVC Architecture Guidelines — Estrutura-Alvo

## Princípios Fundamentais

1. **Config:** zero credenciais hardcoded — sempre via variáveis de ambiente com fallback para desenvolvimento
2. **Model:** apenas acesso a dados (queries, ORM) — sem lógica de negócio, sem HTTP
3. **Controller:** orquestra model + regras de negócio — sem acesso direto a `request`/`response`
4. **View / Route:** valida input, chama controller, serializa response — sem lógica de negócio
5. **Middleware:** error handling, logging, auth — nunca inline nas rotas
6. **Entry point (app.py / app.js):** apenas composition root — registra blueprints/routers, inicializa app

---

## Estrutura Python / Flask

```
src/
├── config/
│   └── settings.py              # Toda configuração via os.environ.get()
├── models/
│   └── <dominio>_model.py       # Acesso a dados por domínio
├── controllers/
│   └── <dominio>_controller.py  # Lógica de negócio por domínio
├── views/
│   └── routes.py                # Blueprint com todas as rotas
├── middlewares/
│   └── error_handler.py         # @app.errorhandler centralizado
└── app.py                       # create_app() — composition root
```

### config/settings.py
```python
import os

DATABASE_PATH = os.environ.get("DATABASE_PATH", "database.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))
```

### models/<dominio>_model.py
```python
# Apenas queries — retorna dicts ou lança exceções de dados
def get_all() -> list[dict]:
    ...

def get_by_id(id: int) -> dict | None:
    ...

def create(data: dict) -> int:
    ...

def update(id: int, data: dict) -> bool:
    ...

def delete(id: int) -> bool:
    ...
```

### controllers/<dominio>_controller.py
```python
# Recebe dados validados, aplica regras, delega ao model
from models import dominio_model

def listar():
    return dominio_model.get_all()

def criar(dados: dict) -> dict:
    if not dados.get("nome"):
        raise ValueError("Campo 'nome' é obrigatório")
    id_ = dominio_model.create(dados)
    return dominio_model.get_by_id(id_)
```

### views/routes.py
```python
from flask import Blueprint, request, jsonify
from controllers import dominio_controller

bp = Blueprint("dominio", __name__, url_prefix="/dominio")

@bp.route("/", methods=["GET"])
def listar():
    return jsonify(dominio_controller.listar())

@bp.route("/", methods=["POST"])
def criar():
    dados = request.get_json()
    resultado = dominio_controller.criar(dados)
    return jsonify(resultado), 201
```

### middlewares/error_handler.py
```python
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(ValueError)
    def value_error(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(Exception)
    def internal_error(e):
        logger.error("Unhandled exception: %s", e, exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
```

### app.py
```python
from flask import Flask
from config import settings
from views.routes import bp as dominio_bp
from middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    app.register_blueprint(dominio_bp)
    register_error_handlers(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
```

---

## Estrutura Node.js / Express

```
src/
├── config/
│   └── settings.js              # process.env com defaults
├── models/
│   └── <dominio>.model.js       # Acesso a dados
├── controllers/
│   └── <dominio>.controller.js  # Lógica de negócio
├── routes/
│   └── <dominio>.routes.js      # express.Router()
├── middlewares/
│   └── errorHandler.js          # Error middleware (4 parâmetros)
└── app.js                       # Composition root
```

### config/settings.js
```javascript
module.exports = {
  dbPath: process.env.DB_PATH || ':memory:',
  secretKey: process.env.SECRET_KEY || 'dev-only-insecure-key',
  port: parseInt(process.env.PORT || '3000', 10),
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
};
```

### models/<dominio>.model.js
```javascript
const db = require('../database');

async function findAll() { ... }
async function findById(id) { ... }
async function create(data) { ... }
async function remove(id) { ... }

module.exports = { findAll, findById, create, remove };
```

### controllers/<dominio>.controller.js
```javascript
const model = require('../models/dominio.model');

async function listar() {
  return model.findAll();
}

async function criar(dados) {
  if (!dados.nome) throw new Error("'nome' é obrigatório");
  return model.create(dados);
}

module.exports = { listar, criar };
```

### routes/<dominio>.routes.js
```javascript
const { Router } = require('express');
const controller = require('../controllers/dominio.controller');
const router = Router();

router.get('/', async (req, res, next) => {
  try {
    res.json(await controller.listar());
  } catch (err) { next(err); }
});

router.post('/', async (req, res, next) => {
  try {
    res.status(201).json(await controller.criar(req.body));
  } catch (err) { next(err); }
});

module.exports = router;
```

### middlewares/errorHandler.js
```javascript
const logger = require('../utils/logger');

function errorHandler(err, req, res, next) {
  logger.error(err.message, { stack: err.stack });
  const status = err.status || 500;
  res.status(status).json({ error: err.message || 'Internal server error' });
}

module.exports = errorHandler;
```

### app.js
```javascript
const express = require('express');
const settings = require('./config/settings');
const dominioRoutes = require('./routes/dominio.routes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());
app.use('/dominio', dominioRoutes);
app.use(errorHandler);

app.listen(settings.port, () => {
  console.log(`Server running on port ${settings.port}`);
});

module.exports = app;
```

---

## Checklist de Conformidade MVC

- [ ] Nenhum secret hardcoded no código — apenas `os.environ.get()` / `process.env`
- [ ] Models não importam `request` ou `response`
- [ ] Controllers não importam `Flask` ou `express` diretamente
- [ ] Rotas não contêm lógica de negócio (sem `if` de regra de domínio)
- [ ] Error handling centralizado em middleware (não duplicado em cada rota)
- [ ] Debug mode controlado por variável de ambiente
- [ ] Logging via biblioteca (`logging` / `winston`) — sem `print` / `console.log` de produção
- [ ] Endpoints originais mantidos (mesmas URLs e response shapes)
