from app import db
from datetime import datetime
import uuid

class Form(db.Model):
    __tablename__ = 'forms'  # Fixed double asterisks
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # relationship with question
    questions = db.relationship('Question', backref='form', lazy=True)

    # relationship with user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # link token
    link_token = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    def __repr__(self):  # Fixed double asterisks
        return f"<Form {self.title}>"
    
    def to_dict(self):
        """
        Convert the form object to a dictionary.
        Returns: Dictionary containing form data
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'link_token': self.link_token,
            'questions': [question.to_dict() for question in self.questions] if self.questions else []
        }
