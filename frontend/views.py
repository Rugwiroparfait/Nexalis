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
    if response.status_code == 200:
        forms = response.json().get('forms', [])
    else:
        forms = []
        flash("Failed to retrieve forms. Please try again later.", "danger")
    return render_template('dashboard.html', forms=forms)

@bp.route('/create_form', methods=['GET', 'POST'])
def create_form_view():
    """Form creation view: Allows users to create forms with questions."""
    if 'token' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('frontend.login_view'))
    
    if request.method == 'POST':
        # Prepare form data
        form_data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "user_id": session.get("user_id")
        }
        print("Form data being sent:", form_data)

        # Collect questions
        questions = []
        for i in range(len(request.form.getlist("question_text"))):
            question_text = request.form.getlist("question_text")[i]
            question_type = request.form.getlist("question_type")[i]
            if question_text and question_type:
                questions.append({
                    "text": question_text,
                    "question_question": question_type
                    })

        # Ading questions to form_data only if they exist
        if questions:
            form_data["questions"]= questions
        # debugging in case LOL (--)
        print("Questions data being sent:", questions)

        # API request will be like ...
        headers = {
                'Authorization': f'Bearer {session["token"]}',
                'Content-type': 'application/json'
            }
        # printing token (debugging purpose)
        print("Token used for Authorization:", session.get("token"))

        # post a  request to the API
        response = requests.post(
                'http://127.0.0.1:5000/api/forms/create_form',
                json=form_data,
                headers=headers
            )
        # Handle the API response
        if response.status_code == 201:
            flash("form created successfully!", "success")
            return redirect(url_for("frontend.dashboard_view"))
        elif response.status_code == 401:
            flash("Unauthorized: Please log in again.", "danger")
        elif response.status_code == 400:
            error_message = response.json().get("error","Failed to create form. Missing or invalid data." )
            flash(f"Error: {error_message}", "danger")
        elif response.status_code == 422:
            flash("The server Unable to process the request because it contains invalid data")
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

@bp.route('/views_form/<int:form_id>', methods=['GET'])
def view_form(form_id):
    """View form: Displays a specific form with its questions."""
    if 'token' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('frontend.login_view'))

    # Request to get form details
    form_response = requests.get(
        f'http://127.0.0.1:5000/api/forms/get_form/{form_id}',
        headers={'Authorization': f'Bearer {session["token"]}'}
    )
    
    if form_response.status_code == 200:
        form_data = form_response.json().get('form', {})
    else:
        flash("Failed to load form. Please try again later", "danger")
        return redirect(url_for('frontend.dashboard_view'))

    # Request to get associated questions for the form
    questions_response = requests.get(
        f'http://127.0.0.1:5000/api/questions/{form_id}/questions',
        headers={'Authorization': f'Bearer {session["token"]}'}
    )

    if questions_response.status_code == 200:
        questions_data = questions_response.json().get('questions', [])
    else:
        flash("Failed to load questions. Please try again later", "danger")
        return redirect(url_for('frontend.dashboard_view'))

    # Render the form with its associated questions
    return render_template('view_form.html', form=form_data, questions=questions_data)



@bp.route('/submit_response/<int:form_id>', methods=['POST'])
def submit_response(form_id):
    """Submit responses to a form."""
    if 'token' not in session:
        flash('Please log in to submit your response.', 'warning')
        return redirect(url_for('frontend.login_view'))
    
    responses = request.form.getlist('responses')
    response_data = {
            'form_id': form_id,
            'responses': responses
            }
    response = requests.post(
            f'http://127.0.0.1:5000/api/responses',
            json=response_data,
            headers={'Authorization': f'Bearer {session["token"]}'}
            )

    if response.status_code == 201:
        flash('Your response has been submitted successfully.', 'success')
    else:
        flash('Failed to submit response. Please try again later.', 'danger')
    return redirect(url_for('frontend.dashboard_view'))
