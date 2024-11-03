from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.form import Form
from app.models.question import Question
from app import db


bp = Blueprint('forms', __name__)

# Add GET all forms route
@bp.route('/get_form', methods=['GET'])
def get_forms():
    """
    Get all forms
    ---
    This endpoint retrieves all forms.
    Response: JSON array containing all forms.
    """
    forms = Form.query.all()
    return jsonify({"forms": [form.to_dict() for form in forms]})

# Add GET single form route
@bp.route('/get_form/<int:id>', methods=['GET'])
def get_form(id):
    """
    Get a single form
    ---
    This endpoint retrieves a form by its ID.
    Response: JSON object containing the form details.
    """
    form = Form.query.get_or_404(id)
    return jsonify({"form": form.to_dict()})

@bp.route('/create_form', methods=['POST'])
# @jwt_required()
def create_form():
    """
    Create a new form
    ---
    This endpoint creates a new form
    Payload: JSON object containing form title and description.
    Response: JSON object containing the created form.
    """
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    user_id = data.get('user_id')
    questions_data = data.get('questions', [])
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
    # Get the current user's identity (user_id) from the JWT token
    # user_id = get_jwt_identity()
    new_form = Form(title=title, description=description, user_id=user_id)
    db.session.add(new_form)
    db.session.commit()
    db.session.flush()

    # Add questions if provided
    questions = []
    for question_data in questions_data:
        question_text = question_data.get('text')
        question_type = question_data.get('text', 'text')
        if question_text:
            question = Question(text=question_text,question_type=question_type, form_id=new_form.id)
            questions.append(question)

    db.session.add_all(questions)
    db.session.commit()
    return jsonify({"form": new_form.to_dict(), "link_token": new_form.link_token}), 201

@bp.route('/update_form/<int:id>', methods=['PUT'])
def update_form(id):
    """
    Update an existing form
    ---
    This endpoint updates an existing form by ID.
    Payload: JSON object containing updated form title and description.
    Response: JSON object with the updated form details.
    """
    form = Form.query.get_or_404(id)
    data = request.get_json()
    
    form.title = data.get('title', form.title)
    form.description = data.get('description', form.description)
    
    db.session.commit()
    return jsonify({"form": form.to_dict()})

@bp.route('delete_form/<int:id>', methods=['DELETE'])
def delete_form(id):
    """
    Delete a form
    ---
    This endpoint deletes a form by its ID.
    Response: JSON message indicating the deletion status.
    """
    form = Form.query.get_or_404(id)
    db.session.delete(form)
    db.session.commit()
    
    return jsonify({"message": "Form deleted successfully"})

@bp.route('/link/<string:link_token>', methods=['GET'])
def get_form_by_link(link_token):
    """
    Get a form by its unique link token.
    ---
    This endpoint retrieves a form using its unique link token.
    Response: JSON object containing the form details.
    """
    form = Form.query.filter_by(link_token=link_token).first_or_404()
    return jsonify({"form": form.to_dict()})

