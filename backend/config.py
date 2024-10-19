import os

class Config:
        """
        a class for configuration of Flask application
        """
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
