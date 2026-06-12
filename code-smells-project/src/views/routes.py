import logging
from flask import Blueprint, request, jsonify
from controllers import produto_controller, usuario_controller, pedido_controller
from database import get_db
from config import settings
from middlewares.admin_auth import require_admin_token

# PT-06: Logger substituindo print()
logger = logging.getLogger(__name__)

bp = Blueprint("api", __name__)


# ---------------------------------------------------------------------------
# INDEX
# ---------------------------------------------------------------------------

@bp.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo a API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        }
    })


# ---------------------------------------------------------------------------
# PRODUTOS
# ---------------------------------------------------------------------------

@bp.route("/produtos", methods=["GET"])
def listar_produtos():
    """AP-15: aceita ?limit=&offset= para paginacao."""
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    produtos = produto_controller.listar(limit=limit, offset=offset)
    return jsonify({"dados": produtos, "sucesso": True}), 200


@bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    if preco_min is not None:
        preco_min = float(preco_min)
    if preco_max is not None:
        preco_max = float(preco_max)

    resultados = produto_controller.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@bp.route("/produtos/<int:id>", methods=["GET"])
def buscar_produto(id):
    # PT-05: sem try/except — error_handler centralizado trata ValueError -> 404
    produto = produto_controller.buscar_por_id(id)
    return jsonify({"dados": produto, "sucesso": True}), 200


@bp.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    resultado = produto_controller.criar(dados)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Produto criado"}), 201


@bp.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    dados = request.get_json()
    resultado = produto_controller.atualizar(id, dados)
    return jsonify(resultado), 200


@bp.route("/produtos/<int:id>", methods=["DELETE"])
def deletar_produto(id):
    resultado = produto_controller.deletar(id)
    return jsonify(resultado), 200


# ---------------------------------------------------------------------------
# USUARIOS
# ---------------------------------------------------------------------------

@bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    """AP-15: paginacao."""
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    usuarios = usuario_controller.listar(limit=limit, offset=offset)
    return jsonify({"dados": usuarios, "sucesso": True}), 200


@bp.route("/usuarios/<int:id>", methods=["GET"])
def buscar_usuario(id):
    usuario = usuario_controller.buscar_por_id(id)
    return jsonify({"dados": usuario, "sucesso": True}), 200


@bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    dados = request.get_json()
    resultado = usuario_controller.criar(dados)
    return jsonify({"dados": resultado, "sucesso": True}), 201


@bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json() or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    usuario = usuario_controller.login(email, senha)
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200


# ---------------------------------------------------------------------------
# PEDIDOS
# ---------------------------------------------------------------------------

@bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados invalidos"}), 400
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    resultado = pedido_controller.criar(usuario_id, itens)
    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso"
    }), 201


@bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    """AP-15: paginacao."""
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    pedidos = pedido_controller.listar_todos(limit=limit, offset=offset)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_controller.listar_por_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    dados = request.get_json() or {}
    novo_status = dados.get("status", "")
    resultado = pedido_controller.atualizar_status(pedido_id, novo_status)
    return jsonify(resultado), 200


# ---------------------------------------------------------------------------
# RELATORIOS
# ---------------------------------------------------------------------------

@bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    relatorio = pedido_controller.relatorio_vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200


# ---------------------------------------------------------------------------
# HEALTH
# ---------------------------------------------------------------------------

@bp.route("/health", methods=["GET"])
def health_check():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    cursor.execute("SELECT COUNT(*) FROM produtos")
    produtos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    usuarios = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    pedidos = cursor.fetchone()[0]

    # AP-02: removidos "secret_key" e "debug" da resposta HTTP
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": produtos,
            "usuarios": usuarios,
            "pedidos": pedidos,
        },
        "versao": "1.0.0",
    }), 200


# ---------------------------------------------------------------------------
# ADMIN — PT-09: /admin/query REMOVIDO; /admin/reset-db protegido por token
# ---------------------------------------------------------------------------

@bp.route("/admin/reset-db", methods=["POST"])
@require_admin_token
def reset_database():
    """PT-09: requer header X-Admin-Token == ADMIN_TOKEN env var."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    db.commit()
    logger.warning("Banco de dados resetado via /admin/reset-db")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
