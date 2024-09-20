from flask import Flask, render_template, redirect, url_for, session, request
from flask_cors import CORS
import boto3
import requests
import json
import jwt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# AWS Cognito configuration
USER_POOL_ID = os.getenv('USER_POOL_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
REGION = os.getenv('REGION')
REDIRECT_URI = os.getenv('REDIRECT_URI')
COGNITO_DOMAIN = os.getenv('COGNITO_DOMAIN')
APP_CLIENT_SCOPE = os.getenv('APP_CLIENT_SCOPE')

@app.route('/')
def home():
    logged_in = session.get('logged_in', False)
    username = session.get('username', '')
    user_info = session.get('user_info', {})
    return render_template('index.html', logged_in=logged_in, username=username, user_info=user_info)


@app.route('/login')
def login():
    login_url = f"https://{COGNITO_DOMAIN}/login?client_id={CLIENT_ID}&response_type=code&scope=openid+profile&redirect_uri={REDIRECT_URI}"
    return redirect(login_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = f"https://{COGNITO_DOMAIN}/oauth2/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    tokens = token_response.json()
    
    if 'id_token' not in tokens:
        print('Error: ID token not found')
        print(tokens)
        return 'Error: ID token not found', 400

    id_token = tokens['id_token']
    access_token = tokens['access_token']

    # Fetch user details from /oauth2/userInfo endpoint
    user_info_url = f"https://{COGNITO_DOMAIN}/oauth2/userInfo"
    user_info_headers = {'Authorization': f'Bearer {access_token}'}
    user_info_response = requests.get(user_info_url, headers=user_info_headers)
    user_info = user_info_response.json()

    # Print the user_info dictionary to check its contents
    print(user_info)

    session['logged_in'] = True
    session['username'] = user_info.get('username', 'Unknown')
    session['user_info'] = user_info
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    logout_url = f"https://{COGNITO_DOMAIN}/logout?client_id={CLIENT_ID}&logout_uri=http://localhost:5000/"
    return redirect(logout_url)

if __name__ == '__main__':
    app.run(debug=True)
