# 💰 SaveLoan - Group Savings & Loan Application

A production-quality web application for managing group-based savings and loans. Members form groups, contribute funds, earn eligibility scores, and request loans with configurable interest rates and dual approval workflows.

## ✨ Features

### 👥 User Management
- Secure registration and authentication
- Password hashing with SHA-256
- Session-based access control
- User eligibility scoring

### 🏦 Group Management
- Create and join savings groups
- Multi-admin support
- Member management (add/remove/promote)
- Configurable group interest rates
- Real-time group balance tracking

### 💵 Contribution System
- Record monetary contributions
- Track contribution duration
- Automatic score updates
- Contribution history tracking

### 📊 Scoring Engine
**Formula:** `Score = (Total Amount × 0.6) + (Average Duration × 0.4)`

The scoring system rewards both:
- **Amount contributed** (60% weight)
- **Commitment duration** (40% weight)

Scores determine:
- Loan eligibility (minimum score required)
- Maximum loan amount (10× your score)

### 💳 Loan System
- Request loans from group pools
- **Dual approval workflow:**
  - Admin approval (any admin can approve), OR
  - Member voting (>50% majority required)
- Automatic approval on majority vote
- Interest calculation and repayment tracking
- Loan status management (pending/approved/rejected/repaid)

### 🎨 Modern UI
- Fully responsive design (mobile, tablet, desktop)
- **Google Pay inspired theme** with clean light design
- Material Design elevation shadows
- Blue and green accent colors
- Smooth animations and transitions
- Real-time updates

## 🏗️ Architecture

### Backend (Python Flask)
```
project/
├── app.py                 # Flask application entry point
├── config.py              # Configuration constants
├── data/
│   ├── data_manager.py    # JSON storage abstraction
│   ├── users.json         # User data
│   ├── groups.json        # Group data
│   ├── contributions.json # Contribution records
│   ├── loans.json         # Loan records
│   └── sessions.json      # Session tokens
├── services/
│   ├── auth_service.py    # Authentication logic
│   ├── group_service.py   # Group management
│   ├── contribution_service.py  # Contribution handling
│   ├── scoring_service.py # Score calculation
│   └── loan_service.py    # Loan management
└── routes/
    ├── auth_routes.py     # Auth endpoints
    ├── group_routes.py    # Group endpoints
    ├── contribution_routes.py  # Contribution endpoints
    └── loan_routes.py     # Loan endpoints
```

### Frontend (HTML/CSS/JavaScript)
```
project/
├── templates/
│   └── index.html         # Single-page app shell
└── static/
    ├── css/
    │   └── style.css      # Responsive styles
    └── js/
        ├── app.js         # App controller & routing
        ├── auth.js        # Login/register UI
        ├── dashboard.js   # User dashboard
        ├── groups.js      # Group management UI
        ├── contributions.js  # Contribution UI
        └── loans.js       # Loan UI
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd /Users/banhi/Desktop/project
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create default test users (OPTIONAL):**
```bash
python create_test_users.py
```

This creates 5 test users with simple passwords for easy testing:
- **Alice Johnson** - Email: `alice@test.com`, Password: `alice`
- **Bob Smith** - Email: `bob@test.com`, Password: `bob`
- **Charlie Davis** - Email: `charlie@test.com`, Password: `charlie`
- **Diana Chen** - Email: `diana@test.com`, Password: `diana`
- **Eve Martinez** - Email: `eve@test.com`, Password: `eve`

4. **Run the application:**
```bash
python app.py
```

5. **Open your browser:**
```
http://localhost:5000
```

The application is now running! 🎉

## 📖 Usage Guide

### 1. Create an Account
- Click "Register" in the navigation
- Enter your name, email, and password
- Login with your credentials

### 2. Create or Join a Group
- Navigate to "Groups"
- Click "Create Group"
- Or wait for an admin to add you to an existing group

### 3. Make Contributions
- Go to "Contributions"
- Click "Make Contribution"
- Select a group, enter amount and duration
- Your score updates automatically!

### 4. Request a Loan
- Navigate to "Loans"
- Click "Request Loan"
- Enter loan details (amount must be ≤ 10× your score)
- Wait for approval from admin or majority vote

### 5. Approve Loans (Admin)
- Admins see a special "Approve" button on pending loans
- One admin approval is sufficient

### 6. Vote on Loans (Members)
- Members can vote Yes/No on pending loans
- Loan auto-approves when >50% vote yes
- Loan auto-rejects when >50% vote no

### 7. Repay Loans
- View your approved loans in "Loans"
- Click "Repay" to pay back principal + interest
- Funds return to group balance

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Scoring weights (must sum to 1.0)
SCORING_WEIGHTS = {
    'amount': 0.6,      # Weight for contribution amount
    'duration': 0.4     # Weight for duration
}

# Loan settings
MINIMUM_SCORE_FOR_LOAN = 100        # Min score to request loans
LOAN_APPROVAL_MAJORITY = 0.5        # 50% majority for approval

# Session timeout
SESSION_TIMEOUT_HOURS = 24
```

## 📊 Data Storage

### JSON File Structure

**Users** (`data/users.json`):
```json
{
  "user_id": {
    "id": "user_id",
    "name": "John Doe",
    "email": "john@example.com",
    "password_hash": "hashed_password",
    "groups": ["group_id"],
    "score": 150.5,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**Groups** (`data/groups.json`):
```json
{
  "group_id": {
    "id": "group_id",
    "name": "Savings Circle",
    "admins": ["user_id"],
    "members": ["user_id"],
    "balance": 5000.00,
    "interest_rate": 0.05,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

## 🔐 Security Notes

### Current Implementation (Development)
- Simple session tokens stored in localStorage
- Password hashing with SHA-256 + salt
- Basic authentication on API endpoints

### Production Recommendations
1. **Replace session management** with JWT or OAuth
2. **Use bcrypt** for password hashing instead of SHA-256
3. **Enable HTTPS** for encrypted communication
4. **Add rate limiting** to prevent abuse
5. **Implement CSRF protection**
6. **Add input sanitization** for XSS prevention

## 🗄️ Database Migration

The `DataManager` class abstracts all storage operations, making it easy to migrate from JSON to a database:

**Current (JSON):**
```python
users = DataManager(config.USERS_FILE, 'users')
user = users.get(user_id)
```

**Future (PostgreSQL):**
```python
user = db.session.query(User).filter_by(id=user_id).first()
```

To migrate:
1. Create database models (SQLAlchemy)
2. Replace `DataManager` calls with ORM queries
3. Run migrations to populate database
4. Update `config.py` with database connection string

## 🎯 Business Logic

### Scoring Formula
- **Purpose:** Reward both contribution amount and commitment
- **Calculation:** `(Total $ × 0.6) + (Avg Days × 0.4)`
- **Example:** User contributes $1000 for 30 days and $500 for 60 days
  - Total amount: $1500
  - Avg duration: (30 + 60) / 2 = 45 days
  - Score: (1500 × 0.6) + (45 × 0.4) = 900 + 18 = 918

### Loan Eligibility
- Minimum score: 100 (configurable)
- Maximum loan: Score × 10
- Example: Score of 918 → Max loan $9,180

### Interest Calculation
- **Interest is charged on the LOAN AMOUNT, not on deposits**
- Interest = Loan Amount × Interest Rate
- Example: $5,000 loan at 5% = $250 interest
- Total repayment = Principal + Interest = $5,250

### Loan Approval
Two independent paths (either triggers approval):
1. **Admin Path:** Any admin clicks "Approve"
2. **Member Path:** >50% of members vote "Yes"

## 🧪 Testing the Application

### Test Scenario 1: Basic Flow
1. Register 3 users (Alice, Bob, Charlie)
2. Alice creates "Savings Group"
3. Alice adds Bob and Charlie
4. All three make contributions
5. Bob requests a loan
6. Alice approves (admin) OR Charlie votes yes (majority)

### Test Scenario 2: Scoring
1. User contributes $1000 for 30 days
2. Check score increases
3. User contributes $2000 for 60 days
4. Verify score calculation: `(3000 × 0.6) + (45 × 0.4) = 1818`

### Test Scenario 3: Loan Rejection
1. Request loan that exceeds score × 10
2. Verify rejection with error message
3. Request loan that exceeds group balance
4. Verify rejection

## 📝 API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user

### Groups
- `POST /api/groups` - Create group
- `GET /api/groups/<id>` - Get group details
- `GET /api/groups/user/<id>` - Get user's groups
- `POST /api/groups/<id>/members` - Add member (admin)
- `POST /api/groups/<id>/admins` - Promote admin (admin)
- `PUT /api/groups/<id>/interest` - Update rate (admin)

### Contributions
- `POST /api/contributions` - Record contribution
- `GET /api/contributions/user/<id>` - Get user contributions
- `GET /api/contributions/group/<id>` - Get group contributions

### Loans
- `POST /api/loans` - Request loan
- `GET /api/loans/<id>` - Get loan details
- `POST /api/loans/<id>/approve` - Admin approval
- `POST /api/loans/<id>/vote` - Member vote
- `POST /api/loans/<id>/repay` - Repay loan
- `GET /api/loans/user/<id>` - Get user loans
- `GET /api/loans/group/<id>` - Get group loans

## 🛠️ Troubleshooting

**Port already in use:**
```bash
# Change port in config.py
PORT = 5001
```

**CORS errors:**
- Ensure `flask-cors` is installed
- Check browser console for specific errors

**Data not persisting:**
- Verify `data/` directory exists
- Check file permissions
- Review server logs for errors

## 📄 License

This is a demonstration project for educational purposes.

## 👨‍💻 Development

Built with:
- **Backend:** Python 3, Flask
- **Frontend:** Vanilla JavaScript, CSS3, HTML5
- **Storage:** JSON files (easily replaceable with PostgreSQL, MongoDB, etc.)

**Design Principles:**
- ✅ Separation of concerns
- ✅ Modular architecture
- ✅ Clean code with comments
- ✅ Production-ready patterns
- ✅ Easy database migration path

---

**Happy Saving! 💰**
