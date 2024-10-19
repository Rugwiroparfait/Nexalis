from flask import Flask

def create_app():
    """
    Create and configure an instance of Flask application.
    
    This function initializes the Flask application, loads the
    configuraionm and registers the neccessary blueprints for application.

    Returns:
        Flask: The configured Flask application instance.
    """

    # Initialize the flask app
    app = Flask(__name__)

    # load configurations from /backend/config.py (in Config class)
    app.config.from_object('config.Config')

    # importing and registering blueprints
    from .api import forms, questions, responses

    # Registering BPs
    app.register_blueprint(forms.bp)
    app.register_blueprint(questions.bp)
    app.register_blueprint(responses.bp)

    return app

app = create_app()
