"""
Enums centralizados para magic strings do domínio Task Manager.
Use sempre os valores deste módulo em vez de strings literais espalhadas no código.
"""
from enum import Enum


class StatusTarefa(Enum):
    """Status possíveis de uma tarefa."""
    PENDENTE = 'pending'
    EM_PROGRESSO = 'in_progress'
    CONCLUIDA = 'done'
    CANCELADA = 'cancelled'

    @classmethod
    def values(cls):
        """Retorna lista de valores string válidos."""
        return [s.value for s in cls]


class StatusUsuario(Enum):
    """Roles possíveis de um usuário."""
    USER = 'user'
    ADMIN = 'admin'
    MANAGER = 'manager'

    @classmethod
    def values(cls):
        """Retorna lista de valores string válidos."""
        return [r.value for r in cls]
