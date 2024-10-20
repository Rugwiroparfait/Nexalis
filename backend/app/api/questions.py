from flask import Blueprint, request, jsonify
from app.models.question import Question
from app import db

bp = Blueprint('questions', __name__, url_prefix='/questions')

@bp.route('/', methods=['POST'])
def create_question():
    """
    Create a new questions
    ---
    This endpoint creates a new question for a form.
    Payload: JSON object containing the form ID, question text, and type.
    Response: JSON object with the created question.
    """
    data = request.get_json()
    form_id = data.get('form_id')
    text = data.get('text')
    question_type = data.get('type')

    if not text or not form_id:
        return jsonify({"error": "Form ID and question text are required"}), 400

    new_question = Question(form_id=form_id, text=text, type=question_type)
    db.session.add(new_question)
    db.session.commit()
    return jsonify({"question": new_question.to_dict()}), 201

@bp.route('<int:id>', methods=['DELETE'])
def delete_quetion(id):
    """
    Delete a question
    ---
    This endpoint deletes a question by its ID.
    Response: JSON message indicating the deletion status.
    """
    question = Question.query.get_or_404(id)

    db.session.delete(question)
    db.session.commit()

    return jsonify({"message":"Question delete successfully"})
