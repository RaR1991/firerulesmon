from app import db
from flask_login import UserMixin
import enum

class UserRole(enum.Enum):
    VIEWER = 'viewer'
    EDITOR = 'editor'
    ADMIN = 'admin'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.VIEWER, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
