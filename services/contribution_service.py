"""
Contribution Service: Manages member contributions to groups.

This service handles:
- Recording contributions
- Updating group balances
- Tracking contribution history
- Triggering score updates
"""

from datetime import datetime
from typing import Dict, Any
from data.data_manager import DataManager
from services.scoring_service import ScoringService
import config


class ContributionService:
    """Manages group contributions."""
    
    def __init__(self):
        """Initialize contribution service with data managers."""
        self.contributions = DataManager(config.CONTRIBUTIONS_FILE, 'contributions')
        self.groups = DataManager(config.GROUPS_FILE, 'groups')
        self.users = DataManager(config.USERS_FILE, 'users')
        self.scoring = ScoringService()
    
    def record_contribution(
        self,
        user_id: str,
        group_id: str,
        amount: float,
        duration_days: int
    ) -> Dict[str, Any]:
        """
        Record a member's contribution to a group.
        
        Args:
            user_id: User making the contribution
            group_id: Group receiving the contribution
            amount: Contribution amount
            duration_days: How long funds will stay deposited
            
        Returns:
            Dictionary with success status and contribution data
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
        
        # Generate contribution ID
        contribution_id = f"contrib_{datetime.now().timestamp()}".replace('.', '_')
        
        # Create contribution record
        contribution = {
            'id': contribution_id,
            'user_id': user_id,
            'group_id': group_id,
            'amount': amount,
            'duration_days': duration_days,
            'timestamp': datetime.now().isoformat()
        }
        
        success = self.contributions.create(contribution_id, contribution)
        
        if success:
            # Update group balance
            group['balance'] += amount
            self.groups.update(group_id, group)
            
            # Update user score
            self.scoring.update_user_score(user_id)
            
            return {
                'success': True,
                'contribution': contribution
            }
        else:
            return {
                'success': False,
                'message': 'Failed to record contribution'
            }
    
    def get_user_contributions(self, user_id: str) -> Dict[str, Any]:
        """
        Get all contributions made by a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with list of contributions
        """
        contributions = self.contributions.filter(
            lambda c: c['user_id'] == user_id
        )
        
        # Sort by timestamp (newest first)
        contributions.sort(key=lambda c: c['timestamp'], reverse=True)
        
        return {
            'success': True,
            'contributions': contributions
        }
    
    def get_group_contributions(self, group_id: str) -> Dict[str, Any]:
        """
        Get all contributions made to a group.
        
        Args:
            group_id: Group identifier
            
        Returns:
            Dictionary with list of contributions
        """
        contributions = self.contributions.filter(
            lambda c: c['group_id'] == group_id
        )
        
        # Sort by timestamp (newest first)
        contributions.sort(key=lambda c: c['timestamp'], reverse=True)
        
        # Enrich with user data
        for contribution in contributions:
            user = self.users.get(contribution['user_id'])
            if user:
                contribution['user_name'] = user['name']
        
        return {
            'success': True,
            'contributions': contributions
        }
