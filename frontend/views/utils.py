from functools import wraps
from flask import session, redirect, url_for, flash
from flask import current_app

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('frontend.login_view'))
        return f(*args, **kwargs)
    return decorated_function

@current_app.template_filter("get_key")
def get_key(value, key, default="N/A"):
    """Retrieve a key from a dictionary, return default if not found."""
    return value.get(key, default)
