from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from app import create_app
from flask import current_app

SECRET_KEY = current_app.config['SECRET_KEY']

# hashing password
def hash_password(password):
    """Hash the user's password."""
    return generate_password_hash(password)


def verify_password(hash, password):
    """ verify if user passsword matches the current password """
    return check_password_hash(hash, password)


def generate_token(user_id):
    """Generate JWT token for the user."""
    payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
            }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """Decode the JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None

