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
            return jsonify({
                'token': access_token,
                'user_id': user.id,
                'message': 'Login successful'
            }), 200
        else:
            print("Password verification failed.")

    return jsonify({"error": "Invalid credentials"}), 401

@users_bp.route('/get_user', methods=['GET'])
@token_required
def get_user_data(current_user):
    """
    Retrieve current user data.
    ---
    This endpoint returns the user's name and email if they are authenticated.
    Headers: 
        Authorization: Bearer <JWT_TOKEN>
    Response: JSON object with `name` and `email`.
    """
    # Retrieve the user information from the database
    print(request.headers.get('Authorization'))
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'name': user.username,
        'email': user.email
    }), 200

@users_bp.route('/update_user', methods=['PUT'])
@token_required
def update_user_data(current_user):
    """
    Update user data: email, username, and password.
    ---
    This endpoint allows an authenticated user to update their email, username, or password.
    Headers:
        Authorization: Bearer <JWT_TOKEN>
    Payload:
        JSON object with fields `username`, `email`, `password` (optional)
    Response:
        JSON object with success message or error details.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    
    data = request.get_json()
    # Extract data from the request body
    new_username = data.get('username')
    new_email = data.get('email')
    new_password = data.get('password')

    # Update username if provided and check if it already exists
    if new_username:
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != current_user.id:
            return jsonify({'error': 'Username already taken'}), 409
        current_user.username = new_username

    # Update email if provided and check if it already exists
    if new_email:
        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user and existing_user.id != current_user.id:
            return jsonify({'error': 'Email already in use'}), 409
        current_user.email = new_email

    # Update password if provided
    if new_password:
        current_user.set_password(new_password)

    # Commit changes to the database
    db.session.commit()

    return jsonify({'message': 'User data updated successfully'}), 200