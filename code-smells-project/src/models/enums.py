from enum import Enum

# PT-07: Magic strings substituidas por Enum tipado
class StatusPedido(Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"

class TipoUsuario(Enum):
    CLIENTE = "cliente"
    ADMIN = "admin"

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
