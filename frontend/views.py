from flask import render_template, request, redirect, url_for, flash, session
import requests

def signup_view():
    """Handles signup: geting user's credentials,
       create account and redirect to login.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form,get('email')
        password = request.form.get('password')


        #Make a request to the backend signup API
        response = requests.post(
                'http://127.0.0.1:5000/signup',
                json={'username':username, 'email':email, 'password':password}
                )

        if response.status_code == 201:
            flash('Account created successfully! please log in.', 'success')
            return redirect(url_for('login_view'))
        else:
            flash(response.json().get('error', 'Failed to create account'), 'danger')
    return render_template('signup.html')


def login_view():
    """Handles login: post user's credentials.
       check if email and password are valid
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Make a request to the backend login API
        response = request.post(
                'http://127.0.0.1:5000/login',
                json={'email': email, 'password': password}
                )

        if response.status_code = 200:
            token = response.json().get('token')
            session['token'] = token
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard_view'))
        else:
            flash(response.json().get('error', 'Invalid credentials'), 'danger')
    return render_template('login.html')

def dashboard_view():
    if 'token' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login_view'))

    # Render the dashboard if authenticated
    return render_template('dashboard.html')
