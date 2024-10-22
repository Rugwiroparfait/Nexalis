from app import db

class Response(db.Model):
    __tablename__ = 'responses'
    
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answers = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Response {self.answers}>"

    def to_dict(self):
        return {
            "id": self.id,
            "form_id": self.form_id,
            "question_id": self.question_id,
            "answers": self.answers
        }
