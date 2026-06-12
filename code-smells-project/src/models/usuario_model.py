import logging
from database import get_db

logger = logging.getLogger(__name__)


def get_all(limit: int = 100, offset: int = 0) -> list:
    """AP-15: Paginacao adicionada."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios LIMIT ? OFFSET ?", (limit, offset))
    rows = cursor.fetchall()
    return [_row_to_dict(row) for row in rows]


def get_by_id(id: int) -> dict | None:
    db = get_db()
    cursor = db.cursor()
    # PT-02: parametro posicional
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
    row = cursor.fetchone()
    return _row_to_dict(row) if row else None


def get_by_email(email: str) -> dict | None:
    db = get_db()
    cursor = db.cursor()
    # PT-02: parametro posicional — elimina SQL injection do login
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    return _row_to_dict_with_senha(row) if row else None


def inserir(nome: str, email: str, senha_hash: str, tipo: str = "cliente") -> int:
    db = get_db()
    cursor = db.cursor()
    # PT-02: parametros posicionais
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo)
    )
    db.commit()
    return cursor.lastrowid


def _row_to_dict(row) -> dict:
    """Retorna usuario sem expor campo senha."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def _row_to_dict_with_senha(row) -> dict:
    """Usado internamente pelo login para comparar hash."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "senha": row["senha"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }
