import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# GitHub info from the .env file
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
REPO_NAME = os.getenv('REPO_NAME')
FILE_PATH = os.getenv('FILE_PATH')

# GitHub API base URL
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{FILE_PATH}"

# Headers for GitHub API requests
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Helper function to get the file content from GitHub
def get_github_file():
    response = requests.get(GITHUB_API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()['content']
    return None

# Helper function to create/update the file on GitHub
def update_github_file(content):
    # Get the current file content
    existing_file = get_github_file()
    
    if existing_file:
        # Decode the content from base64
        existing_file_content = json.loads(existing_file)
        current_sha = existing_file_content['sha']
    else:
        current_sha = None

    # Prepare the file update payload
    payload = {
        'message': 'Update credentials file',
        'content': content,
        'sha': current_sha
    }

    response = requests.put(GITHUB_API_URL, headers=headers, json=payload)
    return response.status_code == 201  # Return True if update was successful

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Prepare the new registration data
    new_registration = {
        "username": username,
        "email": email,
        "password": password
    }

    # Get existing registration data from GitHub
    existing_data = get_github_file()
    
    if existing_data:
        # Decode the file content from base64 and load as JSON
        existing_data = json.loads(existing_data)
    else:
        existing_data = []

    # Add the new registration to the data
    existing_data.append(new_registration)

    # Update the file on GitHub
    if update_github_file(json.dumps(existing_data)):
        return jsonify({'message': 'Registration successful!'}), 200
    return jsonify({'error': 'Failed to save registration data'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Get existing registration data from GitHub
    existing_data = get_github_file()
    
    if existing_data:
        # Decode the file content from base64 and load as JSON
        existing_data = json.loads(existing_data)
    else:
        return jsonify({'error': 'No users registered yet'}), 400

    # Check if the username and password match any entry
    for user in existing_data:
        if user['username'] == username and user['password'] == password:
            return jsonify({'message': 'Login successful!'}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True)
