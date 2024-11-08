from flask import render_template, request, redirect, url_for, flash, session
import requests
import csv
from io import StringIO
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


@bp.route('/form/<int:form_id>/responses', methods=['GET'])
@login_required
def view_form_responses(form_id):
    """View form responses in a table format"""
    try:
        headers = {'Authorization': f'Bearer {session["token"]}'}

        # Fetch form information
        form_response = requests.get(f'http://127.0.0.1:5000/api/forms/get_forms/{form_id}', headers=headers)
        form_response.raise_for_status()
        form = form_response.json().get('form')

        # Fetch questions and responses
        questions_response = requests.get(f'http://127.0.0.1:5000/api/questions/{form_id}/questions', headers=headers)
        questions_response.raise_for_status()
        questions = questions_response.json().get('questions', [])

        responses_response = requests.get(f'http://127.0.0.1:5000/api/responses/get_responses/{form_id}', headers=headers)
        responses_response.raise_for_status()
        responses = responses_response.json().get('responses', [])

        # Organize responses in a structured format
        question_texts = [question['text'] for question in questions]
        response_data = []
        for response in responses:
            row = {'Submission Date': datetime.datetime.fromisoformat(response['created_at'].replace('Z', '')).strftime('%Y-%m-%d %H:%M:%S')}
            for answer in response['answers']:
                question_text = next((q['text'] for q in questions if q['id'] == answer['question_id']), None)
                if question_text:
                    row[question_text] = answer['answer']
            response_data.append(row)

        return render_template('view_responses.html', form=form, questions=question_texts, responses=response_data)

    except requests.RequestException as e:
        flash(f"Error retrieving form responses: {str(e)}", "danger")
        return redirect(url_for('frontend.dashboard_view'))

@bp.route('/form/<int:form_id>/responses/csv', methods=['GET'])
@login_required
def export_responses_csv(form_id):
    """Export form responses as CSV"""
    try:
        headers = {'Authorization': f'Bearer {session["token"]}'}

        # Fetch form, questions, and responses data
        form_response = requests.get(f'http://127.0.0.1:5000/api/forms/get_forms/{form_id}', headers=headers)
        form_response.raise_for_status()
        form = form_response.json().get('form')

        questions_response = requests.get(f'http://127.0.0.1:5000/api/questions/{form_id}/questions', headers=headers)
        questions_response.raise_for_status()
        questions = questions_response.json().get('questions', [])

        responses_response = requests.get(f'http://127.0.0.1:5000/api/responses/get_responses/{form_id}', headers=headers)
        responses_response.raise_for_status()
        responses = responses_response.json().get('responses', [])

        # Prepare CSV data
        output = StringIO()
        writer = csv.writer(output)

        # Header row
        headers = ['Response ID', 'Submission Date'] + [q['text'] for q in questions]
        writer.writerow(headers)

        # Data rows
        for response in responses:
            row = [''] * len(headers)
            row[0] = response['id']
            row[1] = datetime.datetime.fromisoformat(response['created_at'].replace('Z', '')).strftime('%Y-%m-%d %H:%M:%S')
            for answer in response['answers']:
                question_text = next((q['text'] for q in questions if q['id'] == answer['question_id']), None)
                if question_text:
                    row[headers.index(question_text)] = answer['answer']
            writer.writerow(row)

        output.seek(0)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        return send_file(
            StringIO(output.getvalue()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'form_{form_id}_responses_{timestamp}.csv'
        )

    except requests.RequestException as e:
        flash(f"Error exporting responses: {str(e)}", "danger")
        return redirect(url_for('frontend.view_form', form_id=form_id))

