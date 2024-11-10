

---

# Nexalis 🌐

**Nexalis** enables users to create forms with customizable questions, collect responses, and view aggregated data on a personal dashboard. The project is structured to ensure modularity, with the backend exposing RESTful APIs, while the frontend uses Jinja templating to dynamically render views and AJAX requests for real-time actions (like deleting a form) without needing a full page refresh. This hybrid approach enhances user experience by combining Flask's server-side rendering with efficient asynchronous interactions.

> **Project Context**: ALX academic project for portfolio demonstration.

---

## 📑 Table of Contents
- [Project Description](#-project-description)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Collaborators](#-collaborators)

---

## 📝 Project Description

**Nexalis** enables users to create forms with customizable questions, collect responses, and view aggregated data on a personal dashboard. It's structured to ensure modularity, with the backend exposing RESTful APIs, while the frontend manages the interface, communicating with the backend through AJAX requests.

---

## ✨ Features

- **User Authentication**: Secure login and signup using JWT (JSON Web Tokens).
- **Form Management**: Create, update, and delete forms.
- **Question & Response Handling**: Add questions to forms, collect responses, and display them.
- **Dashboard**: A personalized dashboard to manage forms and view responses.
- **Modular Design**: Clear separation between frontend and backend for easy maintainability.
- **Response Export**: Download responses  in **CSV** format for further analyis

---

## 🏗️ Project Structure

The project follows a clean, modular structure. Below is a quick overview:

```plaintext
Nexalis/
├── backend/                  # Backend (API) and main application folder
│   ├── app/                  # Main Flask application
│   │   ├── api/              # Backend APIs (organized by blueprints)
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Data schemas for validation
│   │   ├── utils/            # Utility functions (e.g., authentication)
│   │   └── __init__.py       # Application and blueprint initialization
│   ├── config.py             # Configuration settings
│   ├── instance/             # Instance folder with SQLite database
│   ├── migrations/           # Database migrations
│   ├── requirements.txt      # Backend dependencies
│   ├── run.py                # Application entry point
│   └── tests/                # API tests
├── frontend/                 # Frontend codebase
│   ├── static/               # Static files (CSS, JS)
│   ├── templates/            # HTML templates for rendering UI
│   ├── views/                # Frontend views and blueprints
│   └── __init__.py           # Blueprint initialization for frontend
└── README.md                 # Project documentation
```

### Breakdown of Key Components

- **`backend/run.py`**: Entry point of the app, running the entire application (both backend and frontend) on `http://127.0.0.1:5000`.
- **`backend/app/__init__.py`**: Initializes Flask app, registers backend API blueprints, and integrates the frontend blueprint to render templates and serve static files.
- **`frontend/views/`**: Contains routes for rendering user interfaces such as the dashboard, form creation, and response views.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Flask**

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Rugwiroparfait/nexalis.git
   cd nexalis
   ```

2. **Set up the virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Run database migrations**:
   ```bash
   cd backend
   flask db upgrade
   ```

### Running the Application

To start the entire application, run:

```bash
python backend/run.py
```

The app will be available at `http://127.0.0.1:5000`.

---

## 🛠 Usage

### Key Routes

- **Homepage**: `http://127.0.0.1:5000/`
- **Dashboard**: Accessible after login; displays forms created by the user.
- **Form Management**: Create, view, edit, and delete forms via the dashboard.
- **Public Forms**: Shareable forms for collecting responses without requiring a login.

### Example Route - Dashboard (`frontend/views/forms.py`)

```python
@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_view():
    user_id = session.get('user_id')
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}'}
    user_response = requests.get('http://127.0.0.1:5000/api/users/me', headers=headers)
    forms_response = requests.get('http://127.0.0.1:5000/api/forms/get_form', headers=headers)
    return render_template("dashboard.html", user=user_response.json(), forms=forms_response.json().get("forms", []))
```
### Asynchronous Example - Delete Form (AJAX)

The **AJAX** requests enhance the app's responsiveness, allowing certain actions, like deleting a form, to occur asynchronously without refreshing the page. Example AJAX code:

```javascript
// JavaScript to delete a form using AJAX
function deleteForm(formId) {
    fetch(`/api/forms/${formId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
    }).then(response => {
        if (response.ok) {
            document.getElementById(`form-${formId}`).remove(); // Remove form from DOM
        }
    });
}
```

### API Endpoints

All backend APIs are prefixed with `/api/` and are organized by feature. Here are some key routes:

1. **User Management**:
   - `POST /api/users/signup`: Register a new user.
   - `POST /api/users/login`: Authenticate and receive a JWT token.
   - `GET /users/get_user`: retrieve the user name, email and password.
   - `PUT /users/update_user`: Update the user name, emai and passord.

2. **Form Management**:
   - `GET /api/forms/get_form`: Retrieve all forms for the authenticated user.
   - `POST /api/forms/create_form`: Create a new form.
   - `GET /api/questions/<form_id>/questions`: Retrieve all form's info.
   - `PUT /api/forms/update_forms/<form_id>`: Update the form's title and description.
   - `DELETE /api/forms/delete_form/<form_id>`: delete a form with given form_id.
   - `GET /api/forms/public/<int:form_id>`: retrieve form questionnaire data for end user without JWT token.
   - `GET /api/forms/get_forms/<int:id>` : retrieve specific form for authenticated user.
3. **Questions**:
    - `GET /api/questions/create_question` : create a new question
    - `DELETE /api/questions/delete_questions<int:id>` : delete question with a given id.

    - `GET /questions/<int:id>/questions`: get all form questions with their responses.

    - `GET /questions/public/<int:id> questions`: get questions without authentication (used in responding)
    
    
4. **Responses**:
   - `POST /api/responses/submit_response`: Submit a response to a form given a Bearer Key in header to identify the user.
   - `GET /api/responses/get_response/<int:id> `: get response with id.
   - `POST /api/responses/submit_public_response`: submit the responses in authenticated form.
   - `GET /api/responses/get_responses/<int:id`: get responses of a given form_id

> **Note**: All protected endpoints require a valid JWT token in the headers.

### Configuration

Configuration settings for the app are located in `backend/config.py`. This includes settings for:
- Database (SQLite)
- JWT secret key for authentication
- Debug mode

To run the application in production, update `config.py` accordingly.

---

## 🧪 Testing

Unit tests are located in `backend/tests/`. To run tests:

1. Ensure that dependencies are installed.
2. Run the following command from the `backend` folder:
   ```bash
   pytest tests/
   ```

---

## 🤝 Collaborators

- **NSANZIMANA RUGWIRO Dominique Parfait** ([@Rugwiroparfait](https://github.com/Rugwiroparfait)) - Developer and Project Lead
- **X (ex-Twitter)**
[x](https://x.com/RugwiroParfait])
Feel free to reach out with questions, suggestions, or contributions!

---

## 📌 Additional Notes

- **Environment Variables**: Use `.env` files for sensitive configurations when deploying.
- **Modularity**: The project structure allows adding more features as needed with minimal disruption to the existing codebase.

Feel free to view more about this project! 🎉
