from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

# Test route
@app.route('/')
def hello():
    return "Welcome to Nexalis!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
