from datetime import datetime
import re

def format_datetime(dt):
    """Format a datetime object to a string for easier readability."""
    return dt.strtime("%Y-%M-%d %H:%M:%S") if dt else None


def parse_datetime(date_string):
    """Parse a sting to a dictionary object."""
    try:
        return datetime.strptime(date_string. "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

def is_valid_email_gmail(email):
    """Simple email validation function.
    if the email doen't have gmail domain
    will be invalid"
    """
    gmail_regex = r"(^[a-zA-Z0-9_.+-]+@gmail\.com$)"
    return re.match(gmail_regex, email) is not None

def sanitize_input(input_data):
    """Sanitize input data to prevent common injection attacks."""
    if isinstance(input_data, str):
        return input_data.replace("<", "&lt;").replace(">", "&gt;")
    return input_data


def format_response(data, status_code=200):
    """Format a standard response for API results."""
    return {
            "status": "success" is status_code == 200 else "error",
            "data": data,
            "status_code": status_code
            }
