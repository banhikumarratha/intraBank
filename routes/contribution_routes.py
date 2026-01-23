"""
Contribution routes: Handle contribution recording and history.
"""

from flask import Blueprint, request, jsonify
from services.contribution_service import ContributionService
from services.auth_service import AuthService

contribution_bp = Blueprint('contributions', __name__)
contribution_service = ContributionService()
auth_service = AuthService()


def get_current_user_id(request):
    """Extract and validate user ID from authorization token."""
    token = request.headers.get('Authorization')
    if not token:
        return None
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    user = auth_service.validate_session(token)
    return user['id'] if user else None


@contribution_bp.route('', methods=['POST'])
def record_contribution():
    """Record a new contribution."""
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    data = request.get_json()
    
    # Validate input
    required_fields = ['group_id', 'amount']
    if not data or not all(k in data for k in required_fields):
        return jsonify({
            'success': False,
            'message': 'Group ID and amount are required'
        }), 400
    
    result = contribution_service.record_contribution(
        user_id=user_id,
        group_id=data['group_id'],
        amount=data['amount']
    )
    
    status_code = 201 if result['success'] else 400
    return jsonify(result), status_code


@contribution_bp.route('/user/<user_id>', methods=['GET'])
def get_user_contributions(user_id):
    """Get all contributions by a user."""
    current_user_id = get_current_user_id(request)
    if not current_user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    result = contribution_service.get_user_contributions(user_id)
    return jsonify(result), 200


@contribution_bp.route('/group/<group_id>', methods=['GET'])
def get_group_contributions(group_id):
    """Get all contributions to a group."""
    current_user_id = get_current_user_id(request)
    if not current_user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    result = contribution_service.get_group_contributions(group_id)
    return jsonify(result), 200
