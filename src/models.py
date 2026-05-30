from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class Task(db.Model):
    """Modelo de Tarefa para o sistema de gerenciamento da TechFlow."""

    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='todo')       # todo | in_progress | done
    priority = db.Column(db.String(10), default='medium')   # low | medium | high
    assignee = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    VALID_STATUSES = ['todo', 'in_progress', 'done']
    VALID_PRIORITIES = ['low', 'medium', 'high']

    def to_dict(self):
        """Converte a tarefa para dicionário serializável em JSON."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'assignee': self.assignee,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f'<Task {self.id}: {self.title} [{self.status}]>'
