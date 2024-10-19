from flask import Blueprint

bp = Blueprint('responses', __name__)

@bp.route('/responses', methods=['GET'])
def get_responses():
    return "This is the responses API!"
