/**
 * Authentication Pages
 * Login and Registration UI
 */

function renderLoginPage() {
    return `
        <div class="page-header text-center">
            <h1 class="page-title">Welcome Back</h1>
            <p style="color: var(--text-secondary);">Login to access your savings and loan groups</p>
        </div>
        
        <div style="max-width: 500px; margin: 0 auto;">
            <div class="glass-card">
                <form onsubmit="handleLogin(event)">
                    <div class="form-group">
                        <label class="form-label">Email Address</label>
                        <input type="email" class="form-input" name="email" placeholder="your@email.com" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-input" name="password" placeholder="Enter your password" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary" style="width: 100%;">
                        Login
                    </button>
                </form>
                
                <div style="text-align: center; margin-top: 1.5rem; color: var(--text-secondary);">
                    Don't have an account? 
                    <a onclick="navigateTo('register')" style="color: var(--primary-light); cursor: pointer; text-decoration: underline;">
                        Register here
                    </a>
                </div>
            </div>
        </div>
    `;
}

function renderRegisterPage() {
    return `
        <div class="page-header text-center">
            <h1 class="page-title">Create Account</h1>
            <p style="color: var(--text-secondary);">Join a community of savers and borrowers</p>
        </div>
        
        <div style="max-width: 500px; margin: 0 auto;">
            <div class="glass-card">
                <form onsubmit="handleRegister(event)">
                    <div class="form-group">
                        <label class="form-label">Full Name</label>
                        <input type="text" class="form-input" name="name" placeholder="John Doe" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Email Address</label>
                        <input type="email" class="form-input" name="email" placeholder="your@email.com" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-input" name="password" placeholder="Create a secure password" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary" style="width: 100%;">
                        Create Account
                    </button>
                </form>
                
                <div style="text-align: center; margin-top: 1.5rem; color: var(--text-secondary);">
                    Already have an account? 
                    <a onclick="navigateTo('login')" style="color: var(--primary-light); cursor: pointer; text-decoration: underline;">
                        Login here
                    </a>
                </div>
            </div>
        </div>
    `;
}

async function handleLogin(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const result = await api.post('/auth/login', {
        email: formData.get('email'),
        password: formData.get('password')
    });

    if (result.success) {
        api.setToken(result.token);
        appState.currentUser = result.user;
        showAlert('Login successful!', 'success');
        navigateTo('dashboard');
    } else {
        showAlert(result.message, 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const result = await api.post('/auth/register', {
        name: formData.get('name'),
        email: formData.get('email'),
        password: formData.get('password')
    });

    if (result.success) {
        showAlert('Registration successful! Please login.', 'success');
        navigateTo('login');
    } else {
        showAlert(result.message, 'error');
    }
}
