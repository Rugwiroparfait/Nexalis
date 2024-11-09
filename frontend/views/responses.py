from flask import render_template, session, flash, send_file, request, redirect, url_for
import requests
import csv
import datetime
from io import StringIO, BytesIO
from .. import bp
from .utils import login_required

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
        
        # Handle missing form data
        if not form:
            flash("Form data could not be retrieved or does not exist.", "danger")
            return redirect(url_for('frontend.dashboard_view'))

        # Fetch questions along with responses using the new API
        questions_response = requests.get(f'http://127.0.0.1:5000/api/questions/{form_id}/questions', headers=headers)
        questions_response.raise_for_status()
        questions = questions_response.json().get('questions', [])

        # Organize responses in a structured format
        question_texts = [question['text'] for question in questions]
        response_data = []

        for question in questions:
            for response in question.get('responses', []):
                # Initialize row data
                row = {'Submission Date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                row[question['text']] = response.get('answers', 'N/A')  # Access answer with a default fallback
                response_data.append(row)

        # Render the template with form, questions, and responses data
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

        # Prepare CSV data using StringIO
        csv_output = StringIO()
        writer = csv.writer(csv_output)

        # Header row
        headers = ['Response ID', 'Submission Date'] + [q['text'] for q in questions if isinstance(q, dict) and 'text' in q]
        writer.writerow(headers)

        # Data rows
        for response in responses:
            row = [''] * len(headers)
            row[0] = response.get('id', "N/A")
            row[1] = datetime.datetime.fromisoformat(response.get('created_at', '').replace('Z', '')).strftime('%Y-%m-%d %H:%M:%S') if response.get('created_at') else "N/A"

            # Ensure answers are in the correct format
            answers = response.get('answers', [])
            if not isinstance(answers, list):
                continue  # Skip if answers is not a list

            for answer in answers:
                if not isinstance(answer, dict):  # Check if answer is a dictionary
                    continue

                question_id = answer.get('question_id')
                if question_id is None:
                    continue  # Skip if no question ID

                question_text = next((q['text'] for q in questions if isinstance(q, dict) and q.get('id') == question_id), None)
                if question_text:
                    row[headers.index(question_text)] = answer.get('answer', "N/A")

            writer.writerow(row)

        # Convert the CSV text data to bytes
        csv_output.seek(0)
        output = BytesIO(csv_output.getvalue().encode('utf-8'))

        # Set a filename with the current timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'form_{form_id}_responses_{timestamp}.csv'

        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except requests.RequestException as e:
        flash(f"Error exporting responses: {str(e)}", "danger")
        return redirect(url_for('frontend.view_form', form_id=form_id))
