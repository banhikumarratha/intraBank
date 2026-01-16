"""
Group Service: Manages group creation, membership, and administration.

This service handles:
- Group creation (creator becomes admin)
- Member management
- Admin promotion
- Interest rate configuration
- Group statistics
"""

from datetime import datetime
from typing import Dict, Any, List
from data.data_manager import DataManager
import config


class GroupService:
    """Manages savings groups."""
    
    def __init__(self):
        """Initialize group service with data managers."""
        self.groups = DataManager(config.GROUPS_FILE, 'groups')
        self.users = DataManager(config.USERS_FILE, 'users')
    
    def create_group(self, name: str, creator_id: str) -> Dict[str, Any]:
        """
        Create a new group with the creator as admin.
        
        Args:
            name: Group name
            creator_id: ID of user creating the group
            
        Returns:
            Dictionary with success status and group data
        """
        # Verify creator exists
        creator = self.users.get(creator_id)
        if not creator:
            return {
                'success': False,
                'message': 'Creator not found'
            }
        
        # Generate group ID
        group_id = f"group_{datetime.now().timestamp()}".replace('.', '_')
        
        # Create group record
        group = {
            'id': group_id,
            'name': name,
            'admins': [creator_id],
            'members': [creator_id],
            'balance': 0.0,
            'interest_rate': 0.05,  # Default 5% interest
            'created_at': datetime.now().isoformat()
        }
        
        success = self.groups.create(group_id, group)
        
        if success:
            # Update user's group list
            creator['groups'].append(group_id)
            self.users.update(creator_id, creator)
            
            return {
                'success': True,
                'group': group
            }
        else:
            return {
                'success': False,
                'message': 'Failed to create group'
            }
    
    def add_member(self, group_id: str, user_id: str, admin_id: str) -> Dict[str, Any]:
        """
        Add a user to a group (admin only).
        
        Args:
            group_id: Group identifier
            user_id: ID of user to add
            admin_id: ID of admin making the request
            
        Returns:
            Dictionary with success status
        """
        group = self.groups.get(group_id)
        if not group:
            return {
                'success': False,
                'message': 'Group not found'
            }
        
        # Verify requester is admin
        if admin_id not in group['admins']:
            return {
                'success': False,
                'message': 'Only admins can add members'
            }
        
        # Verify user exists
        user = self.users.get(user_id)
        if not user:
            return {
                'success': False,
                'message': 'User not found'
            }
        
        # Check if already a member
        if user_id in group['members']:
            return {
                'success': False,
                'message': 'User already a member'
            }
        
        # Add to group
        group['members'].append(user_id)
        self.groups.update(group_id, group)
        
        # Update user's group list
        user['groups'].append(group_id)
        self.users.update(user_id, user)
        
        return {
            'success': True,
            'message': 'Member added successfully'
        }
    
    def promote_to_admin(self, group_id: str, user_id: str, admin_id: str) -> Dict[str, Any]:
        """
        Promote a member to admin (admin only).
        
        Args:
            group_id: Group identifier
            user_id: ID of user to promote
            admin_id: ID of admin making the request
            
        Returns:
            Dictionary with success status
        """
        group = self.groups.get(group_id)
        if not group:
            return {
                'success': False,
                'message': 'Group not found'
            }
        
        # Verify requester is admin
        if admin_id not in group['admins']:
            return {
                'success': False,
                'message': 'Only admins can promote members'
            }
        
        # Verify user is a member
        if user_id not in group['members']:
            return {
                'success': False,
                'message': 'User is not a member of this group'
            }
        
        # Check if already admin
        if user_id in group['admins']:
            return {
                'success': False,
                'message': 'User is already an admin'
            }
        
        # Promote to admin
        group['admins'].append(user_id)
        self.groups.update(group_id, group)
        
        return {
            'success': True,
            'message': 'User promoted to admin'
        }
    
    def update_interest_rate(self, group_id: str, rate: float, admin_id: str) -> Dict[str, Any]:
        """
        Update group's loan interest rate (admin only).
        
        Args:
            group_id: Group identifier
            rate: New interest rate (e.g., 0.05 for 5%)
            admin_id: ID of admin making the request
            
        Returns:
            Dictionary with success status
        """
        group = self.groups.get(group_id)
        if not group:
            return {
                'success': False,
                'message': 'Group not found'
            }
        
        # Verify requester is admin
        if admin_id not in group['admins']:
            return {
                'success': False,
                'message': 'Only admins can update interest rate'
            }
        
        # Validate rate
        if rate < 0 or rate > 1:
            return {
                'success': False,
                'message': 'Interest rate must be between 0 and 1'
            }
        
        # Update rate
        group['interest_rate'] = rate
        self.groups.update(group_id, group)
        
        return {
            'success': True,
            'message': f'Interest rate updated to {rate * 100}%'
        }
    
    def get_group(self, group_id: str) -> Dict[str, Any]:
        """
        Get group details with member information.
        
        Args:
            group_id: Group identifier
            
        Returns:
            Dictionary with group data
        """
        group = self.groups.get(group_id)
        if not group:
            return {
                'success': False,
                'message': 'Group not found'
            }
        
        # Enrich with member details
        members_data = []
        for member_id in group['members']:
            user = self.users.get(member_id)
            if user:
                members_data.append({
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'score': user['score'],
                    'is_admin': member_id in group['admins']
                })
        
        group['members_data'] = members_data
        
        return {
            'success': True,
            'group': group
        }
    
    def get_user_groups(self, user_id: str) -> Dict[str, Any]:
        """
        Get all groups a user belongs to.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with list of groups
        """
        user = self.users.get(user_id)
        if not user:
            return {
                'success': False,
                'message': 'User not found'
            }
        
        groups = []
        for group_id in user['groups']:
            group = self.groups.get(group_id)
            if group:
                groups.append(group)
        
        return {
            'success': True,
            'groups': groups
        }
