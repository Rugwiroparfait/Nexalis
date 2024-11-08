from flask import render_template, request, redirect, url_for, flash, session
import requests
from .. import bp
from .utils import login_required

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
