# Nexalis

Nexalis is a Flask-based web application for creating and managing online forms, inspired by popular form-building platforms.

## Project Structure

```
nexalis/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── run.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── form.py
│   │   │   ├── question.py
│   │   │   ├── response.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── form_schema.py
│   │   │   ├── question_schema.py
│   │   │   ├── response_schema.py
│   │   │   └── user_schema.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── forms.py
│   │   │   ├── questions.py
│   │   │   ├── responses.py
│   │   │   └── auth.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── login.py
│   │   │   ├── signup.py
│   │   │   └── token.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   ├── migrations/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_forms.py
│   │   ├── test_questions.py
│   │   ├── test_responses.py
│   │   └── test_auth.py
│   └── requirements.txt
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── create_form.html
│   │   ├── view_form.html
│   │   ├── login.html
│   │   └── signup.html
│   └── views.py
│       ├── login_view()
│       ├── signup_view()
│       └── form_views()
│
├── Dockerfile
├── docker-compose.yml
└── README.md

```

## Setup and Installation

### Using Docker

1. Clone the repository:
   ```
   git clone https://github.com/Rugwiroparfait/nexalis.git
   cd nexalis
   ```

2. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

3. Access the application at `http://localhost:5000`

### Manual Setup

1. Clone the repository:
   ```
   git clone https://github.com/Rugwiroparfait/nexalis.git
   cd nexalis
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the application:
   ```
   python run.py
   ```

## Features

- Create custom forms with various question types
- Share forms with unique URLs
- Collect and store form responses
- View and analyze response data
- User authentication and form management

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
# Nexalis
