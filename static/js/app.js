
const API_BASE = 'http://localhost:5000/api';

// API Client
class APIClient {
    constructor() {
        this.token = localStorage.getItem('auth_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders()
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Error:', error);
            return { success: false, message: 'Network error' };
        }
    }

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, body) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }

    async put(endpoint, body) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body)
        });
    }
}

// Global API client instance
const api = new APIClient();

// App State
const appState = {
    currentUser: null,
    currentPage: 'login'
};

// Initialize app
async function initApp() {
    // Check if user is logged in
    if (api.token) {
        const result = await api.get('/auth/me');
        if (result.success) {
            appState.currentUser = result.user;
            navigateTo('dashboard');
        } else {
            api.clearToken();
            navigateTo('login');
        }
    } else {
        navigateTo('login');
    }
}

// Navigation
function navigateTo(page) {
    appState.currentPage = page;
    updateNavbar();

    const app = document.getElementById('app');

    switch (page) {
        case 'login':
            app.innerHTML = renderLoginPage();
            break;
        case 'register':
            app.innerHTML = renderRegisterPage();
            break;
        case 'dashboard':
            renderDashboard();
            break;
        case 'groups':
            renderGroupsPage();
            break;
        case 'contributions':
            renderContributionsPage();
            break;
        case 'loans':
            renderLoansPage();
            break;
        default:
            app.innerHTML = '<h1>Page not found</h1>';
    }
}

// Update navbar based on auth state
function updateNavbar() {
    const navLinks = document.getElementById('nav-links');
    const navUser = document.getElementById('nav-user');

    if (appState.currentUser) {
        // Logged in
        navLinks.innerHTML = `
            <li><a onclick="navigateTo('dashboard')">Dashboard</a></li>
            <li><a onclick="navigateTo('groups')">Groups</a></li>
            <li><a onclick="navigateTo('contributions')">Contributions</a></li>
            <li><a onclick="navigateTo('loans')">Loans</a></li>
        `;

        navUser.innerHTML = `
            <div class="score-indicator">Score: ${appState.currentUser.score}</div>
            <span>${appState.currentUser.name}</span>
            <button class="btn btn-sm btn-outline" onclick="logout()">Logout</button>
        `;
    } else {
        // Logged out
        navLinks.innerHTML = `
            <li><a onclick="navigateTo('login')">Login</a></li>
            <li><a onclick="navigateTo('register')">Register</a></li>
        `;

        navUser.innerHTML = '';
    }
}

// Logout
async function logout() {
    await api.post('/auth/logout', {});
    api.clearToken();
    appState.currentUser = null;
    navigateTo('login');
}

// Show alert
function showAlert(message, type = 'info') {
    const alertClass = `alert-${type}`;
    const alertHTML = `
        <div class="alert ${alertClass}">
            ${message}
        </div>
    `;

    const alertContainer = document.createElement('div');
    alertContainer.innerHTML = alertHTML;

    const app = document.getElementById('app');
    app.insertBefore(alertContainer.firstElementChild, app.firstChild);

    // Auto remove after 5 seconds
    setTimeout(() => {
        alertContainer.firstElementChild?.remove();
    }, 5000);
}

// Show loading spinner
function showLoading() {
    return `
        <div style="display: flex; justify-content: center; padding: 2rem;">
            <div class="spinner"></div>
        </div>
    `;
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Detect user's currency based on browser locale
function getUserCurrency() {
    const locale = navigator.language || 'en-IN';

    // Map common locales to currency symbols
    const currencyMap = {
        'en-IN': '₹',  // India
        'hi-IN': '₹',  // India (Hindi)
        'en-US': '$',  // United States
        'en-GB': '£',  // United Kingdom
        'en-EU': '€',  // Europe
        'de-DE': '€',  // Germany
        'fr-FR': '€',  // France
        'ja-JP': '¥',  // Japan
        'zh-CN': '¥',  // China
    };

    // Check if locale matches
    if (currencyMap[locale]) {
        return currencyMap[locale];
    }

    // Check country code (last 2 characters)
    const parts = locale.split('-');
    if (parts.length > 1) {
        const country = parts[1];
        if (country === 'IN') return '₹';
        if (country === 'US') return '$';
        if (country === 'GB') return '£';
        if (country === 'EU' || country === 'DE' || country === 'FR') return '€';
        if (country === 'JP' || country === 'CN') return '¥';
    }

    // Default to rupee (₹) since user is in India
    return '₹';
}

// Format currency with dynamic symbol
function formatCurrency(amount) {
    const symbol = '₹'//getUserCurrency();
    return `${symbol}${amount.toFixed(2)}`;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initApp);
