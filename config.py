"""
Configuration module for the Savings & Loan Application.

This module centralizes all configuration constants, making it easy to:
- Adjust business rules without touching core logic
- Switch storage backends in the future
- Configure scoring weights and loan parameters
"""

import os

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data storage paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
GROUPS_FILE = os.path.join(DATA_DIR, 'groups.json')
CONTRIBUTIONS_FILE = os.path.join(DATA_DIR, 'contributions.json')
LOANS_FILE = os.path.join(DATA_DIR, 'loans.json')
SESSIONS_FILE = os.path.join(DATA_DIR, 'sessions.json')

# Scoring configuration
# Score = (Total Amount × AMOUNT_WEIGHT) + (Average Duration × DURATION_WEIGHT)
SCORING_WEIGHTS = {
    'amount': 0.6,      # 60% weight for contribution amount
    'duration': 0.4     # 40% weight for contribution duration
}

# Loan configuration
MINIMUM_SCORE_FOR_LOAN = 100  # Minimum score required to request a loan
LOAN_APPROVAL_MAJORITY = 0.5   # 50% of members must vote yes for approval

# Session configuration
SESSION_TIMEOUT_HOURS = 24

# Flask configuration
SECRET_KEY = 'dev-secret-key-change-in-production'
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# Security configuration (for password hashing)
PASSWORD_SALT = 'loan-app-salt-2024'  # Change in production
