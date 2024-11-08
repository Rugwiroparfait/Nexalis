from flask import render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect, generate_csrf
import requests
from .. import bp
from .utils import login_required

@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_view():
    user_id = session.get('user_id')
    token = session.get('token')

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-type': 'application/json'
    }

    user_response = requests.get('http://127.0.0.1:5000/api/user', headers=headers)
    user_data = user_response.json() if user_response.status_code == 200 else {}

    forms_response = requests.get('http://127.0.0.1:5000/api/forms/get_form', headers=headers)
    forms_data = forms_response.json().get("forms", []) if forms_response.status_code == 200 else []
    
    return render_template("dashboard.html", user=user_data, forms=forms_data)

@bp.route('/create_form', methods=['GET', 'POST'])
@login_required
def create_form_view():
    token = session.get('token')
    user_id = session.get('user_id')

    if not token or not user_id:
        flash("Please log in again.", "danger")
        return redirect(url_for('frontend.login_view'))

    if request.method == 'POST':
        form_data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "user_id": user_id,
            "questions": [
                {"text": text, "type": "text"}
                for text in request.form.getlist("questions[]")
                if text.strip()
            ]
        }

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                'http://127.0.0.1:5000/api/forms/create_form',
                json=form_data,
                headers=headers
            )

            if response.status_code == 201:
                data = response.json()
                flash(f"Form '{data['form']['title']}' created successfully!", "success")
                return redirect(url_for("frontend.dashboard_view"))
            else:
                flash(f"Failed to create form: {response.json().get('message', 'Unknown error')}", "danger")

        except requests.exceptions.RequestException as e:
            flash(f"Error communicating with the server: {str(e)}", "danger")

    return render_template("create_form.html")

@bp.route('/my_forms', methods=['GET'])
@login_required
def view_all_forms():
    token = session.get('token')

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-type': 'application/json'
    }

    form_response = requests.get(
        'http://127.0.0.1:5000/api/forms/get_form',
        headers=headers
    )

    forms = form_response.json().get("forms", []) if form_response.status_code == 200 else []
    return render_template("view_all_forms.html", forms=forms)


@bp.route('/form/<int:form_id>', methods=['GET', 'POST'])
@login_required
def view_form(form_id):
    """View a single form with questions, allowing delete and update of questions."""
    user_id = session.get('user_id')
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json'}

    # Fetch form details
    form_response = requests.get(
        f'http://127.0.0.1:5000/api/forms/get_forms/{form_id}',
        headers=headers
    )
    if form_response.status_code == 200:
        form = form_response.json().get('form', {})
    else:
        form = None
        flash("Failed to retrieve form details.", "danger")

    # Debugging output to check form data
    print("Form data:", form)  # Debugging statement

    # Fetch questions for the form
    questions_response = requests.get(
        f'http://127.0.0.1:5000/api/questions/{form_id}/questions',
        headers=headers
    )
    if questions_response.status_code == 200:
        questions = questions_response.json().get('questions', [])
    else:
        questions = []
        flash("Failed to retrieve questions for this form.", "danger")

    csrf_token = generate_csrf()

    return render_template("view_form.html", form=form, questions=questions, csrf_token=csrf_token)


@bp.route('/share/<string:link_token>', methods=['GET'])
def share_link_view(link_token):
    """Public view where a responder can view and respond to a form without logging in."""

    # Fetch the form details using the link_token
    try:
        response = requests.get(
            f'http://127.0.0.1:5000/api/forms/link/{link_token}',
            headers={'Content-type': 'application/json'}
        )
        if response.status_code == 200:
            form_data = response.json().get("form", {})
        else:
            form_data = None
            flash("Form not found or link is invalid.", "danger")
            return render_template("error.html", message="Form not found or link is invalid.")

    except requests.RequestException as e:
        flash("Error fetching form data. Please try again later.", "danger")
        form_data = None

    # Render the responder view if the form data is available
    return render_template("responder_form.html", form=form_data)


@bp.route('/update_question/<int:id>', methods=['GET', 'POST'])
@login_required
def update_question(id):
    """Update a question with the given ID."""
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json'}

    if request.method == 'POST':
        question_text = request.form.get('question_text')
        question_type = request.form.get('question_type')
        options = request.form.getlist('options')

        data = {
            'text': question_text,
            'question_type': question_type,
            'options': options
        }

        response = requests.put(
            f'http://127.0.0.1:5000/api/forms/update_question/{id}',
            json=data,
            headers=headers
        )

        if response.status_code == 200:
            flash("Question updated successfully.", "success")
        else:
            flash("Failed to update question.", "danger")

        # Redirect to the form view page after update
        form_id = request.args.get('form_id')
        return redirect(url_for('frontend.view_form', form_id=form_id))

    # GET request: Fetch question details for pre-filling in the update form
    question_response = requests.get(
        f'http://127.0.0.1:5000/api/forms/get_question/{id}',
        headers=headers
    )

    if question_response.status_code == 200:
        question = question_response.json().get('question', {})
    else:
        question = {}
        flash("Failed to retrieve question details.", "danger")

    return render_template("update_question.html", question=question)


@bp.route('/delete_question/<int:id>/<int:form_id>', methods=['DELETE'])
@login_required
def delete_question(id, form_id):
    """
    Delete a question with the given ID by calling the API.
    Redirects back to the form view page with a success or failure message.
    """
    token = session.get('token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-type': 'application/json'
    }

    response = requests.delete(f'http://127.0.0.1:5000/api/forms/delete_form/{id}', headers=headers)
    
    if response.status_code == 200:
        flash('Form deleted successfully!', 'success')
    else:
        flash('Failed to delete the form.', 'danger')
    
    return redirect(url_for('frontend.dashboard_view'))
