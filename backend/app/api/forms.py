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
    Get all forms for the current user with optional pagination.
    """
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    forms = Form.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "status": "success",
        "forms": [form.to_dict() for form in forms.items],
        "total": forms.total,
        "page": forms.page,
        "pages": forms.pages
    }), 200

@bp.route('/get_forms/<int:id>', methods=['GET'])
@jwt_required()
def get_form(id):
    """
    Get a single form created by the current user by form ID.
    """
    user_id = get_jwt_identity()
    form = Form.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify({
        "status": "success",
        "form": form.to_dict()
    }), 200

@bp.route('/create_form', methods=['POST'])
@jwt_required()
def create_form():
    """
    Create a new form for the current user.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status":"error", "message": "No data is provided"}), 400
        title = data.get('title')
        description = data.get('description')
        questions_data = data.get('questions', [])

        if not title:
            return jsonify({"status": "error", "message": "Title is required"}), 400
        
        if not isinstance(questions_data, list):
            return jsonify({"status": "error", "message": "Questions must be a list"}), 400

        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        new_form = Form(title=title, description=description, user_id=user_id)
        db.session.add(new_form)
        db.session.flush()

        # Add questions if provided
        questions = []
        for question_data in questions_data:
            # Validate question format
            question_text = question_data.get('text')
            question_type = question_data.get('type', 'text')  # Default to 'text' if type is not provided
            
            if not question_text:
                return jsonify({"status": "error", "message": "Each question must have text"}), 400
            
            # Ensure question_type is a valid value if your app has specific types
            if question_type not in ['text', 'multiple_choice', 'checkbox']:
                return jsonify({"status": "error", "message": f"Invalid question type '{question_type}'"}), 400

            # Create the question object
            question = Question(text=question_text, question_type=question_type, form_id=new_form.id)
            questions.append(question)

        # Add questions to the session and commit all changes
        db.session.add_all(questions)
        db.session.commit()

        # Return the success response
        return jsonify({
            "status": "success",
            "form": new_form.to_dict(),
            "link_token": new_form.link_token
        }), 201

    except Exception as e:
        # Roll back the session in case of any exception
        db.session.rollback()
        print(f"Error creating form: {e}")  # For debugging purposes
        return jsonify({"status": "error", "message": "Failed to create form due to an unexpected error"}), 500

@bp.route('/update_forms/<int:id>', methods=['PUT'])
@jwt_required()
def update_form(id):
    """
    Update an existing form created by the current user by form ID.
    """
    try:
        user_id = get_jwt_identity()
        form = Form.query.filter_by(id=id, user_id=user_id).first_or_404()

        data = request.get_json()
        if 'title' in data:
            form.title = data['title']
        if 'description' in data:
            form.description = data['description']

        db.session.commit()
        return jsonify({
            "status": "success",
            "form": form.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Failed to update form"}), 500

@bp.route('/delete_form/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_form(id):
    """
    Delete a form created by the current user by form ID.
    """
    try:
        user_id = get_jwt_identity()
        form = Form.query.filter_by(id=id, user_id=user_id).first_or_404()
        db.session.delete(form)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Form deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Failed to delete form"}), 500

@bp.route('/forms/link/<string:link_token>', methods=['GET'])
def get_form_by_link(link_token):
    """
    Get a form by its unique link token (public access).
    """
    form = Form.query.filter_by(link_token=link_token).first_or_404()
    return jsonify({
        "status": "success",
        "form": form.to_dict()
    }), 200

@bp.route('/forms/detailed', methods=['GET'])
@jwt_required()
def list_forms():
    """
    List all forms with details (including questions) for the current user.
    """
    user_id = get_jwt_identity()
    forms = Form.query.filter_by(user_id=user_id).options(db.joinedload(Form.questions)).all()
    return jsonify({
        "status": "success",
        "forms": [form.to_dict(include_questions=True) for form in forms]
    }), 200

