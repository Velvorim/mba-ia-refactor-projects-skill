import logging
from models import produto_model
from models.enums import CATEGORIAS_VALIDAS

# PT-06: Logger substituindo print()
logger = logging.getLogger(__name__)


def listar(limit: int = 100, offset: int = 0) -> list:
    """AP-15: repassa limit/offset para o model."""
    produtos = produto_model.get_all(limit=limit, offset=offset)
    logger.info("Listando %d produtos (offset=%d)", len(produtos), offset)
    return produtos


def buscar_por_id(id: int) -> dict:
    produto = produto_model.get_by_id(id)
    if produto is None:
        raise ValueError("Produto nao encontrado")
    return produto


def buscar(termo: str, categoria: str = None, preco_min: float = None, preco_max: float = None) -> list:
    return produto_model.search(termo, categoria, preco_min, preco_max)


def criar(dados: dict) -> dict:
    """PT-03: logica de validacao no controller, persistencia no model."""
    if not dados:
        raise ValueError("Dados invalidos")
    if "nome" not in dados:
        raise ValueError("Nome e obrigatorio")
    if "preco" not in dados:
        raise ValueError("Preco e obrigatorio")
    if "estoque" not in dados:
        raise ValueError("Estoque e obrigatorio")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        raise ValueError("Preco nao pode ser negativo")
    if estoque < 0:
        raise ValueError("Estoque nao pode ser negativo")
    if len(nome) < 2:
        raise ValueError("Nome muito curto")
    if len(nome) > 200:
        raise ValueError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError("Categoria invalida. Validas: " + str(CATEGORIAS_VALIDAS))

    id_ = produto_model.inserir(nome, descricao, preco, estoque, categoria)
    logger.info("Produto criado: id=%d nome=%s", id_, nome)
    return {"id": id_}


def atualizar(id: int, dados: dict) -> dict:
    """PT-03: validacao no controller."""
    produto_existente = produto_model.get_by_id(id)
    if not produto_existente:
        raise ValueError("Produto nao encontrado")

    if not dados:
        raise ValueError("Dados invalidos")
    if "nome" not in dados:
        raise ValueError("Nome e obrigatorio")
    if "preco" not in dados:
        raise ValueError("Preco e obrigatorio")
    if "estoque" not in dados:
        raise ValueError("Estoque e obrigatorio")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        raise ValueError("Preco nao pode ser negativo")
    if estoque < 0:
        raise ValueError("Estoque nao pode ser negativo")

    produto_model.atualizar(id, nome, descricao, preco, estoque, categoria)
    logger.info("Produto atualizado: id=%d", id)
    return {"sucesso": True, "mensagem": "Produto atualizado"}


def deletar(id: int) -> dict:
    produto = produto_model.get_by_id(id)
    if not produto:
        raise ValueError("Produto nao encontrado")
    produto_model.deletar(id)
    logger.info("Produto deletado: id=%d", id)
    return {"sucesso": True, "mensagem": "Produto deletado"}
