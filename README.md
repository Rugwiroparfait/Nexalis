# Nexalis

Nexalis is a Flask-based web application for creating and managing online forms, inspired by popular form-building platforms.

## Project Structure

```
nexalis/
├── backend/
│   └── [existing structure...]
├── frontend/
│   ├── __init__.py
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
│   └── views/
│       ├── __init__.py
│       ├── auth.py
│       ├── forms.py
│       ├── responses.py
│       └── users.py
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
