# Python Web App with AWS Cognito Authentication

This project demonstrates a simple Python web application using Flask and AWS Cognito for authentication. The application supports both Hosted UI and custom login page for user authentication.

## Table of Contents
- Project Scope
- Branches
- AWS Cognito Setup
- Local Development Setup
- Routes
- Execution and Testing

## Project Scope
This project aims to provide a secure authentication mechanism using AWS Cognito. It supports:
- Hosted UI for authentication
- Custom login page for authentication
- Secure Remote Password (SRP) authentication flow

## Branches
### `secure-hosted-noui`
- This branch implements authentication using a custom login page without the Hosted UI.
- Users can log in using their username and password directly on the application.

### `secure-hosted-ui`
- This branch implements authentication using the AWS Cognito Hosted UI.
- Users are redirected to the Hosted UI for authentication.

### `secure-hosted-ui-improved`
- This branch combines both Hosted UI and custom login page.
- If the Hosted UI is configured, users are redirected to it for authentication.
- If the Hosted UI is not configured, the application shows its own login page.
- This branch includes logic to handle both scenarios and logs the chosen authentication flow and login option.

## AWS Cognito Setup
1. **Create a User Pool**:
    - Go to the AWS Cognito Console.
    - Create a new User Pool and configure it according to your requirements.
    - Note down the User Pool ID.

2. **Create an App Client**:
    - In the User Pool, create a new App Client.
    - Enable `ALLOW_USER_SRP_AUTH` as the authentication flow.
    - If using Hosted UI, configure the callback URLs and sign-out URLs.
    - Note down the App Client ID.

3. **Configure Hosted UI (if applicable)**:
    - In the App Client settings, enable the Hosted UI.
    - Configure the callback URLs and sign-out URLs.

## Local Development Setup
1. **Clone the Repository**:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Checkout the Desired Branch**:
    ```sh
    git checkout <branch_name>
    ```

3. **Create a Virtual Environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

5. **Create a `.env` File**:
    - Create a `.env` file in the project directory with the following content:
    ```env
    USER_POOL_ID=your_user_pool_id
    CLIENT_ID=your_app_client_id
    REGION=your_aws_region
    REDIRECT_URI=http://localhost:5000/callback
    COGNITO_DOMAIN=your_cognito_domain
    APP_CLIENT_SCOPE=openid+profile
    ```

## Routes
- **Home (`/`)**: Displays the welcome message and user profile information if logged in.
- **Login (`/login`)**: Handles user login. Redirects to Hosted UI if configured, otherwise shows the custom login page.
- **Callback (`/callback`)**: Handles the OAuth2 callback from the Hosted UI.
- **Logout (`/logout`)**: Logs out the user and redirects to the home page.

## Execution and Testing
1. **Run the Application**:
    ```sh
    python app.py
    ```

2. **Access the Web App**:
    - Open your web browser and go to `http://localhost:5000/`.
    - Log in using the appropriate method (Hosted UI or custom login page).
    - Verify that the welcome message and user profile information are displayed.
    - Click the logout button to log out and verify that you are redirected to the home page.

## Logging
- The application logs the chosen authentication flow and login option.
- Logs are printed to the console for easy debugging and monitoring.

Feel free to reach out if you have any questions or need further assistance!
