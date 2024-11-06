from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from functools import wraps

bp = Blueprint('frontend', __name__, template_folder='templates', url_prefix='/app')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('frontend.login_view'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/signup', methods=['GET', 'POST'])
def signup_view():
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
@login_required
def dashboard_view():
    try:
        response = requests.get(
            'http://127.0.0.1:5000/api/forms/get_form',
            headers={'Authorization': f'Bearer {session["token"]}'}
        )
        forms = response.json().get('forms', []) if response.status_code == 200 else []

        user_response = requests.get(
            'http://127.0.0.1:5000/api/users/user',
            headers={'Authorization': f'Bearer {session["token"]}'}
        )
        user = user_response.json() if user_response.status_code == 200 else None

    except requests.ConnectionError:
        flash("Failed to connect to the server. Please try again later.", "danger")
        forms = []
        user = None

    return render_template('dashboard.html', forms=forms, user=user)


@bp.route('/create_form', methods=['GET', 'POST'])
@login_required
def create_form_view():
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

        headers = {'Authorization': f'Bearer {session["token"]}', 'Content-type': 'application/json'}
        response = requests.post(
            'http://127.0.0.1:5000/api/forms/create_form',
            json=form_data,
            headers=headers
        )

        if response.status_code == 201:
            flash("Form created successfully!", "success")
            return redirect(url_for("frontend.dashboard_view"))
        else:
            flash(response.json().get("error", "Failed to create form. Please try again."), "danger")
    return render_template("create_form.html")


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


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_view():
    headers = {'Authorization': f'Bearer {session["token"]}'}
    if request.method == 'POST':
        update_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        response = requests.put('http://127.0.0.1:5000/api/users/update', headers=headers, json=update_data)
        flash("Profile updated successfully!" if response.status_code == 200 else "Failed to update profile. Please try again.", "success" if response.status_code == 200 else "danger")

    response = requests.get('http://127.0.0.1:5000/api/users/profile', headers=headers)
    user_data = response.json() if response.status_code == 200 else None
    if not user_data:
        flash("Unable to load profile information.", "danger")
    return render_template('profile.html', user=user_data)


@bp.route('/forms', methods=['GET'])
@login_required
def view_all_forms():
    response = requests.get(
        'http://127.0.0.1:5000/api/forms',
        headers={'Authorization': f'Bearer {session["token"]}'}
    )
    forms = response.json().get('forms', []) if response.status_code == 200 else []
    return render_template('all_forms.html', forms=forms)


@bp.route('/edit_form/<int:form_id>', methods=['GET', 'POST'])
@login_required
def edit_form(form_id):
    if request.method == 'POST':
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

        headers = {'Authorization': f'Bearer {session["token"]}', 'Content-type': 'application/json'}
        response = requests.put(
            f'http://127.0.0.1:5000/api/forms/edit/{form_id}',
            json=form_data,
            headers=headers
        )
        flash("Form updated successfully!" if response.status_code == 200 else response.json().get("error", "Failed to update form."), "success" if response.status_code == 200 else "danger")

    response = requests.get(
        f'http://127.0.0.1:5000/api/forms/get_form/{form_id}',
        headers={'Authorization': f'Bearer {session["token"]}'}
    )
    form = response.json().get("form", {}) if response.status_code == 200 else None
    return render_template('edit_form.html', form=form)


@bp.route('/delete_form/<int:form_id>', methods=['POST'])
@login_required
def delete_form(form_id):
    headers = {'Authorization': f'Bearer {session["token"]}'}
    response = requests.delete(
        f'http://127.0.0.1:5000/api/forms/delete/{form_id}',
        headers=headers
    )
    flash("Form deleted successfully." if response.status_code == 200 else "Failed to delete form. Please try again.", "success" if response.status_code == 200 else "danger")
    return redirect(url_for('frontend.dashboard_view'))


@bp.route('/logout')
def logout_view():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("frontend.login_view"))

