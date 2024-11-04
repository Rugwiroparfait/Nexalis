from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.form import Form
from app.models.question import Question
from app import db
from datetime import datetime

bp = Blueprint('forms', __name__)

@bp.route('/get_form', methods=['GET'])
@jwt_required()
def get_forms():
    """
    Get all forms for the current user
    ---
    This endpoint retrieves all forms created by the current user.
    Response: JSON array containing all forms.
    """
    user_id = get_jwt_identity()
    forms = Form.query.filter_by(user_id=user_id).all()
    return jsonify({"forms": [form.to_dict() for form in forms]})

@bp.route('/get_form/<int:id>', methods=['GET'])
@jwt_required()
def get_form(id):
    """
    Get a single form created by the current user
    ---
    This endpoint retrieves a form by its ID if it belongs to the current user.
    Response: JSON object containing the form details.
    """
    user_id = get_jwt_identity()
    form = Form.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify({"form": form.to_dict()})

@bp.route('/create_form', methods=['POST'])
@jwt_required()
def create_form():
    """
    Create a new form
    ---
    This endpoint creates a new form for the current user.
    Payload: JSON object containing form title and description.
    Response: JSON object containing the created form.
    """
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    questions_data = data.get('questions', [])
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    # Get the current user's identity (user_id) from the JWT token
    user_id = get_jwt_identity()
    new_form = Form(title=title, description=description, user_id=user_id)
    db.session.add(new_form)
    db.session.commit()
    db.session.flush()

    # Add questions if provided
    questions = []
    for question_data in questions_data:
        question_text = question_data.get('text')
        question_type = question_data.get('type', 'text')
        if question_text:
            question = Question(text=question_text, question_type=question_type, form_id=new_form.id)
            questions.append(question)

    db.session.add_all(questions)
    db.session.commit()
    return jsonify({"form": new_form.to_dict(), "link_token": new_form.link_token}), 201

@bp.route('/update_form/<int:id>', methods=['PUT'])
@jwt_required()
def update_form(id):
    """
    Update an existing form created by the current user
    ---
    This endpoint updates a form by ID if it belongs to the current user.
    Payload: JSON object containing updated form title and description.
    Response: JSON object with the updated form details.
    """
    user_id = get_jwt_identity()
    form = Form.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    data = request.get_json()
    form.title = data.get('title', form.title)
    form.description = data.get('description', form.description)
    
    db.session.commit()
    return jsonify({"form": form.to_dict()})

@bp.route('/delete_form/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_form(id):
    """
    Delete a form created by the current user
    ---
    This endpoint deletes a form by its ID if it belongs to the current user.
    Response: JSON message indicating the deletion status.
    """
    user_id = get_jwt_identity()
    form = Form.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(form)
    db.session.commit()
    
    return jsonify({"message": "Form deleted successfully"})

@bp.route('/link/<string:link_token>', methods=['GET'])
def get_form_by_link(link_token):
    """
    Get a form by its unique link token (public access)
    ---
    This endpoint retrieves a form using its unique link token.
    Response: JSON object containing the form details.
    """
    form = Form.query.filter_by(link_token=link_token).first_or_404()
    return jsonify({"form": form.to_dict()})

@bp.route('/list_forms', methods=['GET'])
@jwt_required()
def list_forms():
    """
    List all forms with details for the current user
    ---
    This endpoint retrieves all forms for the current user, including the form ID and questions.
    """
    user_id = get_jwt_identity()
    forms = Form.query.filter_by(user_id=user_id).options(db.joinedload(Form.questions)).all()
    return jsonify({
        "forms": [form.to_dict(include_questions=True) for form in forms]
    })

