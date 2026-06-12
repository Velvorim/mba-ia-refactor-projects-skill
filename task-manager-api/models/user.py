from database import db
from datetime import datetime, timezone
import hashlib

# NOTE: SHA-256 é uma melhoria sobre MD5, mas para produção real
# recomenda-se migrar para bcrypt: pip install bcrypt
# e substituir set_password/check_password por bcrypt.hashpw/checkpw.

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, pwd):
        # SHA-256 substitui MD5 (AP-07 fix); migrar para bcrypt em produção
        self.password = hashlib.sha256(pwd.encode()).hexdigest()

    def check_password(self, pwd):
        return self.password == hashlib.sha256(pwd.encode()).hexdigest()

    def is_admin(self):
        return self.role == 'admin'
