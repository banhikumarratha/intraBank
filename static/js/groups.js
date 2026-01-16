/**
 * Groups Page
 * Group management, creation, and member administration
 */

async function renderGroupsPage() {
    const app = document.getElementById('app');
    app.innerHTML = showLoading();

    const user = appState.currentUser;
    const groupsResult = await api.get(`/groups/user/${user.id}`);
    const groups = groupsResult.success ? groupsResult.groups : [];

    app.innerHTML = `
        <div class="page-header">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="page-title">My Groups</h1>
                    <p style="color: var(--text-secondary);">Manage your savings groups</p>
                </div>
                <button class="btn btn-primary" onclick="showCreateGroupModal()">
                    + Create Group
                </button>
            </div>
        </div>
        
        ${groups.length === 0 ? `
            <div class="glass-card text-center">
                <div class="empty-state">
                    <div class="empty-state-icon">👥</div>
                    <h3>No Groups Yet</h3>
                    <p style="color: var(--text-muted);">Create your first group to start saving together</p>
                    <button class="btn btn-primary mt-2" onclick="showCreateGroupModal()">Create Group</button>
                </div>
            </div>
        ` : `
            <div class="grid grid-2">
                ${groups.map(group => `
                    <div class="card" onclick="showGroupDetails('${group.id}')" style="cursor: pointer;">
                        <div class="card-header">
                            <h3 class="card-title">${group.name}</h3>
                            ${group.admins.includes(user.id) ? '<span class="badge badge-info">Admin</span>' : ''}
                        </div>
                        <div class="card-body">
                            <div class="grid grid-2" style="gap: 1rem;">
                                <div>
                                    <div style="font-weight: 600; color: var(--text-secondary); font-size: 0.875rem;">Balance</div>
                                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--success);">
                                        ${formatCurrency(group.balance)}
                                    </div>
                                </div>
                                <div>
                                    <div style="font-weight: 600; color: var(--text-secondary); font-size: 0.875rem;">Interest Rate</div>
                                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--warning);">
                                        ${(group.interest_rate * 100).toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                            <div class="mt-2">
                                <div style="font-size: 0.875rem; color: var(--text-muted);">
                                    👥 ${group.members.length} members
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `}
    `;
}

function showCreateGroupModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <h2>Create New Group</h2>
            <form onsubmit="handleCreateGroup(event)">
                <div class="form-group">
                    <label class="form-label">Group Name</label>
                    <input type="text" class="form-input" name="name" placeholder="My Savings Group" required>
                </div>
                
                <div class="flex gap-2">
                    <button type="submit" class="btn btn-primary">Create</button>
                    <button type="button" class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);
}

async function handleCreateGroup(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const result = await api.post('/groups', {
        name: formData.get('name')
    });

    if (result.success) {
        showAlert('Group created successfully!', 'success');
        document.querySelector('.modal-overlay').remove();
        renderGroupsPage();
    } else {
        showAlert(result.message, 'error');
    }
}

async function showGroupDetails(groupId) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `<div class="modal">${showLoading()}</div>`;
    document.body.appendChild(modal);

    const result = await api.get(`/groups/${groupId}`);

    if (!result.success) {
        showAlert('Failed to load group details', 'error');
        modal.remove();
        return;
    }

    const group = result.group;
    const user = appState.currentUser;
    const isAdmin = group.admins.includes(user.id);

    modal.innerHTML = `
        <div class="modal">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h2>${group.name}</h2>
                <button class="btn btn-sm btn-outline" onclick="this.closest('.modal-overlay').remove()">Close</button>
            </div>
            
            <div class="grid grid-2" style="gap: 1rem; margin-bottom: 1.5rem;">
                <div class="stat-card">
                    <div class="stat-value">${formatCurrency(group.balance)}</div>
                    <div class="stat-label">Group Balance</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(group.interest_rate * 100).toFixed(1)}%</div>
                    <div class="stat-label">Interest Rate</div>
                </div>
            </div>
            
            ${isAdmin ? `
                <div style="margin-bottom: 1.5rem;">
                    <h4>Admin Controls</h4>
                    <div class="flex gap-2 mt-2">
                        <button class="btn btn-sm btn-primary" onclick="showAddMemberModal('${groupId}')">Add Member</button>
                        <button class="btn btn-sm btn-secondary" onclick="showUpdateInterestModal('${groupId}', ${group.interest_rate})">Update Interest</button>
                    </div>
                </div>
            ` : ''}
            
            <div>
                <h4>Members (${group.members_data.length})</h4>
                <div style="margin-top: 1rem;">
                    ${group.members_data.map(member => `
                        <div style="padding: 0.75rem; margin-bottom: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: 600;">${member.name}</div>
                                <div style="font-size: 0.875rem; color: var(--text-muted);">
                                    Score: ${member.score.toFixed(2)} • ${member.email}
                                </div>
                            </div>
                            <div>
                                ${member.is_admin ? '<span class="badge badge-info">Admin</span>' : ''}
                                ${isAdmin && !member.is_admin ? `
                                    <button class="btn btn-sm btn-outline" onclick="promoteToAdmin('${groupId}', '${member.id}')">
                                        Promote
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function showAddMemberModal(groupId) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <h3>Add Member</h3>
            <form onsubmit="handleAddMember(event, '${groupId}')">
                <div class="form-group">
                    <label class="form-label">User ID</label>
                    <input type="text" class="form-input" name="user_id" placeholder="user_email_at_domain_com" required>
                    <small style="color: var(--text-muted);">Enter the user's ID (email-based)</small>
                </div>
                
                <div class="flex gap-2">
                    <button type="submit" class="btn btn-primary">Add</button>
                    <button type="button" class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);
}

async function handleAddMember(event, groupId) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const result = await api.post(`/groups/${groupId}/members`, {
        user_id: formData.get('user_id')
    });

    if (result.success) {
        showAlert(result.message, 'success');
        document.querySelectorAll('.modal-overlay').forEach(m => m.remove());
        showGroupDetails(groupId);
    } else {
        showAlert(result.message, 'error');
    }
}

function showUpdateInterestModal(groupId, currentRate) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <h3>Update Interest Rate</h3>
            <form onsubmit="handleUpdateInterest(event, '${groupId}')">
                <div class="form-group">
                    <label class="form-label">Interest Rate (decimal)</label>
                    <input type="number" step="0.01" class="form-input" name="rate" value="${currentRate}" min="0" max="1" required>
                    <small style="color: var(--text-muted);">Enter as decimal (e.g., 0.05 for 5%)</small>
                </div>
                
                <div class="flex gap-2">
                    <button type="submit" class="btn btn-primary">Update</button>
                    <button type="button" class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);
}

async function handleUpdateInterest(event, groupId) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const result = await api.put(`/groups/${groupId}/interest`, {
        rate: parseFloat(formData.get('rate'))
    });

    if (result.success) {
        showAlert(result.message, 'success');
        document.querySelectorAll('.modal-overlay').forEach(m => m.remove());
        showGroupDetails(groupId);
    } else {
        showAlert(result.message, 'error');
    }
}

async function promoteToAdmin(groupId, userId) {
    const result = await api.post(`/groups/${groupId}/admins`, {
        user_id: userId
    });

    if (result.success) {
        showAlert(result.message, 'success');
        document.querySelectorAll('.modal-overlay').forEach(m => m.remove());
        showGroupDetails(groupId);
    } else {
        showAlert(result.message, 'error');
    }
}
