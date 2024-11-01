from app import db

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    responses = db.relationship('Response', backref='question', lazy=True)

    def __repr__(self):
        return f"<Question {self.text}>"

    def to_dict(self):
        """
        Convert the question object to a dictionary.
        Returns: Dictionary containing question data.
        """
        return {
            'id': self.id,
            'text': self.text,
            'question_type': self.question_type,
            'form_id': self.form_id,
            'responses': [response.to_dict() for response in self.responses] if self.responses else []
        }

