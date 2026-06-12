"""
User Controller — lógica de negócio para o domínio User.
Não importa Flask diretamente; recebe dados validados e delega ao model/ORM.
"""
import logging
import re
import secrets

from database import db
from models.user import User
from models.task import Task
from models.enums import StatusUsuario

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')


def _gerar_token(user: User) -> str:
    """
    Gera um token de sessão baseado em secrets.token_hex.
    NOTE: Para autenticação real em produção, migrar para JWT (PyJWT)
    com expiração e assinatura usando SECRET_KEY.
    """
    return secrets.token_hex(32)


def listar_usuarios() -> list:
    """Retorna todos os usuários com contagem de tarefas."""
    users = User.query.all()
    result = []
    for u in users:
        d = {
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'active': u.active,
            'created_at': str(u.created_at),
            'task_count': len(u.tasks),
        }
        result.append(d)
    return result


def buscar_usuario(user_id: int) -> dict:
    """Retorna um usuário com suas tarefas. Levanta LookupError se não encontrado."""
    user = db.session.get(User, user_id)
    if not user:
        raise LookupError('Usuário não encontrado')

    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data['tasks'] = [t.to_dict() for t in tasks]
    return data


def criar_usuario(data: dict) -> dict:
    """
    Cria um novo usuário.
    Levanta ValueError para dados inválidos, LookupError para conflitos.
    """
    if not data:
        raise ValueError('Dados inválidos')

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        raise ValueError('Nome é obrigatório')
    if not email:
        raise ValueError('Email é obrigatório')
    if not password:
        raise ValueError('Senha é obrigatória')

    if not _EMAIL_RE.match(email):
        raise ValueError('Email inválido')

    if len(password) < 4:
        raise ValueError('Senha deve ter no mínimo 4 caracteres')

    if User.query.filter_by(email=email).first():
        raise LookupError('Email já cadastrado')

    if role not in StatusUsuario.values():
        raise ValueError('Role inválido')

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    db.session.add(user)
    db.session.commit()
    logger.info("Usuário criado: id=%d name=%s", user.id, user.name)
    return user.to_dict()


def atualizar_usuario(user_id: int, data: dict) -> dict:
    """Atualiza campos de um usuário existente."""
    user = db.session.get(User, user_id)
    if not user:
        raise LookupError('Usuário não encontrado')

    if not data:
        raise ValueError('Dados inválidos')

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not _EMAIL_RE.match(data['email']):
            raise ValueError('Email inválido')
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise LookupError('Email já cadastrado')
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < 4:
            raise ValueError('Senha muito curta')
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in StatusUsuario.values():
            raise ValueError('Role inválido')
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    logger.info("Usuário atualizado: id=%d", user.id)
    return user.to_dict()


def deletar_usuario(user_id: int) -> dict:
    """Remove um usuário e suas tarefas associadas."""
    user = db.session.get(User, user_id)
    if not user:
        raise LookupError('Usuário não encontrado')

    tasks = Task.query.filter_by(user_id=user_id).all()
    for t in tasks:
        db.session.delete(t)

    db.session.delete(user)
    db.session.commit()
    logger.info("Usuário deletado: id=%d", user_id)
    return {'message': 'Usuário deletado com sucesso'}


def tarefas_do_usuario(user_id: int) -> list:
    """Retorna tarefas de um usuário com indicador de overdue."""
    user = db.session.get(User, user_id)
    if not user:
        raise LookupError('Usuário não encontrado')

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for t in tasks:
        d = {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'created_at': str(t.created_at),
            'due_date': str(t.due_date) if t.due_date else None,
            'overdue': t.is_overdue(),
        }
        result.append(d)
    return result


def login(email: str, password: str) -> dict:
    """
    Autentica um usuário.
    Retorna dict com user e token.
    Levanta ValueError para credenciais inválidas, PermissionError para usuário inativo.
    """
    if not email or not password:
        raise ValueError('Email e senha são obrigatórios')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise ValueError('Credenciais inválidas')

    if not user.active:
        raise PermissionError('Usuário inativo')

    token = _gerar_token(user)
    logger.info("Login realizado: user_id=%d", user.id)
    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': token,
    }
