from flask import request, jsonify
from firebase_admin import auth, initialize_app
import firebase_admin

if not firebase_admin._apps:
    initialize_app()

def verify_token(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        
        token = auth_header.split("Bearer ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
            request.user_uid = decoded_token['uid']
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401
    wrapper.__name__ = func.__name__
    return wrapper