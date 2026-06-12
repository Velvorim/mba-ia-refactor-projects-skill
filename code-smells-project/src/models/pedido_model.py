import logging
from database import get_db
from models.enums import StatusPedido

logger = logging.getLogger(__name__)


def inserir(usuario_id: int, total: float) -> int:
    """Insere pedido e retorna o ID gerado."""
    db = get_db()
    cursor = db.cursor()
    # PT-02 + PT-07: parametro posicional + enum para status inicial
    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, StatusPedido.PENDENTE.value, total)
    )
    db.commit()
    return cursor.lastrowid


def inserir_item(cursor, pedido_id: int, produto_id: int, quantidade: int, preco_unitario: float) -> None:
    """Insere item de pedido usando cursor compartilhado (mesma transacao)."""
    # PT-02: parametros posicionais
    cursor.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario)
    )


def get_produto_para_pedido(cursor, produto_id: int) -> dict | None:
    """Busca produto com cursor compartilhado para verificacao de estoque."""
    # PT-02: parametro posicional
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def atualizar_estoque(cursor, produto_id: int, quantidade: int) -> None:
    """Decrementa estoque usando cursor compartilhado."""
    # PT-02: parametros posicionais
    cursor.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id)
    )


def get_by_usuario(usuario_id: int) -> list:
    """PT-04: JOIN unico eliminando N+1 queries para pedidos do usuario."""
    db = get_db()
    cursor = db.cursor()
    # PT-02 + PT-04: parametro posicional + JOIN unico
    cursor.execute("""
        SELECT
            p.id         AS pedido_id,
            p.usuario_id,
            p.status,
            p.total,
            p.criado_em,
            i.produto_id,
            i.quantidade,
            i.preco_unitario,
            pr.nome      AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr   ON pr.id = i.produto_id
        WHERE p.usuario_id = ?
        ORDER BY p.id
    """, (usuario_id,))
    rows = cursor.fetchall()
    return _agrupar_pedidos(rows)


def get_all(limit: int = 100, offset: int = 0) -> list:
    """PT-04: JOIN unico + AP-15: paginacao."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            p.id         AS pedido_id,
            p.usuario_id,
            p.status,
            p.total,
            p.criado_em,
            i.produto_id,
            i.quantidade,
            i.preco_unitario,
            pr.nome      AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr   ON pr.id = i.produto_id
        ORDER BY p.id
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    return _agrupar_pedidos(rows)


def atualizar_status(pedido_id: int, novo_status: str) -> bool:
    db = get_db()
    cursor = db.cursor()
    # PT-02: parametros posicionais
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id)
    )
    db.commit()
    return cursor.rowcount > 0


def get_stats() -> dict:
    """Queries agregadas para relatorio — apenas acesso a dados, sem logica de negocio."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0] or 0.0

    # PT-07: StatusPedido.value para evitar magic strings
    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", (StatusPedido.PENDENTE.value,))
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", (StatusPedido.APROVADO.value,))
    aprovados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", (StatusPedido.CANCELADO.value,))
    cancelados = cursor.fetchone()[0]

    return {
        "total_pedidos": total_pedidos,
        "faturamento": faturamento,
        "pendentes": pendentes,
        "aprovados": aprovados,
        "cancelados": cancelados,
    }


def _agrupar_pedidos(rows) -> list:
    """PT-04: agrupa linhas de JOIN em estrutura de pedidos com itens aninhados."""
    pedidos = {}
    for row in rows:
        pid = row["pedido_id"]
        if pid not in pedidos:
            pedidos[pid] = {
                "id": pid,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["produto_id"] is not None:
            pedidos[pid]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] if row["produto_nome"] else "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())
