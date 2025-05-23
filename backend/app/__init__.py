from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


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
    jwt.init_app(app)
    
    # Initialize the database
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Import models
        from .models.form import Form
        from .models.question import Question
        from .models.response import Response
        from .models.user import User

        # Import blueprints
        from .api.forms import bp as forms_bp
        from .api.questions import bp as questions_bp
        from .api.responses import bp as responses_bp
        from .api.users import  users_bp

        # Import frontend blueprint
        from frontend.views import bp as frontend_bp

        
        # Register blueprints
        app.register_blueprint(forms_bp, url_prefix='/api/forms')
        app.register_blueprint(questions_bp, url_prefix='/api/questions')
        app.register_blueprint(responses_bp, url_prefix='/api/responses')
        app.register_blueprint(users_bp, url_prefix='/api/users')

        # Register frontend blueprint without prefix
        app.register_blueprint(frontend_bp)
        # Create tables
        db.create_all()
    
    return app
