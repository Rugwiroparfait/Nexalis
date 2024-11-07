from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from functools import wraps
from flask_wtf.csrf import CSRFProtect, generate_csrf

bp = Blueprint('frontend', __name__, template_folder='templates', url_prefix='/app')
csrf = CSRFProtect()

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
@csrf.exempt
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
                # Store both token and user_id in session
                session["token"] = response_data.get("token")
                session["user_id"] = response_data.get("user_id")
                
                # Debug prints
                print("Login successful")
                print(f"Token: {session.get('token')}")
                print(f"User ID: {session.get('user_id')}")
                
                flash("Logged in successfully", "success")
                return redirect(url_for('frontend.dashboard_view'))
            else:
                error_msg = response.json().get('error', 'Invalid credentials')
                print(f"Login failed: {error_msg}")
                flash(error_msg, 'danger')
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            flash("Connection error. Please try again.", "danger")
            
    return render_template("login.html")


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_view():
    """Dashboard view for a user to see their forms."""
    user_id = session.get('user_id')  # Assuming user_id is available from current_user
    token = session.get('token')  # Ensure JWT token is in session

    # Fetch forms from API
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-type': 'application/json'
    }

    user_response = requests.get('http://127.0.0.1:5000/api/user', headers=headers)
    user_data = user_response.json() if user_response.status_code == 200 else {}

    forms_response = requests.get('http://127.0.0.1:5000/api/forms/get_form', headers=headers)
    forms_data = forms_response.json().get("forms", []) if forms_response.status_code == 200 else []
    
    return render_template("dashboard.html",user=user_data, forms=forms_data)



@bp.route('/create_form', methods=['GET', 'POST'])
@login_required
def create_form_view():
    """Form creation view: Allows users to create forms with questions."""
    token = session.get('token')
    user_id = session.get('user_id')
    # Debug prints
    print(f"Session token: {token}")
    print(f"Session user_id: {user_id}")
    
    if not token or not user_id:
        flash("Please log in again.", "danger")
        return redirect(url_for('frontend.login_view'))
    
    if request.method == 'POST':
        form_data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "user_id": user_id,  # Now this should be properly set
            "questions": [
                {"text": text, "type": "text"}
                for text in request.form.getlist("questions[]")
                if text.strip()
            ]
        }
        
        # Debug print
        print("Form data being sent:", form_data)
        
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
            
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 201:
                data = response.json()
                flash(f"Form '{data['form']['title']}' created successfully!", "success")
                return redirect(url_for("frontend.dashboard_view"))
            else:
                flash(f"Failed to create form: {response.json().get('message', 'Unknown error')}", "danger")
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            flash(f"Error communicating with the server: {str(e)}", "danger")
    
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

@bp.route('/edit_form/<int:form_id>', methods=['GET', 'POST'])
@login_required
def edit_form(form_id):
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json'}

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

        response = requests.put(
            f'http://127.0.0.1:5000/api/forms/update_forms/{form_id}',
            json=form_data,
            headers=headers
        )

        if response.status_code == 200:
            flash("Form updated successfully!", "success")
        else:
            flash("Failed to update form.", "danger")

    form_response = requests.get(
        f'http://127.0.0.1:5000/api/forms/get_forms/{form_id}',
        headers=headers
    )
    form = form_response.json().get("form", {}) if form_response.status_code == 200 else None
    return render_template('edit_form.html', form=form)


@bp.route('/delete_form/<int:form_id>', methods=['POST'])
@login_required
def delete_form(form_id):
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.delete(
        f'http://127.0.0.1:5000/api/forms/forms/{form_id}',
        headers=headers
    )

    if response.status_code == 200:
        flash("Form deleted successfully.", "success")
    else:
        flash("Failed to delete form. Please try again.", "danger")

    return redirect(url_for('frontend.dashboard_view'))



@bp.route('/logout')
def logout_view():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("frontend.login_view"))


@bp.route('/my_forms', methods=['GET'])
@login_required
def view_all_forms():
    """View all forms created by the logged-in user."""
    token = session.get('token')

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-type': 'application/json'
    }

    form_response = requests.get(
        'http://127.0.0.1:5000/api/forms/get_form',  # Correct API endpoint to fetch all forms
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


@bp.route('/form/respond/<string:link_token>', methods=['GET', 'POST'])
def responder_view(link_token):
    """Display questions for a responder and handle response submission."""
    
    # Fetch form details and questions based on link_token
    try:
        form_response = requests.get(f'http://127.0.0.1:5000/api/forms/link/{link_token}')
        if form_response.status_code == 200:
            form_data = form_response.json().get("form", {})
        else:
            flash("Form not found or link is invalid.", "danger")
            return render_template("error.html", message="Form not found or link is invalid.")
    
    except requests.RequestException:
        flash("Error fetching form data. Please try again later.", "danger")
        return render_template("error.html", message="Error fetching form data.")
    
    # Handle the response submission (POST request)
    if request.method == 'POST':
        answers = [
            {"question_id": int(q_id), "answer": ans}
            for q_id, ans in zip(request.form.getlist('question_id'), request.form.getlist('answer'))
        ]
        
        # Prepare the data for submission
        response_data = {'form_id': form_data.get('id'), 'answers': answers}
        
        try:
            submit_response = requests.post(
                'http://127.0.0.1:5000/api/forms/submit_response',
                json=response_data,
                headers={'Content-type': 'application/json'}
            )
            
            if submit_response.status_code == 201:
                flash("Thank you! Your response has been recorded.", "success")
                return redirect(url_for('frontend.share_link_view', link_token=link_token))
            else:
                flash("Failed to submit response. Please try again.", "danger")
        
        except requests.RequestException:
            flash("Error submitting response. Please try again later.", "danger")
    
    # Render the responder form view if the method is GET
    return render_template("responder_form.html", form=form_data)

@bp.route('/form/<int:form_id>/responses', methods=['GET'])
@login_required
def view_responses(form_id):
    """View all responses for a specific form created by the logged-in user."""
    
    user_id = session.get('user_id')  # Ensure we have the logged-in user's ID
    token = session.get('token')      # Ensure we have the JWT token for API access

    headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json'}
    
    # Fetch responses for the form
    try:
        response = requests.get(
            f'http://127.0.0.1:5000/api/forms/get_response/{form_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            responses = response.json().get("responses", [])
        else:
            flash("Failed to retrieve responses. Please try again later.", "danger")
            responses = []
    
    except requests.RequestException:
        flash("Error retrieving responses. Please try again later.", "danger")
        responses = []
    
    # Render the responses in a template (view_responses.html)
    return render_template("view_responses.html", form_id=form_id, responses=responses)

@bp.route('/delete_question/<int:id>/<int:form_id>', methods=['DELETE'])
@login_required
def delete_question(id, form_id):
    """
    Delete a question with the given ID by calling the API.
    Redirects back to the form view page with a success or failure message.
    """
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    try:
        # Send DELETE request to the API
        response = requests.delete(
            f'http://127.0.0.1:5000/api/questions/delete_question/{id}',
            headers=headers
        )
        
        # Check response status
        if response.status_code == 200:
            flash("Question deleted successfully.", "success")
        else:
            # Extract error message from the API response if available
            error_message = response.json().get("error", "Failed to delete question.")
            flash(f"Error: {error_message}", "danger")
        
        # Log response content for debugging
        print(f"API Response: {response.status_code} - {response.json()}")

    except requests.exceptions.RequestException as e:
        # Handle request exceptions and display message
        flash("An error occurred while connecting to the server.", "danger")
        print(f"RequestException: {e}")
    
    print(f"Question ID: {id}, Form ID: {form_id}")
    
    # Redirect back to the form view page
    return redirect(url_for('frontend.view_form', form_id=form_id))




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
