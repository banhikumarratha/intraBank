"""
Loan routes: Handle loan requests, approvals, voting, and repayments.
"""

from flask import Blueprint, request, jsonify
from services.loan_service import LoanService
from services.auth_service import AuthService

loan_bp = Blueprint('loans', __name__)
loan_service = LoanService()
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


@loan_bp.route('', methods=['POST'])
def request_loan():
    """Request a new loan."""
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    data = request.get_json()
    
    # Validate input
    required_fields = ['group_id', 'amount', 'duration_days']
    if not data or not all(k in data for k in required_fields):
        return jsonify({
            'success': False,
            'message': 'Group ID, amount, and duration are required'
        }), 400
    
    result = loan_service.request_loan(
        user_id=user_id,
        group_id=data['group_id'],
        amount=data['amount'],
        duration_days=data['duration_days']
    )
    
    status_code = 201 if result['success'] else 400
    return jsonify(result), status_code


@loan_bp.route('/<loan_id>', methods=['GET'])
def get_loan(loan_id):
    """Get loan details."""
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    result = loan_service.get_loan(loan_id)
    
    status_code = 200 if result['success'] else 404
    return jsonify(result), status_code


@loan_bp.route('/<loan_id>/approve', methods=['POST'])
def approve_loan(loan_id):
    """Admin approves a loan."""
    admin_id = get_current_user_id(request)
    if not admin_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    result = loan_service.admin_approve(
        loan_id=loan_id,
        admin_id=admin_id
    )
    
    status_code = 200 if result['success'] else 403
    return jsonify(result), status_code


@loan_bp.route('/<loan_id>/vote', methods=['POST'])
def vote_on_loan(loan_id):
    """Member votes on a loan."""
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    data = request.get_json()
    
    # Validate input
    if not data or 'approve' not in data:
        return jsonify({
            'success': False,
            'message': 'Vote (approve: true/false) is required'
        }), 400
    
    result = loan_service.member_vote(
        loan_id=loan_id,
        user_id=user_id,
        approve=data['approve']
    )
    
    status_code = 200 if result['success'] else 403
    return jsonify(result), status_code


@loan_bp.route('/<loan_id>/repay', methods=['POST'])
def repay_loan(loan_id):
    """Repay a loan."""
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    result = loan_service.repay_loan(
        loan_id=loan_id,
        user_id=user_id
    )
    
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code


@loan_bp.route('/user/<user_id>', methods=['GET'])
def get_user_loans(user_id):
    """Get all loans for a user."""
    current_user_id = get_current_user_id(request)
    if not current_user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    result = loan_service.get_user_loans(user_id)
    return jsonify(result), 200


@loan_bp.route('/group/<group_id>', methods=['GET'])
def get_group_loans(group_id):
    """Get all loans for a group."""
    current_user_id = get_current_user_id(request)
    if not current_user_id:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    result = loan_service.get_group_loans(group_id)
    return jsonify(result), 200
