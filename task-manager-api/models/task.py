from database import db
from datetime import datetime, timezone
from models.enums import StatusTarefa

_now_utc = lambda: datetime.now(timezone.utc)


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=StatusTarefa.PENDENTE.value)
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=_now_utc)
    updated_at = db.Column(db.DateTime, default=_now_utc, onupdate=_now_utc)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }

    def validate_status(self, new_status):
        return new_status in StatusTarefa.values()

    def validate_priority(self, p):
        return 1 <= p <= 5

    def is_overdue(self):
        """Retorna True se a tarefa está atrasada (due_date no passado e não concluída/cancelada)."""
        if not self.due_date:
            return False
        now = datetime.now(timezone.utc)
        # Normaliza due_date para aware se necessário
        due = self.due_date
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        completed = (self.status == StatusTarefa.CONCLUIDA.value
                     or self.status == StatusTarefa.CANCELADA.value)
        return due < now and not completed
