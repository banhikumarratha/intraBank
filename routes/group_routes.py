"""
Group routes: Handle group creation, membership, and administration.
"""

from flask import Blueprint, request, jsonify
from services.group_service import GroupService
from services.auth_service import AuthService

group_bp = Blueprint('groups', __name__)
group_service = GroupService()
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


@group_bp.route('', methods=['POST'])
def create_group():
    """Create a new group."""
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    data = request.get_json()
    
    # Validate input
    if not data or 'name' not in data:
        return jsonify({
            'success': False,
            'message': 'Group name is required'
        }), 400
    
    result = group_service.create_group(
        name=data['name'],
        creator_id=user_id
    )
    
    status_code = 201 if result['success'] else 400
    return jsonify(result), status_code


@group_bp.route('/<group_id>', methods=['GET'])
def get_group(group_id):
    """Get group details."""
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    result = group_service.get_group(group_id)
    
    status_code = 200 if result['success'] else 404
    return jsonify(result), status_code


@group_bp.route('/user/<user_id>', methods=['GET'])
def get_user_groups(user_id):
    """Get all groups for a user."""
    current_user_id = get_current_user_id(request)
    if not current_user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    result = group_service.get_user_groups(user_id)
    
    status_code = 200 if result['success'] else 404
    return jsonify(result), status_code


@group_bp.route('/<group_id>/members', methods=['POST'])
def add_member(group_id):
    """Add a member to a group."""
    admin_id = get_current_user_id(request)
    if not admin_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    data = request.get_json()
    
    # Validate input
    if not data or 'user_id' not in data:
        return jsonify({
            'success': False,
            'message': 'User ID is required'
        }), 400
    
    result = group_service.add_member(
        group_id=group_id,
        user_id=data['user_id'],
        admin_id=admin_id
    )
    
    status_code = 200 if result['success'] else 403
    return jsonify(result), status_code


@group_bp.route('/<group_id>/admins', methods=['POST'])
def promote_to_admin(group_id):
    """Promote a member to admin."""
    admin_id = get_current_user_id(request)
    if not admin_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    data = request.get_json()
    
    # Validate input
    if not data or 'user_id' not in data:
        return jsonify({
            'success': False,
            'message': 'User ID is required'
        }), 400
    
    result = group_service.promote_to_admin(
        group_id=group_id,
        user_id=data['user_id'],
        admin_id=admin_id
    )
    
    status_code = 200 if result['success'] else 403
    return jsonify(result), status_code


@group_bp.route('/<group_id>/interest', methods=['PUT'])
def update_interest_rate(group_id):
    """Update group's interest rate."""
    admin_id = get_current_user_id(request)
    if not admin_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    data = request.get_json()
    
    # Validate input
    if not data or 'rate' not in data:
        return jsonify({
            'success': False,
            'message': 'Interest rate is required'
        }), 400
    
    result = group_service.update_interest_rate(
        group_id=group_id,
        rate=data['rate'],
        admin_id=admin_id
    )
    
    status_code = 200 if result['success'] else 403
    return jsonify(result), status_code
