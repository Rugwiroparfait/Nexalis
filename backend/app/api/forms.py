from flask import Blueprint, request, jsonify
from app.models.form import Form
from app import db

bp = Blueprint('forms', __name__)

@bp.route('/', methods=['POST'])
def create_form():
    """
    Create a new form
    ___
    this endpoint creates an new form
    Payload: JSON object containing form title and description.
    Response: JSON object containing the created form.
    """
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')


    if not title:
        return jsonify({"Error": "Title is required"}), 400

    new_form = Form(title=title, description=description)
    db.session.add(new_form)
    db.session.commit()

    return jsonify({"form": new_form.to_dict()}), 201


@bp.route('/<int:id>', methods=['PUT'])
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

@bp.route('/<int:ind>', methods=['DELETE'])
def delete_form(id):
    """
    Delete a form
    ---
    This endpoint deletes a form bt its ID.
    Response: JSON message indicating the deletion status.
    """
    form = Form.query.get_or_404(id)

    db.session.delete(form)
    db.session.commit()

    return jsonify({"message": "Form deleted successfully"})
