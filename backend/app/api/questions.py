from flask import Blueprint

bp = Blueprint('questions', __name__)

@bp.route('/questions', methods=['GET'])
def get_questions():
    return "This is the questions API!"
