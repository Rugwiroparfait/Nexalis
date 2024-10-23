from app import create_app
# from app.models import db, Form, Question, Response
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
