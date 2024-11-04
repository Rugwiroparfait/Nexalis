from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    forms = db.relationship('Form', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        """Hashes the password and stores it in password_hash."""
        self.password_hash = generate_password_hash(password)

    # Property for setting password: hashes it automatically
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to check if a password matches the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_forms=False):
        """
        Convert the user object to dictionary.
        Args:
            include_forms (bool): Whether to include user's forms in the output
        Returns:
            dict: Dictionary containing user data
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_forms:
            data['forms'] = [form.to_dict() for form in self.forms]
        return data

