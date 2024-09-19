from flask import Flask, render_template, redirect, url_for, session, request
from flask_cors import CORS
from pycognito import Cognito
import boto3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# AWS Cognito configuration
USER_POOL_ID = 'ap-southeast-2_TQHGbRRgb'
CLIENT_ID = '1ohpj05vj7mo8g0bpu09sne3ci'
REGION = 'ap-southeast-2'

cognito_client = boto3.client('cognito-idp', region_name=REGION)

@app.route('/')
def home():
    logged_in = session.get('logged_in', False)
    username = session.get('username', '')
    return render_template('index.html', logged_in=logged_in, username=username)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    try:
        user = Cognito(USER_POOL_ID, CLIENT_ID, username=username)
        user.authenticate(password=password)
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('home'))
    except Exception as e:
        return str(e), 401

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)