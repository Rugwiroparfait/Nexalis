from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    """
    Create and configure an instance of Flask application.
    
    This function initializes the Flask application, loads the
    configuration, and registers the necessary blueprints for application.
    Returns:
        Flask: The configured Flask application instance.
    """
    # Initialize the flask app
    app = Flask(__name__)
    
    # load configurations
    app.config.from_object(config_class)
    
    # Initialize the database
    db.init_app(app)
    
    with app.app_context():
        # Import models
        from .models.form import Form
        from .models.question import Question
        from .models.response import Response
        
        # Import blueprints
        from .api.forms import bp as forms_bp
        from .api.questions import bp as questions_bp
        from .api.responses import bp as responses_bp
        
        # Register blueprints
        app.register_blueprint(forms_bp)
        app.register_blueprint(questions_bp)
        app.register_blueprint(responses_bp)
        
        # Create tables
        db.create_all()
    
    return app
