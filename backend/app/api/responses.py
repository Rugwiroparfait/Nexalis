from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.response import Response
from app.models.question import Question
from app import db

bp = Blueprint('responses', __name__)

@bp.route('/submit_response', methods=['POST'])
@jwt_required()
def submit_response():
    """
    Submit responses to a form
    ---
    This endpoint allows users to submit responses for specific questions within a form.
    Payload: JSON object containing the form ID and a list of answers.
    Response: JSON object with the submitted responses.
    """
    data = request.get_json()
    form_id = data.get('form_id')
    answers = data.get('answers')  # Expecting a list of answers with question_id and answer text

    if not form_id or not answers:
        return jsonify({"error": "Form ID and answers are required"}), 400

    # Retrieve user ID from the JWT token
    user_id = get_jwt_identity()
    
    # Process each answer in the answers list
    responses = []
    for answer_data in answers:
        question_id = answer_data.get('question_id')
        answer_text = answer_data.get('answer')  # Matches the 'answers' field in the Response model

        # Validate required fields within each answer
        if not question_id or answer_text is None:
            return jsonify({"error": "Each answer must include question_id and answer"}), 400

        # Ensure the question belongs to the specified form
        question = Question.query.filter_by(id=question_id, form_id=form_id).first()
        if not question:
            return jsonify({"error": f"Question with ID {question_id} does not exist in form {form_id}"}), 404

        # Create a new Response instance
        new_response = Response(form_id=form_id, question_id=question_id, answers=answer_text)
        db.session.add(new_response)
        responses.append(new_response)

    # Commit all responses at once
    db.session.commit()

    # Return a list of all responses as confirmation
    return jsonify({"responses": [response.to_dict() for response in responses]}), 201


@bp.route('/get_response/<int:id>', methods=['GET'])
@jwt_required()
def get_response(id):
    """
    Get a form response
    ---
    This endpoint retrieves a specific response by its ID.
    Response: JSON object with the response details.
    """
    response = Response.query.get(id)

    # Provide a meaningful message if the response is not found
    if not response:
        return jsonify({"error": f"Response with ID {id} not found"}), 404

    return jsonify({"response": response.to_dict()}), 200

@bp.route('/submit_public_response', methods=['POST'])
def submit_public_response():
    """
    Submit responses to a form (allows both public and authenticated users).
    """
    data = request.get_json()
    form_id = data.get('form_id')
    answers = data.get('answers')  # Expecting a list of answers with question_id and answer text

    if not form_id or not answers:
        return jsonify({"error": "Form ID and answers are required"}), 400

    # Retrieve user ID from JWT token if available
    user_id = None
    try:
        user_id = get_jwt_identity()
    except Exception:
        pass  # Continue with user_id as None for public access

    # Process each answer in the answers list
    responses = []
    for answer_data in answers:
        question_id = answer_data.get('question_id')
        answer_text = answer_data.get('answer')  # Matches the 'answers' field in the Response model

        # Validate required fields within each answer
        if not question_id or answer_text is None:
            return jsonify({"error": "Each answer must include question_id and answer"}), 400

        # Ensure the question belongs to the specified form
        question = Question.query.filter_by(id=question_id, form_id=form_id).first()
        if not question:
            return jsonify({"error": f"Question with ID {question_id} does not exist in form {form_id}"}), 404

        # Create a new Response instance
        new_response = Response(form_id=form_id, question_id=question_id, answers=answer_text)
        db.session.add(new_response)
        responses.append(new_response)

    # Commit all responses at once
    db.session.commit()

    # Return a list of all responses as confirmation
    return jsonify({"responses": [response.to_dict() for response in responses]}), 201
