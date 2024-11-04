from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app import db
from app.utils.auth import hash_password, verify_password, generate_token, decode_token, token_required
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

    # Create a new user
    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        created_at=datetime.utcnow()
    )
    new_user.set_password(password)
    print(f"Signup - Password Hash for {username}: {new_user.password_hash}")

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@users_bp.route('/login', methods=['POST'])
def login():
    """
    User login route
    ---
    This endpoint authenticates a user and returns a JWT access token.
    Payload: JSON object containing `email` and `password`.
    Response: JSON object with `access_token` if authentication is successful.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        print(f"Login - Password Hash in DB: {user.password_hash}")
        print(f"Login - Password Entered: {password}")
        if user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token), 200
        else:
            print("Password verification failed.") 
    return jsonify({"error": "Invalid credentials"}), 401

@users_bp.route('/user', methods=['GET'])
@token_required
def get_user_info(current_user):
    """Get user details API."""
    return jsonify(current_user.to_dict()), 200

@users_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Retrieve user profile information."""
    return jsonify({
        'name': current_user.username,
        'email': current_user.email
    }), 200

@users_bp.route('/update', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile information."""
    data = request.get_json()
    username = data.get('username', current_user.username)
    email = data.get('email', current_user.email)

    # Check if the new email or username is taken by another user
    if User.query.filter(User.username == username, User.id != current_user.id).first():
        return jsonify({'error': 'Username is already taken'}), 409
    if User.query.filter(User.email == email, User.id != current_user.id).first():
        return jsonify({'error': 'Email is already registered'}), 409

    current_user.username = username
    current_user.email = email

    if 'password' in data and data['password']:
        current_user.password_hash = hash_password(data['password'])

    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

