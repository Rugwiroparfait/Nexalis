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
    data = {"email": request.form.get("email"), "password": request.form.get("password")}
    response = requests.post('http://127.0.0.1:5000/api/users/login', json=data)
    if response.status_code == 200:
        #parsing response to get the user_id and token
        user_data = response.json()
        session["token"] = user_data.get("token")
        session["user_id"] = user_data.get("user_id")
        flash("Logged in successfully", "success")
        return redirect(url_for('frontend.dashboard_view'))
    else:
        flash("Invalid credentials", "danger")
    return render_template("login.html")

    # if request.method == 'POST':
        #email = request.form.get('email')
        #password = request.form.get('password')

        #response = requests.post(
         #   'http://127.0.0.1:5000/api/users/login',
          #  json={'email': email, 'password': password}
        #)

        #if response.status_code == 200:
         #   session['token'] = response.json().get('token')
          #  flash('Logged in successfully!', 'success')
           # return redirect(url_for('frontend.dashboard_view'))
        #else:
          #  flash(response.json().get('error', 'Invalid credentials'), 'danger')
    #return render_template('login.html')

@bp.route('/dashboard')
def dashboard_view():
    """Dashboard view: Displays user forms if logged in."""
    if 'token' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('frontend.login_view'))

    response = requests.get(
        'http://127.0.0.1:5000/api/forms/get_form',
        headers={'Authorization': f'Bearer {session["token"]}'}
    )
    forms = response.json() if response.status_code == 200 else []
    return render_template('dashboard.html', forms=forms)

@bp.route('/create_form', methods=['GET', 'POST'])
def create_form_view():
    """Form creation view: Allows users to create forms with questions."""
    if 'token' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('frontend.login_view'))
    form_data = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "user_id": session.get("user_id")  # Make sure user_id is stored in the session after login
    }
    print("Form data being sent:", form_data)

    headers =  {
            'Authorization': f'Bearer {session["token"]}',
            'Content-Type' : 'application/json'
            }
    print("Token used for Authorization:", session.get("token"))

    response = requests.post(
        'http://127.0.0.1:5000/api/forms/create_form',
        json=form_data,
        headers=headers
    )

    if response.status_code == 201:
        flash("Form created successfully!", "success")
        return redirect(url_for("frontend.dashboard_view"))
    else:
        flash("Failed to create form. Please try again.", "danger")
    return render_template("create_form.html")

@bp.route('/response/<int:form_id>', methods=['GET', 'POST'])
def response_view(form_id):
    """View for displaying questions and submitting responses to a form."""
    if 'token' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('frontend.login_view'))

    if request.method == 'GET':
        # Retrieve questions for the form
        response = requests.get(
            f'http://127.0.0.1:5000/api/questions/{form_id}',
            headers={'Authorization': f'Bearer {session["token"]}'}
        )
        questions = response.json().get("questions", []) if response.status_code == 200 else []
        return render_template('response.html', questions=questions, form_id=form_id)

    elif request.method == 'POST':
        # Submit answers to the form
        answers = request.form.getlist('answers')
        response = requests.post(
            'http://127.0.0.1:5000/api/responses/submit_response',
            headers={'Authorization': f'Bearer {session["token"]}'},
            json={'form_id': form_id, 'answers': answers}
        )
        if response.status_code == 201:
            flash("Response submitted successfully!", "success")
        else:
            flash("Failed to submit response.", "danger")
        return redirect(url_for('frontend.dashboard_view'))

