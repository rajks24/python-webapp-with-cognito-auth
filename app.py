from flask import Flask, render_template, redirect, url_for, session, request
from flask_cors import CORS
from pycognito import Cognito
import boto3
import requests
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
REDIRECT_URI = os.getenv('REDIRECT_URI')
COGNITO_DOMAIN = os.getenv('COGNITO_DOMAIN')
APP_CLIENT_SCOPE = os.getenv('APP_CLIENT_SCOPE')

def is_hosted_ui_configured():
    client = boto3.client('cognito-idp', region_name=REGION)
    response = client.describe_user_pool_client(
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
    if is_hosted_ui_configured():
        login_url = f"https://{COGNITO_DOMAIN}/login?client_id={CLIENT_ID}&response_type=code&scope={APP_CLIENT_SCOPE}&redirect_uri={REDIRECT_URI}"
        print("Hosted UI is configured. Redirecting to Hosted UI.")
        return redirect(login_url)
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            try:
                user = Cognito(USER_POOL_ID, CLIENT_ID, username=username)
                user.authenticate(password=password)
                
                # Fetch user details using boto3
                client = boto3.client('cognito-idp', region_name=REGION)
                response = client.admin_get_user(
                    UserPoolId=USER_POOL_ID,
                    Username=username
                )
                
                # Debug print to inspect response structure
                # print("User info:", response)
                
                # Convert response to a dictionary
                user_info_dict = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
                
                # print("User info dict:", user_info_dict)
                
                session['logged_in'] = True
                session['username'] = username
                session['user_info'] = user_info_dict
                return redirect(url_for('home'))
            except Exception as e:
                print(f"Authentication failed: {e}")
                return 'Invalid username or password', 401
        print("Hosted UI is not configured. Showing app's own login page.")
        return render_template('login.html')

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
    session.pop('user_info', None)
    print("User logged out. Redirecting to home page.")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
