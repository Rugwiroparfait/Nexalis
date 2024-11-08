from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.question import Question
from app.models.form import Form
from app import db

bp = Blueprint('questions', __name__)

@bp.route('/create_question', methods=['POST'])
@jwt_required()
def create_question():
    """
    Create a new question
    ---
    This endpoint creates a new question for a form.
    Payload: JSON object containing the form ID, question text, and type.
    Response: JSON object with the created question.
    """
    data = request.get_json()
    form_id = data.get('form_id')
    text = data.get('text')
    question_type = data.get('type', 'text')  # default to 'text' if not provided

    if not text or not form_id:
        return jsonify({"error": "Form ID and question text are required"}), 400

    # Verify the form belongs to the current user
    user_id = get_jwt_identity()
    form = Form.query.filter_by(id=form_id, user_id=user_id).first()
    if not form:
        return jsonify({"error": "Form not found or unauthorized access"}), 404

    # Create and save the new question
    new_question = Question(form_id=form_id, text=text, question_type=question_type)
    db.session.add(new_question)
    db.session.commit()

    return jsonify({"question": new_question.to_dict()}), 201

@bp.route('/delete_question/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_question(id):
    """
    Delete a question
    ---
    This endpoint deletes a question by its ID if the user owns the form it belongs to.
    Response: JSON message indicating the deletion status.
    """
    user_id = get_jwt_identity()

    # Fetch the question and ensure it belongs to a form owned by the current user
    question = Question.query.get(id)
    if not question or question.form.user_id != user_id:
        return jsonify({"error": "Question not found or unauthorized access"}), 404

    # Delete the question
    db.session.delete(question)
    db.session.commit()

    return jsonify({"message": "Question deleted successfully"}), 200

@bp.route('/<int:form_id>/questions', methods=['GET'])
@jwt_required()
def get_form_questions(form_id):
    """
    Get all questions for a specific form
    ---
    This endpoint retrieves all questions associated with a form if it belongs to the current user.
    Response: JSON object with the list of questions.
    """
    user_id = get_jwt_identity()

    # Verify that the form exists and belongs to the current user
    form = Form.query.filter_by(id=form_id, user_id=user_id).first()
    if not form:
        return jsonify({"error": "Form not found or unauthorized access"}), 404

    # Retrieve questions for the form
    questions = Question.query.filter_by(form_id=form_id).all()
    questions_data = [question.to_dict() for question in questions]

    return jsonify({"questions": questions_data}), 200

# In your questions blueprint file
@bp.route('/public/<int:form_id>/questions', methods=['GET'])
def get_public_questions(form_id):
    """Fetch questions for a form without requiring authentication."""
    questions = Question.query.filter_by(form_id=form_id).all()
    if questions:
        return jsonify({'questions': [question.to_dict() for question in questions]})
    else:
        return jsonify({'error': 'No questions found for this form'}), 404

