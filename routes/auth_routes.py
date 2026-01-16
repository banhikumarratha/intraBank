"""
Authentication routes: Handle user registration, login, and session management.
"""

from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate input
    if not data or not all(k in data for k in ['name', 'email', 'password']):
        return jsonify({
            'success': False,
            'message': 'Name, email, and password are required'
        }), 400
    
    result = auth_service.register(
        name=data['name'],
        email=data['email'],
        password=data['password']
    )
    
    status_code = 201 if result['success'] else 400
    return jsonify(result), status_code


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user."""
    data = request.get_json()
    
    # Validate input
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({
            'success': False,
            'message': 'Email and password are required'
        }), 400
    
    result = auth_service.login(
        email=data['email'],
        password=data['password']
    )
    
    status_code = 200 if result['success'] else 401
    return jsonify(result), status_code


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout a user."""
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({
            'success': False,
            'message': 'Authorization token required'
        }), 401
    
    # Remove 'Bearer ' prefix if present
    if token.startswith('Bearer '):
        token = token[7:]
    
    result = auth_service.logout(token)
    return jsonify(result), 200


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information."""
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({
            'success': False,
            'message': 'Authorization token required'
        }), 401
    
    # Remove 'Bearer ' prefix if present
    if token.startswith('Bearer '):
        token = token[7:]
    
    user = auth_service.validate_session(token)
    
    if user:
        return jsonify({
            'success': True,
            'user': user
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid or expired session'
        }), 401
