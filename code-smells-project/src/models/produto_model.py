import logging
from database import get_db

logger = logging.getLogger(__name__)


def get_all(limit: int = 100, offset: int = 0) -> list:
    """AP-15: Paginacao adicionada com limit/offset."""
    db = get_db()
    cursor = db.cursor()
    # PT-02: parâmetros posicionais — sem concatenacao
    cursor.execute("SELECT * FROM produtos LIMIT ? OFFSET ?", (limit, offset))
    rows = cursor.fetchall()
    return [_row_to_dict(row) for row in rows]


def get_by_id(id: int) -> dict | None:
    db = get_db()
    cursor = db.cursor()
    # PT-02: parametro posicional
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
    row = cursor.fetchone()
    return _row_to_dict(row) if row else None


def search(termo: str, categoria: str = None, preco_min: float = None, preco_max: float = None) -> list:
    """PT-02: busca com parametros posicionais — elimina SQL injection da busca dinamica."""
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM produtos WHERE 1=1"
    params = []

    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params.extend(["%" + termo + "%", "%" + termo + "%"])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [_row_to_dict(row) for row in rows]


def inserir(nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> int:
    db = get_db()
    cursor = db.cursor()
    # PT-02: parametros posicionais
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria)
    )
    db.commit()
    return cursor.lastrowid


def atualizar(id: int, nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> bool:
    db = get_db()
    cursor = db.cursor()
    # PT-02: parametros posicionais
    cursor.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, id)
    )
    db.commit()
    return cursor.rowcount > 0


def deletar(id: int) -> bool:
    db = get_db()
    cursor = db.cursor()
    # PT-02: parametro posicional
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
    db.commit()
    return cursor.rowcount > 0


def decrementar_estoque(cursor, produto_id: int, quantidade: int) -> None:
    """Usado internamente por pedido_model ao criar pedido."""
    # PT-02: parametros posicionais
    cursor.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id)
    )


def _row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }
