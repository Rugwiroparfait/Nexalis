from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# import pytz
db = SQLAlchemy()

# Define the local timezone (Africa/Kigali for Rwanda)
# local_tz = pytz.timezone('Africa/Kigali')

class Form(db.Model):
    __tablename__ = 'forms'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))

    # the UTC is not my time , so this will be changed later
    # The time will be set  in commented lines which will be uncommented
    # timestamp = datetime.now(local_tz)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', backref='form', lazy=True)

    def __repr__(self):
        return f"<Form {self.title}>"

