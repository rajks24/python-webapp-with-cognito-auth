from flask import Flask, render_template, redirect, url_for, session, request
from flask_cors import CORS
from pycognito import Cognito
import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# AWS Cognito configuration
USER_POOL_ID = os.getenv('USER_POOL_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
REGION = os.getenv('REGION')
COGNITO_DOMAIN = os.getenv('COGNITO_DOMAIN')
APP_CLIENT_SCOPE = os.getenv('APP_CLIENT_SCOPE')
REDIRECT_URI = os.getenv('REDIRECT_URI')

cognito_client = boto3.client('cognito-idp', region_name=REGION)

def is_hosted_ui_configured():
    response = cognito_client.describe_user_pool_client(
        UserPoolId=USER_POOL_ID,
        ClientId=CLIENT_ID
    )
    callback_urls = response['UserPoolClient'].get('CallbackURLs', [])
    return bool(callback_urls)

@app.route('/')
def home():
    logged_in = session.get('logged_in', False)
    username = session.get('username', '')
    user_info = session.get('user_info', {})
    return render_template('index.html', logged_in=logged_in, username=username, user_info=user_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Using ALLOW_USER_SRP_AUTH flow")
    
    username = request.form['username']
    password = request.form['password']
    print("Hosted UI is not configured. Showing app's own login page.")
    try:
        user = Cognito(USER_POOL_ID, CLIENT_ID, username=username)
        user.authenticate(password=password)
        
        # Fetch user details using boto3
        response = cognito_client.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=username
        )
        
        # Debug print to inspect response structure
        # print("User info:", response)
        
        # Convert response to a dictionary
        user_info_dict = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
        
        print("User info dict:", user_info_dict)
        
        session['logged_in'] = True
        session['username'] = username
        session['user_info'] = user_info_dict
        return redirect(url_for('home'))
    except Exception as e:
        print(f"Authentication failed: {e}")
        return 'Invalid username or password', 401

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('user_info', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)