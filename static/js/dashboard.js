/**
 * Dashboard Page
 * User overview with score, groups, contributions, and loans
 */

async function renderDashboard() {
    const app = document.getElementById('app');
    app.innerHTML = showLoading();

    // Fetch user data
    const userResult = await api.get(`/auth/me`);
    if (!userResult.success) {
        showAlert('Failed to load user data', 'error');
        return;
    }

    const user = userResult.user;
    appState.currentUser = user; // Update state
    updateNavbar(); // Update score in navbar

    // Fetch groups
    const groupsResult = await api.get(`/groups/user/${user.id}`);
    const groups = groupsResult.success ? groupsResult.groups : [];

    // Fetch contributions
    const contributionsResult = await api.get(`/contributions/user/${user.id}`);
    const contributions = contributionsResult.success ? contributionsResult.contributions.slice(0, 5) : [];

    // Fetch loans
    const loansResult = await api.get(`/loans/user/${user.id}`);
    const loans = loansResult.success ? loansResult.loans.slice(0, 5) : [];

    // Calculate stats
    const totalContributions = contributions.reduce((sum, c) => sum + c.amount, 0);
    const activeLoans = loans.filter(l => l.status === 'approved').length;
    const pendingLoans = loans.filter(l => l.status === 'pending').length;

    app.innerHTML = `
        <div class="page-header">
            <h1 class="page-title">Welcome, ${user.name}! 👋</h1>
            <p style="color: var(--text-secondary);">Here's your savings and loan overview</p>
        </div>
        
        <!-- Stats Grid -->
        <div class="grid grid-3 mb-3">
            <div class="stat-card">
                <div class="stat-value">${user.score.toFixed(2)}</div>
                <div class="stat-label">Your Score</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">${groups.length}</div>
                <div class="stat-label">Groups Joined</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">${formatCurrency(totalContributions)}</div>
                <div class="stat-label">Total Contributions</div>
            </div>
        </div>
        
        <!-- Main Content Grid -->
        <div class="grid grid-2">
            <!-- Groups Section -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Your Groups</h3>
                    <button class="btn btn-sm btn-primary" onclick="navigateTo('groups')">View All</button>
                </div>
                <div class="card-body">
                    ${groups.length === 0 ? `
                        <div class="empty-state">
                            <div class="empty-state-icon">👥</div>
                            <p>You haven't joined any groups yet</p>
                            <button class="btn btn-primary mt-2" onclick="navigateTo('groups')">Explore Groups</button>
                        </div>
                    ` : `
                        ${groups.map(group => `
                            <div style="padding: 1rem; margin-bottom: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 0.5rem;">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <div style="font-weight: 600;">${group.name}</div>
                                        <div style="font-size: 0.875rem; color: var(--text-muted);">
                                            Balance: ${formatCurrency(group.balance)} • ${group.members.length} members
                                        </div>
                                    </div>
                                    ${group.admins.includes(user.id) ? '<span class="badge badge-info">Admin</span>' : ''}
                                </div>
                            </div>
                        `).join('')}
                    `}
                </div>
            </div>
            
            <!-- Recent Contributions -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Recent Contributions</h3>
                    <button class="btn btn-sm btn-primary" onclick="navigateTo('contributions')">View All</button>
                </div>
                <div class="card-body">
                    ${contributions.length === 0 ? `
                        <div class="empty-state">
                            <div class="empty-state-icon">💰</div>
                            <p>No contributions yet</p>
                            <button class="btn btn-primary mt-2" onclick="navigateTo('contributions')">Make Contribution</button>
                        </div>
                    ` : `
                        ${contributions.map(contrib => `
                            <div style="padding: 1rem; margin-bottom: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 0.5rem;">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <div style="font-weight: 600;">${formatCurrency(contrib.amount)}</div>
                                        <div style="font-size: 0.875rem; color: var(--text-muted);">
                                            ${contrib.duration_days} days • ${formatDate(contrib.timestamp)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    `}
                </div>
            </div>
        </div>
        
        <!-- Loans Section -->
        <div class="card mt-3">
            <div class="card-header">
                <h3 class="card-title">Your Loans</h3>
                <button class="btn btn-sm btn-primary" onclick="navigateTo('loans')">View All</button>
            </div>
            <div class="card-body">
                ${loans.length === 0 ? `
                    <div class="empty-state">
                        <div class="empty-state-icon">📋</div>
                        <p>No loans yet</p>
                        <button class="btn btn-primary mt-2" onclick="navigateTo('loans')">Request Loan</button>
                    </div>
                ` : `
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Amount</th>
                                <th>Duration</th>
                                <th>Interest</th>
                                <th>Status</th>
                                <th>Requested</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${loans.map(loan => `
                                <tr>
                                    <td>${formatCurrency(loan.amount)}</td>
                                    <td>${loan.duration_days} days</td>
                                    <td>${(loan.interest_rate * 100).toFixed(1)}%</td>
                                    <td>
                                        <span class="badge badge-${loan.status === 'approved' ? 'success' : loan.status === 'pending' ? 'warning' : loan.status === 'repaid' ? 'info' : 'error'}">
                                            ${loan.status}
                                        </span>
                                    </td>
                                    <td>${formatDate(loan.requested_at)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `}
            </div>
        </div>
    `;
}
