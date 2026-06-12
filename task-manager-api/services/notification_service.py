"""
Notification Service — envio de emails e registro de notificações.
Credenciais SMTP lidas da configuração centralizada (variáveis de ambiente).
"""
import logging
import smtplib
from datetime import datetime, timezone

from config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.notifications = []
        # AP-02 fix: credenciais lidas de variáveis de ambiente via config/settings.py
        self.email_host = settings.EMAIL_HOST
        self.email_port = settings.EMAIL_PORT
        self.email_user = settings.EMAIL_USER
        self.email_password = settings.EMAIL_PASSWORD

    def send_email(self, to: str, subject: str, body: str) -> bool:
        if not self.email_user or not self.email_password:
            logger.warning("Email não configurado — EMAIL_USER/EMAIL_PASSWORD ausentes.")
            return False
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            logger.info("Email enviado para %s", to)
            return True
        except Exception as e:
            logger.error("Erro ao enviar email: %s", e, exc_info=True)
            return False

    def notify_task_assigned(self, user, task) -> None:
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': datetime.now(timezone.utc),
        })

    def notify_task_overdue(self, user, task) -> None:
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id: int) -> list:
        return [n for n in self.notifications if n['user_id'] == user_id]
