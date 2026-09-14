from flask import request, redirect, url_for, current_app
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from authlib.integrations.flask_client import OAuth
from flask_mailman import EmailMessage
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from .models import User, db
from . import user_datastore
from flask_security.utils import hash_password, verify_password
from flask_security import login_user
import os
from . import oauth, mail
import requests
import logging

# Configure a logger for this module
logger = logging.getLogger(__name__)

GALAXY_API_URL = os.getenv('GALAXY_URL') 
galaxy_user = None
GALAXY_API_TOKEN = "galaxy_api_token"

# Token serializer for password reset tokens
ts = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
class Register(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if User.query.filter_by(email=email).first():
            return {'message': 'User already exists'}, 400

        hashed_password = hash_password(password)
        new_user = user_datastore.create_user(email=email, password=hashed_password)
        db.session.commit()

        return {'message': 'User created successfully'}, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not verify_password(password, user.password):
            return {'message': 'Invalid credentials'}, 401

        galaxy_user = None
        try:
            response = requests.post(
                GALAXY_API_URL + "/register-user",
                params={"email": email, "password": password},
                timeout=5
            )
            # if response.status_code == 200:
            galaxy_user = response.json()
            galaxy_user = galaxy_user["api_token"]
        except requests.RequestException as e:
            logger.error("Error calling Galaxy API for user %s: %s", email, e)

        access_token = create_access_token(identity=user.id, additional_claims={"user_id": user.id, "email": user.email, GALAXY_API_TOKEN:galaxy_user})
        refresh_token = create_refresh_token(identity=user.id, additional_claims={"user_id": user.id, "email": user.email, GALAXY_API_TOKEN:galaxy_user})


        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }, 200

class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return {'message': 'Invalid Refresh Token'}, 401
        new_access_token = create_access_token(identity=current_user_id, additional_claims={"user_id": user.id, "user_email": user.email, GALAXY_API_TOKEN:galaxy_user})
        return {'access_token': new_access_token}, 200

class Protected(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        return {'message': f'Hello user {current_user_id}'}, 200

class GoogleLogin(Resource):
    def get(self):
        redirect_uri = url_for('api.googlecallback', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

class GoogleCallback(Resource):
    def get(self):
        token = oauth.google.authorize_access_token()
        user_info = token['userinfo']
        user = User.query.filter_by(email=user_info['email']).first()

        if not user:
            user = user_datastore.create_user(email=user_info['email'], password=hash_password(os.urandom(24)))
            db.session.commit()

        login_user(user)
        access_token = create_access_token(identity=user.id, additional_claims={"user_id": user.id, "email": user.email, GALAXY_API_TOKEN:galaxy_user})
        refresh_token = create_refresh_token(identity=user.id, additional_claims={"user_id": user.id, "email": user.email, GALAXY_API_TOKEN:galaxy_user})

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200

class GithubLogin(Resource):
    def get(self):
        redirect_uri = url_for('api.githubcallback', _external=True)
        return oauth.github.authorize_redirect(redirect_uri)

class GithubCallback(Resource):
    def get(self):
        token = oauth.github.authorize_access_token()
        user_info = oauth.github.get('https://api.github.com/user').json()
        user = User.query.filter_by(email=user_info['email']).first()

        if not user:
            user = user_datastore.create_user(email=user_info['email'], password=hash_password(os.urandom(24)))
            db.session.commit()

        login_user(user)
        access_token = create_access_token(identity=user.id, additional_claims={"user_id": user.id, "email": user.email, GALAXY_API_TOKEN:galaxy_user})
        refresh_token = create_refresh_token(identity=user.id, additional_claims={"user_id": user.id, "email": user.email, GALAXY_API_TOKEN:galaxy_user})

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200

class RequestResetPassword(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        base_url = os.getenv("PLATFORM_URL")
        if user is None:
            return {'message': 'No user found with this email'}, 400
        
        token = ts.dumps(user.email, salt=os.getenv('SECURITY_PASSWORD_SALT'))
        reset_url = f"{base_url}/resetpassword?token={token}"
        msg = EmailMessage(
            subject='Password Reset Request',
            body=f'''To reset your password, visit the following link: {reset_url} 
            If you did not make this request, please ignore this email.''',
            to=[user.email],
        )
        msg.send()
        return {'message': 'Password reset link has been sent to your email'}, 200

class ResetPassword(Resource):
    def post(self, token):
        try:
            email = ts.loads(token, salt=os.getenv('SECURITY_PASSWORD_SALT'), max_age=86400)
        except (SignatureExpired, BadSignature):
            return {'message': 'Invalid or expired token'}, 400

        user = User.query.filter_by(email=email).first()
        if user is None:
            return {'message': 'Invalid user'}, 400

        data = request.get_json()
        password = data.get('password')
        user.password = hash_password(password)
        db.session.commit()

        return {'message': 'Your password has been reset'}, 200
