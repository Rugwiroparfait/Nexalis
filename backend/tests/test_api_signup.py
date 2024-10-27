import requests

def test_signup_endpoint():
    url = "http://127.0.0.1:5000/signup"
    payload = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "testpassword"
            }
    response = requests.post(url, json=payload)

    assert response.status_code == 201
    assert response.json().get("message") == "User created successfully"

if __name__ == "__main__":
    test_signup_endpoint()
