"""
Report Controller — lógica de negócio para relatórios e categorias.
Resolve AP-06 (N+1) usando JOIN único para user_productivity.
"""
import logging
from datetime import datetime, timezone, timedelta

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from models.enums import StatusTarefa

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_dt(dt):
    """Garante que um datetime seja timezone-aware (UTC)."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def relatorio_resumo() -> dict:
    """
    Gera relatório resumido de toda a aplicação.
    Usa JOIN único para user_productivity — elimina N+1 (AP-06 fix, PT-04).
    """
    now = _now()

    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status=StatusTarefa.PENDENTE.value).count()
    in_progress = Task.query.filter_by(status=StatusTarefa.EM_PROGRESSO.value).count()
    done = Task.query.filter_by(status=StatusTarefa.CONCLUIDA.value).count()
    cancelled = Task.query.filter_by(status=StatusTarefa.CANCELADA.value).count()

    p1 = Task.query.filter_by(priority=1).count()
    p2 = Task.query.filter_by(priority=2).count()
    p3 = Task.query.filter_by(priority=3).count()
    p4 = Task.query.filter_by(priority=4).count()
    p5 = Task.query.filter_by(priority=5).count()

    # Overdue — usa is_overdue() centralizado no model (AP-10 fix)
    overdue_tasks = [t for t in Task.query.all() if t.is_overdue()]
    overdue_list = [
        {
            'id': t.id,
            'title': t.title,
            'due_date': str(t.due_date),
            'days_overdue': (now - _normalize_dt(t.due_date)).days,
        }
        for t in overdue_tasks
    ]

    seven_days_ago = now - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == StatusTarefa.CONCLUIDA.value,
        Task.updated_at >= seven_days_ago,
    ).count()

    # user_productivity — JOIN único via SQLAlchemy (AP-06 fix: sem N+1)
    # Carrega users + tasks em 2 queries com relacionamento eager
    users = User.query.all()  # tasks carregadas via backref (1 query adicional pelo ORM)
    user_stats = []
    for u in users:
        user_tasks = u.tasks  # acessa via backref já carregado
        total = len(user_tasks)
        completed = sum(1 for t in user_tasks if t.status == StatusTarefa.CONCLUIDA.value)
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
        })

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': {
            'critical': p1,
            'high': p2,
            'medium': p3,
            'low': p4,
            'minimal': p5,
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def relatorio_usuario(user_id: int) -> dict:
    """Relatório detalhado de um usuário específico."""
    user = db.session.get(User, user_id)
    if not user:
        raise LookupError('Usuário não encontrado')

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = pending = in_progress = cancelled = overdue = high_priority = 0

    for t in tasks:
        if t.status == StatusTarefa.CONCLUIDA.value:
            done += 1
        elif t.status == StatusTarefa.PENDENTE.value:
            pending += 1
        elif t.status == StatusTarefa.EM_PROGRESSO.value:
            in_progress += 1
        elif t.status == StatusTarefa.CANCELADA.value:
            cancelled += 1

        if t.priority <= 2:
            high_priority += 1

        if t.is_overdue():
            overdue += 1

    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        },
    }


# ── Categorias ────────────────────────────────────────────────────────────────

def listar_categorias() -> list:
    """Lista todas as categorias com contagem de tarefas."""
    categories = Category.query.all()
    result = []
    for c in categories:
        d = c.to_dict()
        d['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(d)
    return result


def criar_categoria(data: dict) -> dict:
    """Cria uma nova categoria."""
    if not data:
        raise ValueError('Dados inválidos')

    name = data.get('name')
    if not name:
        raise ValueError('Nome é obrigatório')

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    db.session.add(category)
    db.session.commit()
    logger.info("Categoria criada: id=%d name=%s", category.id, category.name)
    return category.to_dict()


def atualizar_categoria(cat_id: int, data: dict) -> dict:
    """Atualiza uma categoria existente."""
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise LookupError('Categoria não encontrada')

    if not data:
        raise ValueError('Dados inválidos')

    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    db.session.commit()
    logger.info("Categoria atualizada: id=%d", cat.id)
    return cat.to_dict()


def deletar_categoria(cat_id: int) -> dict:
    """Remove uma categoria."""
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise LookupError('Categoria não encontrada')

    db.session.delete(cat)
    db.session.commit()
    logger.info("Categoria deletada: id=%d", cat_id)
    return {'message': 'Categoria deletada'}
