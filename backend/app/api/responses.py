from flask import Blueprint
from app.models.response import Response
from app import db

bp = Blueprint('responses', __name__, url_prefix='/responses')

@bp.route('/', methods=['POST'])
def submit_response():
    """
    Submit a response to a form
    ---
    This endpoint allows users to submit responses for a specific form.
    Payload: JSON object containing the form ID and the answers.
    Response: JSON object with the submitted response.
    """
    data = request.get_json()
    form_id = data.get('form_id')
    answers = data.get('answers')


    if not form_id or not answers:
        return jsonify({"error":"Form ID and answers are required"}), 400

    new_response = Response(form_id = form_id, answers=answers)
    db.session.add(new_response)
    db.session.commit()

    return jsonify({"response": new_response.to_dict()}), 201


@bp.route('/<int:id>', methods=['GET'])
def get_response(id):
    """
    Get a form response
    ---
    This endpoint retrieve a specific response by its ID.
    Response: JSON object with the response details.
    """
    response = Response.query.get_or_404(id)

    return jsonify({"response": response.to dict()})


