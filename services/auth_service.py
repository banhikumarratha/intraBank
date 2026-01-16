"""
Authentication Service: Handles user registration, login, and session management.

This service provides:
- Secure password hashing
- Session token generation
- User authentication
- Session validation
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from data.data_manager import DataManager
import config


class AuthService:
    """Manages user authentication and sessions."""
    
    def __init__(self):
        """Initialize authentication service with data managers."""
        self.users = DataManager(config.USERS_FILE, 'users')
        self.sessions = DataManager(config.SESSIONS_FILE, 'sessions')
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256 with salt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salted = password + config.PASSWORD_SALT
        return hashlib.sha256(salted.encode()).hexdigest()
    
    def _generate_token(self) -> str:
        """
        Generate a secure random session token.
        
        Returns:
            Random token string
        """
        return secrets.token_urlsafe(32)
    
    def register(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            name: User's full name
            email: User's email address
            password: Plain text password
            
        Returns:
            Dictionary with success status and message/user data
        """
        # Validate email uniqueness
        existing_user = self.users.find(lambda u: u['email'] == email)
        if existing_user:
            return {
                'success': False,
                'message': 'Email already registered'
            }
        
        # Create user ID from email
        user_id = email.lower().replace('@', '_at_').replace('.', '_')
        
        # Create user record
        user = {
            'id': user_id,
            'name': name,
            'email': email,
            'password_hash': self._hash_password(password),
            'groups': [],
            'score': 0.0,
            'created_at': datetime.now().isoformat()
        }
        
        success = self.users.create(user_id, user)
        
        if success:
            # Remove sensitive data before returning
            safe_user = {k: v for k, v in user.items() if k != 'password_hash'}
            return {
                'success': True,
                'user': safe_user
            }
        else:
            return {
                'success': False,
                'message': 'Failed to create user'
            }
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and create a session.
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            Dictionary with success status and session token/user data
        """
        # Find user by email
        user = self.users.find(lambda u: u['email'] == email)
        
        if not user:
            return {
                'success': False,
                'message': 'Invalid email or password'
            }
        
        # Verify password
        password_hash = self._hash_password(password)
        if user['password_hash'] != password_hash:
            return {
                'success': False,
                'message': 'Invalid email or password'
            }
        
        # Create session
        token = self._generate_token()
        session = {
            'token': token,
            'user_id': user['id'],
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=config.SESSION_TIMEOUT_HOURS)).isoformat()
        }
        
        self.sessions.upsert(token, session)
        
        # Remove sensitive data before returning
        safe_user = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return {
            'success': True,
            'token': token,
            'user': safe_user
        }
    
    def logout(self, token: str) -> Dict[str, Any]:
        """
        End a user session.
        
        Args:
            token: Session token
            
        Returns:
            Dictionary with success status
        """
        success = self.sessions.delete(token)
        return {
            'success': success,
            'message': 'Logged out successfully' if success else 'Session not found'
        }
    
    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a session token and return user data.
        
        Args:
            token: Session token
            
        Returns:
            User dictionary if valid, None otherwise
        """
        session = self.sessions.get(token)
        
        if not session:
            return None
        
        # Check if session expired
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            self.sessions.delete(token)
            return None
        
        # Get user data
        user = self.users.get(session['user_id'])
        if not user:
            return None
        
        # Remove sensitive data
        safe_user = {k: v for k, v in user.items() if k != 'password_hash'}
        return safe_user
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User dictionary (without password) or None
        """
        user = self.users.get(user_id)
        if not user:
            return None
        
        safe_user = {k: v for k, v in user.items() if k != 'password_hash'}
        return safe_user
