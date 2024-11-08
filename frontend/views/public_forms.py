# frontend/views/public_forms.py
from flask import render_template, request, flash, session, send_file, redirect, url_for
import requests
from io import StringIO
import csv
import datetime
from .. import bp
from .utils import login_required

@bp.route('/p/<int:form_id>', methods=['GET', 'POST'])
def public_form_view(form_id):
    """Public view for users to fill out forms - no login required"""
    try:
        form_response = requests.get(f'http://127.0.0.1:5000/api/forms/public/{form_id}')
        form_response.raise_for_status()
        form = form_response.json().get('form')
        
        if not form:
            return render_template('error.html', message="Form not found or is no longer active."), 404

        questions_response = requests.get(f'http://127.0.0.1:5000/api/questions/public/{form_id}/questions')
        questions_response.raise_for_status()
        questions = questions_response.json().get('questions', [])

        if request.method == 'POST':
            try:
                for question in questions:
                    question.setdefault("type","text")
                    if question.get('required') and not request.form.get(f'answer_{question["id"]}'):
                        flash("Please answer all required questions.", "danger")
                        return render_template('public_form.html', form=form, questions=questions)

                answers = []
                for question in questions:
                    question_id = question['id']
                    if question['type'] == 'checkbox':
                        # Handle multiple checkbox values
                        checkbox_values = request.form.getlist(f'answer_{question_id}')
                        answer = ', '.join(checkbox_values) if checkbox_values else ''
                    else:
                        answer = request.form.get(f'answer_{question_id}', '')
                    
                    answers.append({"question_id": question_id, "answer": answer})

                response_data = {'form_id': form_id, 'answers': answers}
                submit_response = requests.post('http://127.0.0.1:5000/api/responses/submit_public_response', json=response_data)
                submit_response.raise_for_status()

                return render_template('thank_you.html', form=form)

            except requests.RequestException as e:
                flash(f"Error submitting form: {str(e)}", "danger")
                return render_template('public_form.html', form=form, questions=questions)

        return render_template('public_form.html', form=form, questions=questions)

    except requests.RequestException as e:
        return render_template('error.html', message=f"Error accessing form: {str(e)}"), 500
