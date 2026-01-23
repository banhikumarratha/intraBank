"""
Loan Service: Manages loan requests, approvals, and repayments.

This service handles:
- Loan requests with eligibility checks
- Admin approval workflow
- Member voting workflow
- Automatic approval on majority vote
- Repayment tracking
- Interest calculation
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from data.data_manager import DataManager
from services.scoring_service import ScoringService
import config


class LoanService:
    """Manages group loans."""
    
    def __init__(self):
        """Initialize loan service with data managers."""
        self.loans = DataManager(config.LOANS_FILE, 'loans')
        self.groups = DataManager(config.GROUPS_FILE, 'groups')
        self.users = DataManager(config.USERS_FILE, 'users')
        self.scoring = ScoringService()
    
    def request_loan(
        self,
        user_id: str,
        group_id: str,
        amount: float,
        duration_days: int
    ) -> Dict[str, Any]:
        """
        Request a loan from a group's pool.
        
        Args:
            user_id: User requesting the loan
            group_id: Group to borrow from
            amount: Loan amount
            duration_days: Loan duration
            
        Returns:
            Dictionary with success status and loan data
        """
        # Verify user exists
        user = self.users.get(user_id)
        if not user:
            return {
                'success': False,
                'message': 'User not found'
            }
        
        # Verify group exists
        group = self.groups.get(group_id)
        if not group:
            return {
                'success': False,
                'message': 'Group not found'
            }
        
        # Verify user is a member
        if user_id not in group['members']:
            return {
                'success': False,
                'message': 'User is not a member of this group'
            }
        
        # Check eligibility
        eligibility = self.scoring.is_eligible_for_loan(user_id, amount)
        if not eligibility['eligible']:
            return {
                'success': False,
                'message': eligibility['reason']
            }
        
        # Check if group has sufficient balance
        if group['balance'] < amount:
            return {
                'success': False,
                'message': f'Insufficient group balance. Available: {group["balance"]:.2f}, requested: {amount}'
            }
        
        # Validate amount
        if amount <= 0:
            return {
                'success': False,
                'message': 'Amount must be positive'
            }
        
        # Validate duration
        if duration_days <= 0:
            return {
                'success': False,
                'message': 'Duration must be positive'
            }
        
        # Generate loan ID
        loan_id = f"loan_{datetime.now().timestamp()}".replace('.', '_')
        
        # Create loan record
        loan = {
            'id': loan_id,
            'user_id': user_id,
            'group_id': group_id,
            'amount': amount,
            'duration_days': duration_days,
            'interest_rate': group['interest_rate'],
            'status': 'pending',
            'admin_approved_by': None,  # Track which admin approved
            'member_votes': {},
            'requested_at': datetime.now().isoformat(),
            'approved_at': None,
            'due_date': None,
            'repaid_at': None
        }
        
        success = self.loans.create(loan_id, loan)
        
        if success:
            return {
                'success': True,
                'loan': loan
            }
        else:
            return {
                'success': False,
                'message': 'Failed to create loan request'
            }
    
    def admin_approve(self, loan_id: str, admin_id: str) -> Dict[str, Any]:
        """
        Admin approves a loan request.
        
        Args:
            loan_id: Loan identifier
            admin_id: Admin making the approval
            
        Returns:
            Dictionary with success status
        """
        loan = self.loans.get(loan_id)
        if not loan:
            return {
                'success': False,
                'message': 'Loan not found'
            }
        
        # Verify loan is pending
        if loan['status'] != 'pending':
            return {
                'success': False,
                'message': f'Loan is already {loan["status"]}'
            }
        
        # Verify admin belongs to group
        group = self.groups.get(loan['group_id'])
        if not group:
            return {
                'success': False,
                'message': 'Group not found'
            }
        
        if admin_id not in group['admins']:
            return {
                'success': False,
                'message': 'Only admins can approve loans'
            }
        
        # Approve the loan and record admin
        return self._approve_loan(loan_id, admin_id=admin_id)
    
    def member_vote(self, loan_id: str, user_id: str, approve: bool) -> Dict[str, Any]:
        """
        Member votes on a loan request.
        
        Args:
            loan_id: Loan identifier
            user_id: Member voting
            approve: True to approve, False to reject
            
        Returns:
            Dictionary with success status
        """
        loan = self.loans.get(loan_id)
        if not loan:
            return {
                'success': False,
                'message': 'Loan not found'
            }
        
        # Verify loan is pending
        if loan['status'] != 'pending':
            return {
                'success': False,
                'message': f'Loan is already {loan["status"]}'
            }
        
        # Verify user is a member
        group = self.groups.get(loan['group_id'])
        if not group:
            return {
                'success': False,
                'message': 'Group not found'
            }
        
        if user_id not in group['members']:
            return {
                'success': False,
                'message': 'Only group members can vote'
            }
        
        # Record vote
        loan['member_votes'][user_id] = approve
        self.loans.update(loan_id, loan)
        
        # Check if majority reached
        total_members = len(group['members'])
        approve_votes = sum(1 for vote in loan['member_votes'].values() if vote)
        reject_votes = sum(1 for vote in loan['member_votes'].values() if not vote)
        
        majority_threshold = total_members * config.LOAN_APPROVAL_MAJORITY
        
        if approve_votes > majority_threshold:
            # Majority approved - auto-approve loan
            return self._approve_loan(loan_id)
        elif reject_votes > majority_threshold:
            # Majority rejected - auto-reject loan
            loan['status'] = 'rejected'
            self.loans.update(loan_id, loan)
            return {
                'success': True,
                'message': 'Loan rejected by majority vote',
                'status': 'rejected'
            }
        else:
            return {
                'success': True,
                'message': f'Vote recorded. Approvals: {approve_votes}/{total_members}, Rejections: {reject_votes}/{total_members}',
                'status': 'pending'
            }
    
    def _approve_loan(self, loan_id: str, admin_id: str = None) -> Dict[str, Any]:
        """
        Internal method to approve a loan and deduct from group balance.
        
        Args:
            loan_id: Loan identifier
            admin_id: Optional admin ID who approved (for admin approval tracking)
            
        Returns:
            Dictionary with success status
        """
        loan = self.loans.get(loan_id)
        group = self.groups.get(loan['group_id'])
        
        # Double-check balance
        if group['balance'] < loan['amount']:
            loan['status'] = 'rejected'
            loan['rejection_reason'] = 'Insufficient group balance'
            self.loans.update(loan_id, loan)
            return {
                'success': False,
                'message': 'Insufficient group balance'
            }
        
        # Approve loan
        loan['status'] = 'approved'
        loan['approved_at'] = datetime.now().isoformat()
        due_date = datetime.now() + timedelta(days=loan['duration_days'])
        loan['due_date'] = due_date.isoformat()
        
        # Record who approved (if admin approval)
        if admin_id:
            loan['admin_approved_by'] = admin_id
        
        # Deduct from group balance
        group['balance'] -= loan['amount']
        
        # Update records
        self.loans.update(loan_id, loan)
        self.groups.update(loan['group_id'], group)
        
        return {
            'success': True,
            'message': 'Loan approved',
            'loan': loan
        }
    
    def repay_loan(self, loan_id: str, user_id: str) -> Dict[str, Any]:
        """
        Record a loan repayment.
        
        Args:
            loan_id: Loan identifier
            user_id: User making the repayment
            
        Returns:
            Dictionary with success status and repayment details
        """
        loan = self.loans.get(loan_id)
        if not loan:
            return {
                'success': False,
                'message': 'Loan not found'
            }
        
        # Verify loan belongs to user
        if loan['user_id'] != user_id:
            return {
                'success': False,
                'message': 'This loan does not belong to you'
            }
        
        # Verify loan is approved
        if loan['status'] != 'approved':
            return {
                'success': False,
                'message': f'Cannot repay a {loan["status"]} loan'
            }
        
        # Calculate total repayment (principal + interest)
        principal = loan['amount']
        interest = principal * loan['interest_rate']
        total_repayment = principal + interest
        
        # Update loan status
        loan['status'] = 'repaid'
        loan['repaid_at'] = datetime.now().isoformat()
        loan['total_repayment'] = total_repayment
        
        # Return money to group (principal + interest)
        group = self.groups.get(loan['group_id'])
        group['balance'] += total_repayment
        
        # Update records
        self.loans.update(loan_id, loan)
        self.groups.update(loan['group_id'], group)
        
        return {
            'success': True,
            'message': 'Loan repaid successfully',
            'principal': principal,
            'interest': interest,
            'total': total_repayment
        }
    
    def get_user_loans(self, user_id: str) -> Dict[str, Any]:
        """
        Get all loans for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with list of loans
        """
        loans = self.loans.filter(lambda l: l['user_id'] == user_id)
        
        # Sort by timestamp (newest first)
        loans.sort(key=lambda l: l['requested_at'], reverse=True)
        
        return {
            'success': True,
            'loans': loans
        }
    
    def get_group_loans(self, group_id: str) -> Dict[str, Any]:
        """
        Get all loans for a group.
        
        Args:
            group_id: Group identifier
            
        Returns:
            Dictionary with list of loans
        """
        loans = self.loans.filter(lambda l: l['group_id'] == group_id)
        
        # Sort by timestamp (newest first)
        loans.sort(key=lambda l: l['requested_at'], reverse=True)
        
        # Enrich with user data
        for loan in loans:
            user = self.users.get(loan['user_id'])
            if user:
                loan['user_name'] = user['name']
        
        return {
            'success': True,
            'loans': loans
        }
    
    def get_loan(self, loan_id: str) -> Dict[str, Any]:
        """
        Get loan details.
        
        Args:
            loan_id: Loan identifier
            
        Returns:
            Dictionary with loan data
        """
        loan = self.loans.get(loan_id)
        if not loan:
            return {
                'success': False,
                'message': 'Loan not found'
            }
        
        return {
            'success': True,
            'loan': loan
        }
