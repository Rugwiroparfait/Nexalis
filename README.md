

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

### API Endpoints

All backend APIs are prefixed with `/api/` and are organized by feature. Here are some key routes:

1. **User Management**:
   - `POST /api/users/signup`: Register a new user.
   - `POST /api/users/login`: Authenticate and receive a JWT token.

2. **Form Management**:
   - `GET /api/forms/get_form`: Retrieve forms for the authenticated user.
   - `POST /api/forms`: Create a new form.

3. **Responses**:
   - `POST /api/forms/<form_id>/responses`: Submit a response to a form.
   - `GET /api/forms/<form_id>/responses`: Retrieve all responses to a form.

> **Note**: All protected endpoints require a valid JWT token in the headers.

### Configuration

Configuration settings for the app are located in `backend/config.py`. This includes settings for:
- Database (SQLite or PostgreSQL, etc.)
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

- **Your Name** ([@Rugwiroparfait](https://github.com/Rugwiroparfait)) - Developer and Project Lead

Feel free to reach out with questions, suggestions, or contributions!

---

## 📌 Additional Notes

- **Environment Variables**: Use `.env` files for sensitive configurations when deploying.
- **Modularity**: The project structure allows adding more features as needed with minimal disruption to the existing codebase.

Feel free to view more about this project! 🎉
