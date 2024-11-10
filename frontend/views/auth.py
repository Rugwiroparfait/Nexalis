from flask import render_template, request, redirect, url_for, flash, session
import requests
from .. import bp
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
        data = {
            "email": request.form.get("email"),
            "password": request.form.get("password")
        }
        
        try:
            response = requests.post('http://127.0.0.1:5000/api/users/login', json=data)
            
            if response.status_code == 200:
                response_data = response.json()
                session["token"] = response_data.get("token")
                session["user_id"] = response_data.get("user_id")
                
                flash("Logged in successfully", "success")
                return redirect(url_for('frontend.dashboard_view'))
            else:
                error_msg = response.json().get('error', 'Invalid credentials')
                flash(error_msg, 'danger')
                
        except requests.exceptions.RequestException as e:
            flash("Connection error. Please try again.", "danger")
            
    return render_template("login.html")

@bp.route('/logout')
def logout_view():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("frontend.login_view"))
