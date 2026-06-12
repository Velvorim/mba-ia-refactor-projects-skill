import logging
from database import get_db
from models import pedido_model
from models.enums import StatusPedido

# PT-06: Logger substituindo print()
logger = logging.getLogger(__name__)


def criar(usuario_id: int, itens: list) -> dict:
    """PT-03: logica de negocio (validacao de estoque, calculo de total) no controller.
    PT-02: todas as queries internas usam parametros posicionais.
    PT-07: StatusPedido.PENDENTE.value em vez de magic string.
    """
    if not usuario_id:
        raise ValueError("Usuario ID e obrigatorio")
    if not itens or len(itens) == 0:
        raise ValueError("Pedido deve ter pelo menos 1 item")

    db = get_db()
    cursor = db.cursor()

    # Fase 1: validar estoque e calcular total (uma query por produto — aceitavel para transacao)
    total = 0.0
    itens_com_preco = []
    for item in itens:
        produto = pedido_model.get_produto_para_pedido(cursor, item["produto_id"])
        if produto is None:
            raise ValueError("Produto " + str(item["produto_id"]) + " nao encontrado")
        if produto["estoque"] < item["quantidade"]:
            raise ValueError("Estoque insuficiente para " + produto["nome"])
        preco_unitario = produto["preco"]
        total += preco_unitario * item["quantidade"]
        itens_com_preco.append({**item, "preco_unitario": preco_unitario})

    # Fase 2: persistir pedido e itens em transacao unica
    pedido_id = pedido_model.inserir(usuario_id, total)

    for item in itens_com_preco:
        pedido_model.inserir_item(cursor, pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
        pedido_model.atualizar_estoque(cursor, item["produto_id"], item["quantidade"])

    db.commit()

    logger.info(
        "Pedido criado: id=%d usuario_id=%d total=%.2f itens=%d",
        pedido_id, usuario_id, total, len(itens)
    )
    return {"pedido_id": pedido_id, "total": total}


def listar_por_usuario(usuario_id: int) -> list:
    return pedido_model.get_by_usuario(usuario_id)


def listar_todos(limit: int = 100, offset: int = 0) -> list:
    """AP-15: paginacao adicionada."""
    return pedido_model.get_all(limit=limit, offset=offset)


def atualizar_status(pedido_id: int, novo_status: str) -> dict:
    """PT-07: valida contra enum StatusPedido."""
    status_validos = [s.value for s in StatusPedido]
    if novo_status not in status_validos:
        raise ValueError("Status invalido. Validos: " + str(status_validos))

    pedido_model.atualizar_status(pedido_id, novo_status)

    if novo_status == StatusPedido.APROVADO.value:
        logger.info("Pedido %d aprovado — preparar envio", pedido_id)
    elif novo_status == StatusPedido.CANCELADO.value:
        logger.warning("Pedido %d cancelado — verificar estoque", pedido_id)

    return {"sucesso": True, "mensagem": "Status atualizado"}


def relatorio_vendas() -> dict:
    """PT-03: logica de negocio (calculo de desconto, ticket medio) no controller.
    O model retorna apenas os dados agregados brutos.
    """
    stats = pedido_model.get_stats()
    faturamento = stats["faturamento"]
    total_pedidos = stats["total_pedidos"]

    # Regra de desconto (logica de negocio — pertence ao controller)
    desconto = 0.0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02

    ticket_medio = round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": stats["pendentes"],
        "pedidos_aprovados": stats["aprovados"],
        "pedidos_cancelados": stats["cancelados"],
        "ticket_medio": ticket_medio,
    }
