/**
 * Loans Page
 * Request loans, vote on loans, and manage repayments
 */

async function renderLoansPage() {
    const app = document.getElementById('app');
    app.innerHTML = showLoading();

    const user = appState.currentUser;

    // Fetch user groups
    const groupsResult = await api.get(`/groups/user/${user.id}`);
    const groups = groupsResult.success ? groupsResult.groups : [];

    // Fetch user loans
    const loansResult = await api.get(`/loans/user/${user.id}`);
    const myLoans = loansResult.success ? loansResult.loans : [];

    // Fetch pending loans in user's groups (for voting)
    let pendingGroupLoans = [];
    for (const group of groups) {
        const groupLoansResult = await api.get(`/loans/group/${group.id}`);
        if (groupLoansResult.success) {
            const pending = groupLoansResult.loans.filter(
                loan => loan.status === 'pending' && loan.user_id !== user.id
            );
            pendingGroupLoans.push(...pending);
        }
    }

    const activeLoans = myLoans.filter(l => l.status === 'approved');
    const pendingLoans = myLoans.filter(l => l.status === 'pending');

    app.innerHTML = `
        <div class="page-header">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="page-title">Loans</h1>
                    <p style="color: var(--text-secondary);">Request and manage loans</p>
                </div>
                ${groups.length > 0 ? `
                    <button class="btn btn-primary" onclick="showRequestLoanModal()">
                        + Request Loan
                    </button>
                ` : ''}
            </div>
        </div>
        
        <!-- Stats -->
        <div class="grid grid-3 mb-3">
            <div class="stat-card">
                <div class="stat-value">${activeLoans.length}</div>
                <div class="stat-label">Active Loans</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${pendingLoans.length}</div>
                <div class="stat-label">Pending Requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${pendingGroupLoans.length}</div>
                <div class="stat-label">Loans to Review</div>
            </div>
        </div>
        
        ${groups.length === 0 ? `
            <div class="glass-card text-center">
                <div class="empty-state">
                    <div class="empty-state-icon">👥</div>
                    <h3>Join a Group First</h3>
                    <p style="color: var(--text-muted);">You need to join a group before requesting loans</p>
                    <button class="btn btn-primary mt-2" onclick="navigateTo('groups')">View Groups</button>
                </div>
            </div>
        ` : ''}
        
        <!-- Pending Group Loans (for voting) -->
        ${pendingGroupLoans.length > 0 ? `
            <div class="card mb-3">
                <div class="card-header">
                    <h3 class="card-title">Loans Pending Your Vote</h3>
                </div>
                <div class="card-body">
                    ${pendingGroupLoans.map(loan => {
        const group = groups.find(g => g.id === loan.group_id);
        const userVoted = loan.member_votes && loan.member_votes[user.id] !== undefined;
        const approveVotes = loan.member_votes ? Object.values(loan.member_votes).filter(v => v).length : 0;
        const totalVotes = loan.member_votes ? Object.keys(loan.member_votes).length : 0;

        return `
                            <div style="padding: 1rem; margin-bottom: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 0.5rem;">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <div style="font-weight: 600;">${loan.user_name} requests ${formatCurrency(loan.amount)}</div>
                                        <div style="font-size: 0.875rem; color: var(--text-muted);">
                                            Group: ${group ? group.name : 'Unknown'} • 
                                            Duration: ${loan.duration_days} days • 
                                            Interest: ${(loan.interest_rate * 100).toFixed(1)}%
                                        </div>
                                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                            Votes: ${approveVotes} approve / ${totalVotes} total
                                        </div>
                                    </div>
                                    ${!userVoted ? `
                                        <div class="flex gap-2">
                                            <button class="btn btn-sm btn-success" onclick="voteLoan('${loan.id}', true)">
                                                ✓ Approve
                                            </button>
                                            <button class="btn btn-sm btn-danger" onclick="voteLoan('${loan.id}', false)">
                                                ✗ Reject
                                            </button>
                                        </div>
                                    ` : `
                                        <span class="badge badge-info">
                                            You voted ${loan.member_votes[user.id] ? 'Yes' : 'No'}
                                        </span>
                                    `}
                                </div>
                            </div>
                        `;
    }).join('')}
                </div>
            </div>
        ` : ''}
        
        <!-- My Loans -->
        ${myLoans.length > 0 ? `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">My Loan Requests</h3>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Group</th>
                                <th>Amount</th>
                                <th>Duration</th>
                                <th>Interest</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${myLoans.map(loan => {
        const group = groups.find(g => g.id === loan.group_id);
        const canRepay = loan.status === 'approved';
        const totalRepay = loan.amount + (loan.amount * loan.interest_rate);

        return `
                                    <tr>
                                        <td>${formatDate(loan.requested_at)}</td>
                                        <td>${group ? group.name : 'Unknown'}</td>
                                        <td style="font-weight: 600;">${formatCurrency(loan.amount)}</td>
                                        <td>${loan.duration_days} days</td>
                                        <td>${(loan.interest_rate * 100).toFixed(1)}%</td>
                                        <td>
                                            <span class="badge badge-${loan.status === 'approved' ? 'success' :
                loan.status === 'pending' ? 'warning' :
                    loan.status === 'repaid' ? 'info' : 'error'
            }">
                                                ${loan.status}
                                            </span>
                                        </td>
                                        <td>
                                            ${canRepay ? `
                                                <button class="btn btn-sm btn-primary" onclick="repayLoan('${loan.id}', ${totalRepay})">
                                                    Repay ${formatCurrency(totalRepay)}
                                                </button>
                                            ` : loan.status === 'pending' ? `
                                                <span style="font-size: 0.75rem; color: var(--text-muted);">
                                                    Awaiting approval
                                                </span>
                                            ` : ''}
                                        </td>
                                    </tr>
                                `;
    }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        ` : groups.length > 0 ? `
            <div class="glass-card text-center">
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <h3>No Loans Yet</h3>
                    <p style="color: var(--text-muted);">Request your first loan to get started</p>
                    <button class="btn btn-primary mt-2" onclick="showRequestLoanModal()">Request Loan</button>
                </div>
            </div>
        ` : ''}
    `;
}

function showRequestLoanModal() {
    const user = appState.currentUser;

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
                <h2>Request Loan</h2>
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                    Your current score: <strong>${user.score.toFixed(2)}</strong><br>
                    Maximum loan amount: <strong>${formatCurrency(user.score * 10)}</strong>
                </p>
                
                <form onsubmit="handleRequestLoan(event)">
                    <div class="form-group">
                        <label class="form-label">Select Group</label>
                        <select class="form-input" name="group_id" required onchange="updateLoanGroupInfo(this)">
                            ${groups.map(group => `
                                <option value="${group.id}" data-balance="${group.balance}" data-rate="${group.interest_rate}">
                                    ${group.name} (Balance: ${formatCurrency(group.balance)})
                                </option>
                            `).join('')}
                        </select>
                        <small id="group-info" style="color: var(--text-muted);"></small>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Loan Amount</label>
                        <input type="number" step="0.01" class="form-input" name="amount" placeholder="1000.00" 
                               min="0.01" max="${user.score * 10}" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Duration (days)</label>
                        <input type="number" class="form-input" name="duration_days" placeholder="30" min="1" required>
                    </div>
                    
                    <div class="flex gap-2">
                        <button type="submit" class="btn btn-primary">Request Loan</button>
                        <button type="button" class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        // Initialize group info
        const select = modal.querySelector('select[name="group_id"]');
        updateLoanGroupInfo(select);
    });
}

function updateLoanGroupInfo(select) {
    const option = select.options[select.selectedIndex];
    const balance = parseFloat(option.dataset.balance);
    const rate = parseFloat(option.dataset.rate);

    const info = document.getElementById('group-info');
    info.textContent = `Interest rate: ${(rate * 100).toFixed(1)}% • Available balance: ${formatCurrency(balance)}`;
}

async function handleRequestLoan(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const result = await api.post('/loans', {
        group_id: formData.get('group_id'),
        amount: parseFloat(formData.get('amount')),
        duration_days: parseInt(formData.get('duration_days'))
    });

    if (result.success) {
        showAlert('Loan request submitted successfully!', 'success');
        document.querySelector('.modal-overlay').remove();
        renderLoansPage();
    } else {
        showAlert(result.message, 'error');
    }
}

async function voteLoan(loanId, approve) {
    const result = await api.post(`/loans/${loanId}/vote`, {
        approve: approve
    });

    if (result.success) {
        showAlert(result.message, 'success');
        renderLoansPage();
    } else {
        showAlert(result.message, 'error');
    }
}

async function repayLoan(loanId, amount) {
    if (!confirm(`Confirm repayment of ${formatCurrency(amount)}?`)) {
        return;
    }

    const result = await api.post(`/loans/${loanId}/repay`, {});

    if (result.success) {
        showAlert(`Loan repaid! Principal: ${formatCurrency(result.principal)}, Interest: ${formatCurrency(result.interest)}`, 'success');
        renderLoansPage();
    } else {
        showAlert(result.message, 'error');
    }
}
