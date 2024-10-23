from app import db
from datetime import datetime

class User(db.model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Form (one-to-many)
    forms = db.relationship('Form', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        """
        Convert the user object to dictionary.
        Returns: Dictionary containing user data
        """
        return {
            'id': self.id
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'forms': [form.to_dict() for form in self.forms] if self.forms else []
            }
