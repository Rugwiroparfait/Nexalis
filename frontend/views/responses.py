from flask import render_template, request, redirect, url_for, flash, session
import requests
from .. import bp
from .utils import login_required

@bp.route('/response/<int:form_id>', methods=['GET', 'POST'])
@login_required
def response_view(form_id):
    if request.method == 'GET':
        response = requests.get(
            f'http://127.0.0.1:5000/api/questions/{form_id}/questions',
            headers={'Authorization': f'Bearer {session["token"]}'}
        )
        questions = response.json().get("questions", []) if response.status_code == 200 else []
        return render_template('response.html', questions=questions, form_id=form_id)

    elif request.method == 'POST':
        answers = [{"question_id": int(q), "answer": a} for q, a in zip(request.form.getlist('question_id'), request.form.getlist('answers'))]
        response_data = {'form_id': form_id, 'answers': answers}
        response = requests.post(
            'http://127.0.0.1:5000/api/responses/submit_response',
            headers={'Authorization': f'Bearer {session["token"]}'},
            json=response_data
        )
        flash("Response submitted successfully!" if response.status_code == 201 else "Failed to submit response.", "success" if response.status_code == 201 else "danger")
        return redirect(url_for('frontend.dashboard_view'))

@bp.route('/form/<int:form_id>/responses', methods=['GET'])
@login_required
def view_responses(form_id):
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json'}

    try:
        response = requests.get(
            f'http://127.0.0.1:5000/api/forms/get_response/{form_id}',
            headers=headers
        )

        if response.status_code == 200:
            responses = response.json().get("responses", [])
        else:
            flash("Failed to retrieve responses. Please try again later.", "danger")
            responses = []

    except requests.RequestException:
        flash("Error retrieving responses. Please try again later.", "danger")
        responses = []

    return render_template("view_responses.html", form_id=form_id, responses=responses)

