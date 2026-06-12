"""
Task Controller — lógica de negócio para o domínio Task.
Não importa Flask diretamente; recebe dados validados e delega ao model/ORM.
"""
import logging
from datetime import datetime, timezone

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from models.enums import StatusTarefa

logger = logging.getLogger(__name__)


def _enrich_task(task: Task) -> dict:
    """Serializa uma Task adicionando overdue, user_name e category_name."""
    data = task.to_dict()
    data['overdue'] = task.is_overdue()

    if task.user_id:
        user = db.session.get(User, task.user_id)
        data['user_name'] = user.name if user else None
    else:
        data['user_name'] = None

    if task.category_id:
        cat = db.session.get(Category, task.category_id)
        data['category_name'] = cat.name if cat else None
    else:
        data['category_name'] = None

    return data


def listar_tasks() -> list:
    """Retorna todas as tarefas enriquecidas."""
    tasks = Task.query.all()
    return [_enrich_task(t) for t in tasks]


def buscar_task(task_id: int) -> dict:
    """Retorna uma tarefa pelo ID ou levanta ValueError se não encontrada."""
    task = db.session.get(Task, task_id)
    if not task:
        raise ValueError('Task não encontrada')
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def criar_task(data: dict) -> dict:
    """
    Cria uma nova tarefa.
    Levanta ValueError para dados inválidos, LookupError para entidades não encontradas.
    """
    if not data:
        raise ValueError('Dados inválidos')

    title = data.get('title', '').strip()
    if not title:
        raise ValueError('Título é obrigatório')
    if len(title) < 3:
        raise ValueError('Título muito curto')
    if len(title) > 200:
        raise ValueError('Título muito longo')

    status = data.get('status', StatusTarefa.PENDENTE.value)
    if status not in StatusTarefa.values():
        raise ValueError('Status inválido')

    priority = data.get('priority', 3)
    if not isinstance(priority, int) or priority < 1 or priority > 5:
        raise ValueError('Prioridade deve ser entre 1 e 5')

    user_id = data.get('user_id')
    if user_id:
        if not db.session.get(User, user_id):
            raise LookupError('Usuário não encontrado')

    category_id = data.get('category_id')
    if category_id:
        if not db.session.get(Category, category_id):
            raise LookupError('Categoria não encontrada')

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get('due_date')
    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except (ValueError, TypeError):
            raise ValueError('Formato de data inválido. Use YYYY-MM-DD')

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    logger.info("Task criada: id=%d title=%s", task.id, task.title)
    return task.to_dict()


def atualizar_task(task_id: int, data: dict) -> dict:
    """
    Atualiza uma tarefa existente.
    Levanta ValueError para dados inválidos, LookupError para entidade não encontrada.
    """
    task = db.session.get(Task, task_id)
    if not task:
        raise LookupError('Task não encontrada')

    if not data:
        raise ValueError('Dados inválidos')

    if 'title' in data:
        title = data['title']
        if len(title) < 3:
            raise ValueError('Título muito curto')
        if len(title) > 200:
            raise ValueError('Título muito longo')
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in StatusTarefa.values():
            raise ValueError('Status inválido')
        task.status = data['status']

    if 'priority' in data:
        p = data['priority']
        if not isinstance(p, int) or p < 1 or p > 5:
            raise ValueError('Prioridade deve ser entre 1 e 5')
        task.priority = p

    if 'user_id' in data:
        if data['user_id']:
            if not db.session.get(User, data['user_id']):
                raise LookupError('Usuário não encontrado')
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id']:
            if not db.session.get(Category, data['category_id']):
                raise LookupError('Categoria não encontrada')
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                raise ValueError('Formato de data inválido')
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    logger.info("Task atualizada: id=%d", task.id)
    return task.to_dict()


def deletar_task(task_id: int) -> dict:
    """Remove uma tarefa. Levanta LookupError se não encontrada."""
    task = db.session.get(Task, task_id)
    if not task:
        raise LookupError('Task não encontrada')
    db.session.delete(task)
    db.session.commit()
    logger.info("Task deletada: id=%d", task_id)
    return {'message': 'Task deletada com sucesso'}


def pesquisar_tasks(query: str = '', status: str = '', priority: str = '', user_id: str = '') -> list:
    """Filtra tarefas por múltiplos critérios."""
    q = Task.query

    if query:
        q = q.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%')
            )
        )
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == int(priority))
    if user_id:
        q = q.filter(Task.user_id == int(user_id))

    return [t.to_dict() for t in q.all()]


def estatisticas_tasks() -> dict:
    """Retorna estatísticas agregadas de tarefas."""
    total = Task.query.count()
    pending = Task.query.filter_by(status=StatusTarefa.PENDENTE.value).count()
    in_progress = Task.query.filter_by(status=StatusTarefa.EM_PROGRESSO.value).count()
    done = Task.query.filter_by(status=StatusTarefa.CONCLUIDA.value).count()
    cancelled = Task.query.filter_by(status=StatusTarefa.CANCELADA.value).count()

    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())

    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
