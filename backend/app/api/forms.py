from flask import Blueprint

bp = Blueprint('forms', __name__)

@bp.route('/forms', methods=['GET'])
def get_forms():
    return "This is the get form API"
