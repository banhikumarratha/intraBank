"""
Scoring Service: Isolated scoring engine for calculating user eligibility scores.

This service implements the scoring algorithm:
    Score = (Total Amount Contributed × AMOUNT_WEIGHT) + (Average Duration × DURATION_WEIGHT)

The scoring weights are configurable in config.py, making it easy to adjust the formula
without changing core logic.
"""

from typing import List, Dict, Any
from data.data_manager import DataManager
import config


class ScoringService:
    """Calculates and manages user eligibility scores."""
    
    def __init__(self):
        """Initialize scoring service with data managers."""
        self.users = DataManager(config.USERS_FILE, 'users')
        self.contributions = DataManager(config.CONTRIBUTIONS_FILE, 'contributions')
    
    def calculate_score(self, user_id: str) -> float:
        """
        Calculate a user's score based on their contributions.
        
        Formula: Score = (Total Amount × 0.6) + (Avg Duration × 0.4)
        Duration is calculated from the deposit date to today.
        
        Args:
            user_id: User identifier
            
        Returns:
            Calculated score
        """
        # Get all contributions for this user
        user_contributions = self.contributions.filter(
            lambda c: c['user_id'] == user_id
        )
        
        if not user_contributions:
            return 0.0
        
        # Calculate total amount
        total_amount = sum(c['amount'] for c in user_contributions)
        
        # Calculate average duration (days since deposit)
        from datetime import datetime
        now = datetime.now()
        total_duration = 0
        
        for contribution in user_contributions:
            # Parse contribution timestamp
            contrib_date = datetime.fromisoformat(contribution['timestamp'])
            # Calculate days since deposit
            days_active = (now - contrib_date).days
            total_duration += days_active
        
        avg_duration = total_duration / len(user_contributions)
        
        # Apply scoring formula
        amount_component = total_amount * config.SCORING_WEIGHTS['amount']
        duration_component = avg_duration * config.SCORING_WEIGHTS['duration']
        
        score = amount_component + duration_component
        
        return round(score, 2)
    
    def update_user_score(self, user_id: str) -> Dict[str, Any]:
        """
        Recalculate and update a user's score.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with success status and new score
        """
        user = self.users.get(user_id)
        if not user:
            return {
                'success': False,
                'message': 'User not found'
            }
        
        # Calculate new score
        new_score = self.calculate_score(user_id)
        
        # Update user record
        user['score'] = new_score
        self.users.update(user_id, user)
        
        return {
            'success': True,
            'score': new_score
        }
    
    def is_eligible_for_loan(self, user_id: str, loan_amount: float) -> Dict[str, Any]:
        """
        Check if a user is eligible for a loan based on their score.
        
        Args:
            user_id: User identifier
            loan_amount: Requested loan amount
            
        Returns:
            Dictionary with eligibility status and details
        """
        user = self.users.get(user_id)
        if not user:
            return {
                'eligible': False,
                'reason': 'User not found'
            }
        
        score = user['score']
        
        # Check minimum score requirement
        if score < config.MINIMUM_SCORE_FOR_LOAN:
            return {
                'eligible': False,
                'reason': f'Score too low. Minimum required: {config.MINIMUM_SCORE_FOR_LOAN}, current: {score}'
            }
        
        # Calculate maximum loan amount (score determines max loan)
        # Rule: User can borrow up to their score amount
        max_loan = score * 10  # Allow borrowing 10x the score
        
        if loan_amount > max_loan:
            return {
                'eligible': False,
                'reason': f'Loan amount too high. Maximum allowed: {max_loan:.2f}, requested: {loan_amount}'
            }
        
        return {
            'eligible': True,
            'score': score,
            'max_loan': max_loan
        }
