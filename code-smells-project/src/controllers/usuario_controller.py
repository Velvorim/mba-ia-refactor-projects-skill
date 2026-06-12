import logging
import hashlib
from models import usuario_model

# PT-06: Logger substituindo print()
logger = logging.getLogger(__name__)


def listar(limit: int = 100, offset: int = 0) -> list:
    """AP-15: repassa limit/offset ao model. Nao expoe senhas (model omite campo)."""
    usuarios = usuario_model.get_all(limit=limit, offset=offset)
    return usuarios


def buscar_por_id(id: int) -> dict:
    usuario = usuario_model.get_by_id(id)
    if usuario is None:
        raise ValueError("Usuario nao encontrado")
    return usuario


def criar(dados: dict) -> dict:
    """PT-03: validacao no controller."""
    if not dados:
        raise ValueError("Dados invalidos")

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ValueError("Nome, email e senha sao obrigatorios")

    # AP-07: hash da senha antes de persistir.
    # Nota: usar bcrypt em producao (pip install bcrypt).
    # Aqui usamos hashlib.sha256 como placeholder adequado para o escopo da refatoracao.
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    id_ = usuario_model.inserir(nome, email, senha_hash)
    logger.info("Usuario criado: email=%s", email)
    return {"id": id_}


def login(email: str, senha: str) -> dict:
    """AP-08: retorna dados do usuario sem token real.
    Nota: JWT real (flask-jwt-extended) esta fora do escopo desta refatoracao."""
    if not email or not senha:
        raise ValueError("Email e senha sao obrigatorios")

    usuario = usuario_model.get_by_email(email)
    if usuario is None:
        raise PermissionError("Email ou senha invalidos")

    # AP-07: comparar hash
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    if usuario["senha"] != senha_hash:
        raise PermissionError("Email ou senha invalidos")

    logger.info("Login bem-sucedido: email=%s", email)

    # Retorna sem expor senha
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "tipo": usuario["tipo"],
    }
