from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests

bp = Blueprint('frontend', __name__, template_folder='templates', url_prefix='/app')

@bp.route('/signup', methods=['GET', 'POST'])
def signup_view():
    """Signup view: Collects user info and creates an account."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        response = requests.post(
            'http://127.0.0.1:5000/api/users/signup',
            json={'username': username, 'email': email, 'password': password}
        )

        if response.status_code in {200, 201}:
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('frontend.login_view'))
        else:
            flash(response.json().get('error', 'Failed to create account'), 'danger')
    return render_template('signup.html')

@bp.route('/login', methods=['GET', 'POST'])
def login_view():
    """Login view: Validates user credentials and logs in."""
    if request.method == 'POST':
        data = {"email": request.form.get("email"), "password": request.form.get("password")}
        response = requests.post('http://127.0.0.1:5000/api/users/login', json=data)
        
        if response.status_code == 200:
            user_data = response.json()
            session["token"] = user_data.get("token")
            session["user_id"] = user_data.get("user_id")
            flash("Logged in successfully", "success")
            return redirect(url_for('frontend.dashboard_view'))
        else:
            flash(response.json().get('error', 'Invalid credentials'), 'danger')
    return render_template("login.html")

@bp.route('/dashboard')
def dashboard_view():
    """Dashboard view: Displays user forms if logged in."""
    token = session.get('token')
    if not token:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('frontend.login_view'))

    response = requests.get(
        'http://127.0.0.1:5000/api/forms/get_form',
        headers={'Authorization': f'Bearer {token}'}
    )
    if response.status_code == 200:
        forms = response.json().get('forms', [])
    else:
        forms = []
        flash("Failed to retrieve forms. Please try again later.", "danger")
    return render_template('dashboard.html', forms=forms)

@bp.route('/create_form', methods=['GET', 'POST'])
def create_form_view():
    """Form creation view: Allows users to create forms with questions."""
    token = session.get('token')
    if not token:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('frontend.login_view'))
    
    if request.method == 'POST':
        form_data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "user_id": session.get("user_id")
        }
        questions = [
            {
                "text": request.form.getlist("question_text")[i],
                "question_type": request.form.getlist("question_type")[i]
            } for i in range(len(request.form.getlist("question_text"))) if request.form.getlist("question_text")[i]
        ]
        if questions:
            form_data["questions"] = questions

        headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json'}
        response = requests.post(
            'http://127.0.0.1:5000/api/forms/create_form',
            json=form_data,
            headers=headers
        )

        if response.status_code == 201:
            flash("Form created successfully!", "success")
            return redirect(url_for("frontend.dashboard_view"))
        elif response.status_code == 401:
            flash("Unauthorized: Please log in again.", "danger")
        else:
            flash(response.json().get("error", "Failed to create form. Please try again."), "danger")
    return render_template("create_form.html")

@bp.route('/response/<int:form_id>', methods=['GET', 'POST'])
def response_view(form_id):
    """View for displaying questions and submitting responses to a form."""
    token = session.get('token')
    if not token:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('frontend.login_view'))

    if request.method == 'GET':
        response = requests.get(
            f'http://127.0.0.1:5000/api/questions/{form_id}/questions',
            headers={'Authorization': f'Bearer {token}'}
        )
        questions = response.json().get("questions", []) if response.status_code == 200 else []
        return render_template('response.html', questions=questions, form_id=form_id)

    elif request.method == 'POST':
        answers = [{"question_id": int(q), "answer": a} for q, a in zip(request.form.getlist('question_id'), request.form.getlist('answers'))]
        response_data = {'form_id': form_id, 'answers': answers}
        response = requests.post(
            'http://127.0.0.1:5000/api/responses/submit_response',
            headers={'Authorization': f'Bearer {token}'},
            json=response_data
        )
        if response.status_code == 201:
            flash("Response submitted successfully!", "success")
        else:
            flash("Failed to submit response.", "danger")
        return redirect(url_for('frontend.dashboard_view'))

@bp.route('/profile', methods=['GET', 'POST'])
def profile_view():
    """Profile view: Displays and updates user profile."""
    token = session.get('token')
    if not token:
        flash('Please log in to access your profile.', 'danger')
        return redirect(url_for('frontend.login_view'))

    headers = {'Authorization': f'Bearer {token}'}
    if request.method == 'POST':
        update_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        response = requests.put('http://127.0.0.1:5000/api/users/update', headers=headers, json=update_data)
        if response.status_code == 200:
            flash("Profile updated successfully!", "success")
        else:
            flash("Failed to update profile. Please try again.", "danger")

    response = requests.get('http://127.0.0.1:5000/api/users/profile', headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return render_template('profile.html', user=user_data)
    else:
        flash("Unable to load profile information.", "danger")
        return redirect(url_for('frontend.dashboard_view'))

@bp.route('/forms', methods=['GET'])
def view_all_forms():
    """View to list all forms created by the user."""
    token = session.get('token')
    if not token:
        flash('Please log in to view your forms.', 'warning')
        return redirect(url_for('frontend.login_view'))

    response = requests.get(
        'http://127.0.0.1:5000/api/forms',
        headers={'Authorization': f'Bearer {token}'}
    )

    if response.status_code == 200:
        forms = response.json().get('forms', [])
    else:
        flash("Failed to load forms. Please try again later.", "danger")
        forms = []

    return render_template('all_forms.html', forms=forms)


@bp.route('/edit_form/<int:form_id>', methods=['GET', 'POST'])
def edit_form(form_id):
    """Edit view: Allows user to edit form details and questions."""
    token = session.get('token')
    if not token:
        flash('Please log in to edit the form.', 'warning')
        return redirect(url_for('frontend.login_view'))

    if request.method == 'POST':
        # Collect updated form data
        form_data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "questions": [
                {
                    "question_id": request.form.getlist("question_id")[i],
                    "text": request.form.getlist("question_text")[i],
                    "type": request.form.getlist("question_type")[i]
                } for i in range(len(request.form.getlist("question_text")))
            ]
        }

        # Send update request to the API
        headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json'}
        response = requests.put(
            f'http://127.0.0.1:5000/api/forms/edit/{form_id}',
            json=form_data,
            headers=headers
        )

        if response.status_code == 200:
            flash("Form updated successfully!", "success")
            return redirect(url_for('frontend.view_all_forms'))
        else:
            flash(response.json().get("error", "Failed to update form."), "danger")

    # GET form data for editing view
    response = requests.get(
        f'http://127.0.0.1:5000/api/forms/get_form/{form_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    if response.status_code == 200:
        form = response.json().get("form", {})
    else:
        flash("Failed to load form details. Please try again.", "danger")
        return redirect(url_for('frontend.view_all_forms'))

    return render_template('edit_form.html', form=form)


@bp.route('/delete_form/<int:form_id>', methods=['POST'])
def delete_form(form_id):
    """Delete a specific form."""
    token = session.get('token')
    if not token:
        flash('Please log in to delete forms.', 'warning')
        return redirect(url_for('frontend.login_view'))

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(
        f'http://127.0.0.1:5000/api/forms/delete/{form_id}',
        headers=headers
    )

    if response.status_code == 200:
        flash("Form deleted successfully.", "success")
    else:
        flash("Failed to delete form. Please try again.", "danger")
    return redirect(url_for('frontend.view_all_forms'))


@bp.route('/view_responses/<int:form_id>', methods=['GET'])
def view_all_responses(form_id):
    """View all responses for a specific form."""
    token = session.get('token')
    if not token:
        flash('Please log in to view form responses.', 'warning')
        return redirect(url_for('frontend.login_view'))

    response = requests.get(
        f'http://127.0.0.1:5000/api/responses/{form_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    if response.status_code == 200:
        responses = response.json().get('responses', [])
    else:
        flash("Failed to load responses. Please try again later.", "danger")
        responses = []

    return render_template('all_responses.html', responses=responses, form_id=form_id)


@bp.route('/delete_response/<int:response_id>', methods=['POST'])
def delete_response(response_id):
    """Delete a specific response."""
    token = session.get('token')
    if not token:
        flash('Please log in to delete responses.', 'warning')
        return redirect(url_for('frontend.login_view'))

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(
        f'http://127.0.0.1:5000/api/responses/delete/{response_id}',
        headers=headers
    )

    if response.status_code == 200:
        flash("Response deleted successfully.", "success")
    else:
        flash("Failed to delete response. Please try again.", "danger")

    # Redirect back to the responses list or dashboard
    return redirect(url_for('frontend.dashboard_view'))

