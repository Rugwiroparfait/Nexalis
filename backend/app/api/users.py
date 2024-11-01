from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
from app.utils.auth import hash_password, verify_password, generate_token, decode_token
from datetime import datetime


users_bp = Blueprint('users', __name__)

@users_bp.route('/signup', methods=['POST'])
def signup():
    """User registration API."""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if email or username already exists
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 409

    #  Create a new user
    new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            created_at=datetime.utcnow()
            )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}),201

@users_bp.route('/login', methods=['POST'])
def login():
    """User login API."""
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'error':'Missing required fields'}), 400

    user = User.query.filter_by(email=email).first()

    if user and verify_password(user.password_hash, password):
        # generate token
        token = generate_token(user.id)
        return jsonify({'token': token, 'user_id': user.id}), 200
    else:
        return jsonify({'error':'Invalid email or password'}), 401

@users_bp.route('/user', methods=['GET'])
def get_user_info():
    """Get user details API."""
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'error':'Token is missing'}), 403

    user_id = decode_token(token)

    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 403

    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user.to_dict()), 200
