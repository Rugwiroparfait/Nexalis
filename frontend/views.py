from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests

bp = Blueprint('frontend', __name__,template_folder='templates', url_prefix='/app')

@bp.route('/signup', methods=['GET', 'POST'])
def signup_view():
    """Handles signup: getting user's credentials,
       create account and redirect to login.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')  # Fixed the typo here
        password = request.form.get('password')

        # Make a request to the backend signup API
        response = requests.post(
            'http://127.0.0.1:5000/api/signup',  # Make sure the URL matches your API endpoint
            json={'username': username, 'email': email, 'password': password}
        )

        if response.status_code == 200 or response.status_code == 201:
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('frontend.login_view'))  # Adjusted to use the frontend prefix
        else:
            flash(response.json().get('error', 'Failed to create account'), 'danger')
    return render_template('signup.html')

@bp.route('/login', methods=['GET', 'POST'])
def login_view():
    """Handles login: post user's credentials.
       check if email and password are valid.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Make a request to the backend login API
        response = requests.post(
            'http://127.0.0.1:5000/api/login',  # Make sure the URL matches your API endpoint
            json={'email': email, 'password': password}
        )

        if response.status_code == 200:  # Fixed the typo here
            token = response.json().get('token')
            session['token'] = token
            flash('Logged in successfully!', 'success')
            return redirect(url_for('frontend.dashboard_view'))  # Adjusted to use the frontend prefix
        else:
            flash(response.json().get('error', 'Invalid credentials'), 'danger')
    return render_template('login.html')

@bp.route('/dashboard')  # Added route for the dashboard
def dashboard_view():
    if 'token' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('frontend.login_view'))  # Adjusted to use the frontend prefix

    # Fetch user's forms (this assumes an API endpoint for fetching\
    # API endpoint for fetching user's form exists)

    response = requests.get('http://127.0.0.1:5000/api/forms', headers={'Authorization': f'Bearer {session["token"]}'})
    forms = response.json() if response.status_code == 200 else []



    # Render the dashboard if authenticated
    return render_template('dashboard.html', forms=forms)

@bp.route('/create_form', methods=['GET', 'POST'])
def create_form_view():
    """Handles form creation with questions."""
    if 'token' not in session:
        flash('please log in to access this page.', 'warning')
        return redirect(url_for('frontend.login_view'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        questions = request.form.getlist('questions[]')

        # Make a request to the backend API to create the form
        response = requests.post(
                'http://127.0.0.1:5000/api/forms',
                headers={'Authorization': f'Bearer {session["token"]}'},
                json={'title': title, 'description': description, 'questions': questions}
                )
        if response.status_code == 201:
            flash('Form created successfully!', 'success')
            return redirect(url_for('frontend.dashboard_view'))

        else:
            flash(response.json().get('error',' Failed to create form'), 'danger')
        return render_template('create_form.html')

