
async function renderContributionsPage() {
    const app = document.getElementById('app');
    app.innerHTML = showLoading();

    const user = appState.currentUser;

    // Fetch user groups for contribution form
    const groupsResult = await api.get(`/groups/user/${user.id}`);
    const groups = groupsResult.success ? groupsResult.groups : [];

    // Fetch user contributions
    const contributionsResult = await api.get(`/contributions/user/${user.id}`);
    const contributions = contributionsResult.success ? contributionsResult.contributions : [];

    const totalAmount = contributions.reduce((sum, c) => sum + c.amount, 0);

    // Calculate average days active from timestamps
    const avgDuration = contributions.length > 0
        ? contributions.reduce((sum, c) => sum + calculateDaysActive(c.timestamp), 0) / contributions.length
        : 0;

    app.innerHTML = `
        <div class="page-header">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="page-title">Contributions</h1>
                    <p style="color: var(--text-secondary);">Track and manage your deposits</p>
                </div>
                ${groups.length > 0 ? `
                    <button class="btn btn-primary" onclick="showContributeModal()">
                        + Make Contribution
                    </button>
                ` : ''}
            </div>
        </div>
        
        <!-- Stats -->
        <div class="grid grid-3 mb-3">
            <div class="stat-card">
                <div class="stat-value">${formatCurrency(totalAmount)}</div>
                <div class="stat-label">Total Contributed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${contributions.length}</div>
                <div class="stat-label">Total Contributions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${avgDuration.toFixed(0)} days</div>
                <div class="stat-label">Avg Days Active</div>
            </div>
        </div>
        
        ${groups.length === 0 ? `
            <div class="glass-card text-center">
                <div class="empty-state">
                    <div class="empty-state-icon">👥</div>
                    <h3>Join a Group First</h3>
                    <p style="color: var(--text-muted);">You need to join a group before making contributions</p>
                    <button class="btn btn-primary mt-2" onclick="navigateTo('groups')">View Groups</button>
                </div>
            </div>
        ` : contributions.length === 0 ? `
            <div class="glass-card text-center">
                <div class="empty-state">
                    <div class="empty-state-icon">💰</div>
                    <h3>No Contributions Yet</h3>
                    <p style="color: var(--text-muted);">Start contributing to increase your score</p>
                    <button class="btn btn-primary mt-2" onclick="showContributeModal()">Make First Contribution</button>
                </div>
            </div>
        ` : `
            <!-- Contributions List -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Contribution History</h3>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Group</th>
                                <th>Amount</th>
                                <th>Days Active</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${contributions.map(contrib => {
        const group = groups.find(g => g.id === contrib.group_id);
        return `
                                    <tr>
                                        <td>${formatDate(contrib.timestamp)}</td>
                                        <td>${group ? group.name : 'Unknown'}</td>
                                        <td style="font-weight: 600; color: var(--success);">${formatCurrency(contrib.amount)}</td>
                                        <td>${calculateDaysActive(contrib.timestamp)} days</td>
                                    </tr>
                                `;
    }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
    `}
    `;
}

function showContributeModal() {
    const user = appState.currentUser;

    // Get user groups
    api.get(`/groups/user/${user.id}`).then(result => {
        if (!result.success || result.groups.length === 0) {
            showAlert('You need to join a group first', 'error');
            return;
        }

        const groups = result.groups;

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <h2>Make Contribution</h2>
                <form onsubmit="handleContribute(event)">
                    <div class="form-group">
                        <label class="form-label">Select Group</label>
                        <select class="form-input" name="group_id" required>
                            ${groups.map(group => `
                                <option value="${group.id}">${group.name} (Balance: ${formatCurrency(group.balance)})</option>
                            `).join('')}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Amount</label>
                        <input type="number" step="0.01" class="form-input" name="amount" placeholder="100.00" min="0.01" required>
                    </div>
                    
                    <div class="flex gap-2">
                        <button type="submit" class="btn btn-primary">Contribute</button>
                        <button type="button" class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);
    });
}

async function handleContribute(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const result = await api.post('/contributions', {
        group_id: formData.get('group_id'),
        amount: parseFloat(formData.get('amount'))
    });

    if (result.success) {
        showAlert('Contribution recorded successfully!', 'success');
        document.querySelector('.modal-overlay').remove();

        // Refresh user data to update score
        const userResult = await api.get('/auth/me');
        if (userResult.success) {
            appState.currentUser = userResult.user;
            updateNavbar();
        }

        renderContributionsPage();
    } else {
        showAlert(result.message, 'error');
    }
}

function calculateDaysActive(timestamp) {
    const depositDate = new Date(timestamp);
    const now = new Date();
    const diffTime = Math.abs(now - depositDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}
