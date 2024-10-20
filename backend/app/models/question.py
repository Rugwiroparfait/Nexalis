from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    form_id = db.Column(db.Integer. db.Foreignkey('forms.id'), nullable=False)

    responses = db.relationship('Response', backref='question', lazy=True)

    def __repr__(self):
        return f"<Question {self.text}>"
