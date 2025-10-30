const API_BASE = '/api';

// Theme functionality
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'default';
    document.body.setAttribute('data-theme', savedTheme);
    const themeSelector = document.getElementById('theme-selector');
    if (themeSelector) {
        themeSelector.value = savedTheme;
    }
}

function changeTheme() {
    const theme = document.getElementById('theme-selector').value;
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

// Load theme on page load
document.addEventListener('DOMContentLoaded', loadTheme);

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    if (tabName === 'dashboard') loadStats();
    if (tabName === 'drafts') loadDrafts();
    if (tabName === 'accounts') loadAccounts();
    if (tabName === 'config') loadConfig();
    if (tabName === 'actions') loadActions();
    if (tabName === 'templates') loadTemplates();
    if (tabName === 'settings') loadSettings();
}

function showPriorityTab(priority) {
    // Remove active class from all sub-tabs and priority content
    document.querySelectorAll('.sub-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.priority-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Add active class to selected priority
    event.target.classList.add('active');
    document.getElementById(`priority-${priority}`).classList.add('active');
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();
        
        document.getElementById('stat-pending').textContent = stats.pending_drafts;
        document.getElementById('stat-approved').textContent = stats.approved_drafts;
        document.getElementById('stat-total').textContent = stats.total_processed;
        
        const categoryDiv = document.getElementById('category-stats');
        if (stats.by_category && stats.by_category.length > 0) {
            categoryDiv.innerHTML = '<div class="category-list">' + 
                stats.by_category.map(cat => 
                    `<div class="category-item">
                        <span>${cat.classification || 'Uncategorized'}</span>
                        <span><strong>${cat.count}</strong></span>
                    </div>`
                ).join('') + '</div>';
        } else {
            categoryDiv.innerHTML = '<p class="help-text">No emails processed yet</p>';
        }
        
        loadEmailSummaries();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadEmailSummaries() {
    try {
        const response = await fetch(`${API_BASE}/email-summaries`);
        const summaries = await response.json();
        
        document.getElementById('high-priority-count').textContent = summaries.high_priority.length;
        document.getElementById('important-count').textContent = summaries.important.length;
        
        const highPriorityDiv = document.getElementById('high-priority-emails');
        if (summaries.high_priority.length > 0) {
            highPriorityDiv.innerHTML = summaries.high_priority.map(email => renderEmailSummaryItem(email)).join('');
        } else {
            highPriorityDiv.innerHTML = '<div class="summary-empty">No high priority emails</div>';
        }
        
        const importantDiv = document.getElementById('important-emails');
        if (summaries.important.length > 0) {
            importantDiv.innerHTML = summaries.important.map(email => renderEmailSummaryItem(email)).join('');
        } else {
            importantDiv.innerHTML = '<div class="summary-empty">No important emails</div>';
        }
    } catch (error) {
        console.error('Error loading email summaries:', error);
    }
}

function renderEmailSummaryItem(email) {
    const slaClass = `sla-${email.sla_status}`;
    const sentimentClass = email.sentiment ? `sentiment-${email.sentiment.toLowerCase()}` : 'sentiment-neutral';
    const slaText = email.sla_status === 'green' ? '< 24h' : email.sla_status === 'amber' ? '24-48h' : '> 48h';
    
    return `
        <div class="summary-email-item">
            <div class="summary-email-header">
                <div class="summary-email-from">${email.sender_name || email.sender_email}</div>
            </div>
            <div class="summary-email-subject">${email.original_subject}</div>
            <div class="summary-email-meta">
                <span class="summary-badge ${slaClass}">SLA: ${slaText}</span>
                ${email.sentiment ? `<span class="summary-badge ${sentimentClass}">${email.sentiment}</span>` : ''}
                ${email.classification ? `<span class="summary-badge" style="background: #e5e7eb; color: #374151;">${email.classification}</span>` : ''}
                ${email.account_name ? `<span class="summary-badge" style="background: #dbeafe; color: #1e40af;">${email.account_name}</span>` : ''}
            </div>
        </div>
    `;
}

function toggleSummary(contentId) {
    const content = document.getElementById(contentId);
    const button = content.previousElementSibling;
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        button.classList.add('expanded');
    } else {
        content.style.display = 'none';
        button.classList.remove('expanded');
    }
}

async function processEmails() {
    const statusEl = document.getElementById('process-status');
    statusEl.textContent = 'Processing...';
    statusEl.style.color = '#667eea';
    
    try {
        const response = await fetch(`${API_BASE}/process-emails`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            statusEl.textContent = `✓ Processed ${result.processed_count} emails`;
            statusEl.style.color = '#10b981';
            loadStats();
        } else {
            statusEl.textContent = `✗ Error: ${result.error}`;
            statusEl.style.color = '#ef4444';
        }
    } catch (error) {
        statusEl.textContent = `✗ Error: ${error.message}`;
        statusEl.style.color = '#ef4444';
    }
}

async function loadDrafts() {
    const container = document.getElementById('drafts-list');
    container.innerHTML = '<div class="loading">Loading drafts...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/drafts?status=pending`);
        const drafts = await response.json();
        
        if (drafts.length === 0) {
            container.innerHTML = '<p class="help-text">No pending drafts. Process emails to generate drafts.</p>';
            return;
        }
        
        container.innerHTML = drafts.map(draft => `
            <div class="draft-card">
                <div class="draft-header">
                    <div>
                        <strong>To: ${draft.recipient_email}</strong>
                        ${draft.account_name ? `<div class="draft-meta"><span class="badge" style="background: #3b82f6;">From: ${draft.account_name}</span></div>` : ''}
                        <div class="draft-meta">
                            <span class="badge badge-${draft.priority.toLowerCase()}">${draft.priority}</span>
                            <span class="badge badge-${draft.sentiment.toLowerCase()}">${draft.sentiment}</span>
                            <span class="badge">${draft.classification}</span>
                            ${formatSLABadge(draft.created_at, 24)}
                        </div>
                    </div>
                    <div class="draft-meta">
                        ${new Date(draft.created_at).toLocaleString()}
                    </div>
                </div>
                
                <div class="draft-content">
                    <strong>Subject:</strong>
                    <input type="text" id="subject-${draft.id}" value="${draft.subject}" 
                           style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px;">
                    
                    <strong style="margin-top: 15px;">Body:</strong>
                    <textarea id="body-${draft.id}" rows="6" 
                              style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; font-family: inherit;">${draft.body}</textarea>
                    
                    <details style="margin-top: 10px;">
                        <summary style="cursor: pointer; color: #667eea;">View Original Email</summary>
                        <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 10px; white-space: pre-wrap;">${draft.original_content}</pre>
                    </details>
                </div>
                
                <div class="draft-actions">
                    <button onclick="updateDraft(${draft.id})" class="btn">Update Draft</button>
                    <button onclick="approveDraft(${draft.id})" class="btn btn-success">Approve & Send</button>
                    <button onclick="rejectDraft(${draft.id})" class="btn btn-danger">Reject</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading drafts</p>';
        console.error(error);
    }
}

async function updateDraft(draftId) {
    const subject = document.getElementById(`subject-${draftId}`).value;
    const body = document.getElementById(`body-${draftId}`).value;
    
    try {
        await fetch(`${API_BASE}/drafts/${draftId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'update', subject, body })
        });
        alert('Draft updated');
    } catch (error) {
        alert('Error updating draft');
    }
}

async function approveDraft(draftId) {
    if (!confirm('Approve and send this email?')) return;
    
    try {
        await fetch(`${API_BASE}/drafts/${draftId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'approve' })
        });
        alert('Draft approved (email sending not implemented yet)');
        loadDrafts();
    } catch (error) {
        alert('Error approving draft');
    }
}

async function rejectDraft(draftId) {
    if (!confirm('Reject this draft?')) return;
    
    try {
        await fetch(`${API_BASE}/drafts/${draftId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'reject' })
        });
        alert('Draft rejected');
        loadDrafts();
    } catch (error) {
        alert('Error rejecting draft');
    }
}

async function loadConfig() {
    // Load priority-based whitelists
    loadPriorityConfigList('whitelist', 'High Priority', 'whitelist-high-items');
    loadPriorityConfigList('whitelist', 'Important', 'whitelist-important-items');
    loadPriorityConfigList('whitelist', 'Low Priority', 'whitelist-low-items');
    
    // Load priority-based subject keywords
    loadPriorityConfigList('subject_keyword', 'High Priority', 'subject-high-items');
    loadPriorityConfigList('subject_keyword', 'Important', 'subject-important-items');
    loadPriorityConfigList('subject_keyword', 'Low Priority', 'subject-low-items');
    
    // Load priority-based body keywords
    loadPriorityConfigList('body_keyword', 'High Priority', 'body-high-items');
    loadPriorityConfigList('body_keyword', 'Important', 'body-important-items');
    loadPriorityConfigList('body_keyword', 'Low Priority', 'body-low-items');
    
    // Load subscriptions whitelist
    loadConfigList('subscriptions_whitelist', 'subscriptions-items');
}

async function loadPriorityConfigList(type, priority, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/config?type=${type}`);
        const configs = await response.json();
        
        // Filter by priority category
        const items = configs[type] ? configs[type].filter(item => item.category === priority) : [];
        
        if (items.length === 0) {
            container.innerHTML = '<p class="help-text">No entries yet</p>';
            return;
        }
        
        container.innerHTML = items.map(item => `
            <div class="config-item">
                <span>${item.value}</span>
                <div class="button-group">
                    <button class="edit-btn" onclick="editConfig('${type}', '${item.key}', '${priority}')">Edit</button>
                    <button class="delete-btn" onclick="deleteConfig('${type}', '${item.key}')">Remove</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading</p>';
    }
}

async function loadConfigList(type, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/config?type=${type}`);
        const configs = await response.json();
        
        if (!configs[type] || configs[type].length === 0) {
            container.innerHTML = '<p class="help-text">No entries yet</p>';
            return;
        }
        
        container.innerHTML = configs[type].map(item => {
            const categoryBadge = item.category ? `<span class="badge" style="margin-left: 10px; background: #ef4444; color: white;">${item.category}</span>` : '';
            return `
                <div class="config-item">
                    <span>${item.value}${categoryBadge}</span>
                    <div class="button-group">
                        <button class="edit-btn" onclick="editConfig('${type}', '${item.key}', null)">Edit</button>
                        <button class="delete-btn" onclick="deleteConfig('${type}', '${item.key}')">Remove</button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading</p>';
    }
}

async function addConfig(type) {
    const input = document.getElementById(`${type}-input`);
    const value = input.value.trim();
    
    if (!value) return;
    
    try {
        await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                config_type: type,
                config_key: value,
                config_value: value
            })
        });
        
        input.value = '';
        loadConfigList(type, `${type}-items`);
    } catch (error) {
        alert('Error adding entry');
    }
}

async function addSubscription() {
    const input = document.getElementById('subscriptions-input');
    const value = input.value.trim();
    
    if (!value) return;
    
    try {
        await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                config_type: 'subscriptions_whitelist',
                config_key: value,
                config_value: value
            })
        });
        
        input.value = '';
        loadConfigList('subscriptions_whitelist', 'subscriptions-items');
    } catch (error) {
        alert('Error adding subscription');
    }
}

async function addPriorityConfig(type, priority) {
    // Map priority to shortened form for input IDs
    const priorityMap = {
        'High Priority': 'high',
        'Important': 'important',
        'Low Priority': 'low'
    };
    
    const priorityShort = priorityMap[priority];
    
    // Determine the input field ID based on type and priority
    let inputId;
    if (type === 'whitelist') {
        inputId = `whitelist-${priorityShort}-input`;
    } else if (type === 'subject_keyword') {
        inputId = `subject-${priorityShort}-input`;
    } else if (type === 'body_keyword') {
        inputId = `body-${priorityShort}-input`;
    }
    
    const input = document.getElementById(inputId);
    if (!input) {
        console.error(`Input field not found: ${inputId}`);
        return;
    }
    
    const value = input.value.trim();
    
    if (!value) return;
    
    try {
        await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                config_type: type,
                config_key: value,
                config_value: value,
                category: priority
            })
        });
        
        input.value = '';
        
        // Determine container ID and reload (use same priorityShort mapping)
        let containerId;
        if (type === 'whitelist') {
            containerId = `whitelist-${priorityShort}-items`;
        } else if (type === 'subject_keyword') {
            containerId = `subject-${priorityShort}-items`;
        } else if (type === 'body_keyword') {
            containerId = `body-${priorityShort}-items`;
        }
        
        loadPriorityConfigList(type, priority, containerId);
    } catch (error) {
        alert('Error adding entry');
    }
}

async function editConfig(type, key, priority) {
    const newValue = prompt('Enter new value:', key);
    if (!newValue || newValue.trim() === '') return;
    
    try {
        await fetch(`${API_BASE}/config/${type}/${encodeURIComponent(key)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                config_key: newValue.trim(),
                config_value: newValue.trim(),
                category: priority
            })
        });
        
        // Reload all config lists
        loadConfig();
    } catch (error) {
        alert('Error updating entry');
    }
}

async function deleteConfig(type, key) {
    try {
        await fetch(`${API_BASE}/config/${type}/${key}`, { method: 'DELETE' });
        // Reload all config lists
        loadConfig();
    } catch (error) {
        alert('Error deleting entry');
    }
}

async function loadTemplates() {
    const container = document.getElementById('templates-list');
    container.innerHTML = '<div class="loading">Loading templates...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/templates`);
        const templates = await response.json();
        
        if (templates.length === 0) {
            container.innerHTML = '<p class="help-text">No templates yet. Create one above.</p>';
            return;
        }
        
        container.innerHTML = templates.map(template => {
            // Color code priority badge
            let priorityColor = '#10b981'; // green for low
            if (template.priority === 'High Priority') priorityColor = '#ef4444';
            else if (template.priority === 'Important') priorityColor = '#f59e0b';
            
            return `
            <div class="template-card">
                <div class="template-header">
                    <div>
                        <strong>${template.name}</strong>
                        <span class="badge" style="background: ${priorityColor};">${template.priority || 'Important'}</span>
                        <span class="badge">${template.category || 'General'}</span>
                    </div>
                    <button class="delete-btn" onclick="deleteTemplate(${template.id})">Delete</button>
                </div>
                ${template.subject_template ? `<div style="margin-top: 10px;"><strong>Subject:</strong> ${template.subject_template}</div>` : ''}
                <div style="margin-top: 10px;"><strong>Body:</strong></div>
                <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 5px; white-space: pre-wrap;">${template.body_template}</pre>
            </div>
        `;
        }).join('');
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading templates</p>';
    }
}

function showTemplateForm() {
    document.getElementById('template-form').style.display = 'block';
}

function hideTemplateForm() {
    document.getElementById('template-form').style.display = 'none';
    document.getElementById('template-name').value = '';
    document.getElementById('template-priority').value = 'Important';
    document.getElementById('template-subject').value = '';
    document.getElementById('template-body').value = '';
}

async function saveTemplate() {
    const name = document.getElementById('template-name').value.trim();
    const priority = document.getElementById('template-priority').value;
    const category = document.getElementById('template-category').value;
    const subject = document.getElementById('template-subject').value.trim();
    const body = document.getElementById('template-body').value.trim();
    
    if (!name || !body) {
        alert('Please fill in template name and body');
        return;
    }
    
    try {
        await fetch(`${API_BASE}/templates`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, priority, category, subject_template: subject, body_template: body })
        });
        
        hideTemplateForm();
        loadTemplates();
        alert('Template saved');
    } catch (error) {
        alert('Error saving template');
    }
}

async function deleteTemplate(id) {
    if (!confirm('Delete this template?')) return;
    
    try {
        await fetch(`${API_BASE}/templates/${id}`, { method: 'DELETE' });
        loadTemplates();
    } catch (error) {
        alert('Error deleting template');
    }
}

async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE}/settings`);
        const settings = await response.json();
        
        document.getElementById('setting-imap').value = settings.imap_server || '';
        document.getElementById('setting-email').value = settings.email_user || '';
        
        const geminiStatus = document.getElementById('gemini-status');
        geminiStatus.innerHTML = '<p class="help-text">✓ Gemini API key is configured in environment variables</p>';
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

async function saveSettings() {
    const imap = document.getElementById('setting-imap').value.trim();
    const email = document.getElementById('setting-email').value.trim();
    const password = document.getElementById('setting-password').value;
    
    if (!imap || !email) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        const settings = { imap_server: imap, email_user: email };
        if (password) settings.email_password = password;
        
        await fetch(`${API_BASE}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        alert('Settings saved successfully');
        document.getElementById('setting-password').value = '';
    } catch (error) {
        alert('Error saving settings');
    }
}

// Email Accounts Management
let currentAccountId = null;

const IMAP_PRESETS = {
    gmail: { server: 'imap.gmail.com', port: 993, domains: ['gmail.com', 'googlemail.com'] },
    outlook: { server: 'outlook.office365.com', port: 993, domains: ['outlook.com', 'hotmail.com', 'live.com'] },
    yahoo: { server: 'imap.mail.yahoo.com', port: 993, domains: ['yahoo.com', 'ymail.com', 'rocketmail.com'] },
    icloud: { server: 'imap.mail.me.com', port: 993, domains: ['icloud.com', 'me.com', 'mac.com'] },
    aol: { server: 'imap.aol.com', port: 993, domains: ['aol.com'] }
};

function applyIMAPPreset() {
    const preset = document.getElementById('imap-preset').value;
    if (preset && IMAP_PRESETS[preset]) {
        document.getElementById('account-imap-server').value = IMAP_PRESETS[preset].server;
        document.getElementById('account-imap-port').value = IMAP_PRESETS[preset].port;
    }
}

async function loadAccounts() {
    const container = document.getElementById('accounts-list');
    container.innerHTML = '<div class="loading">Loading accounts...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/email-accounts`);
        const accounts = await response.json();
        
        if (accounts.length === 0) {
            container.innerHTML = '<p class="help-text">No email accounts configured yet. Add one to start processing emails.</p>';
            return;
        }
        
        container.innerHTML = accounts.map(account => `
            <div class="card" style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0 0 10px 0;">${account.account_name}</h3>
                        <p style="margin: 5px 0;"><strong>Email:</strong> ${account.email_address}</p>
                        <p style="margin: 5px 0;"><strong>Mail Server:</strong> ${account.imap_server}:${account.imap_port}</p>
                        <p style="margin: 5px 0;">
                            <span class="badge" style="background: ${account.is_active ? '#10b981' : '#6b7280'}">
                                ${account.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </p>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button onclick="editAccount(${account.id})" class="edit-btn" style="padding: 8px 12px;">
                            Edit
                        </button>
                        <button onclick="toggleAccount(${account.id})" class="btn" style="padding: 8px 12px;">
                            ${account.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                        <button onclick="deleteAccount(${account.id}, '${account.account_name}')" class="delete-btn">
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading accounts</p>';
    }
}

function showAccountForm() {
    currentAccountId = null;
    document.getElementById('account-form').style.display = 'block';
    document.getElementById('account-form-title').textContent = 'Add Email Account';
    clearAccountForm();
}

function hideAccountForm() {
    document.getElementById('account-form').style.display = 'none';
    currentAccountId = null;
    clearAccountForm();
}

function clearAccountForm() {
    document.getElementById('account-name').value = '';
    document.getElementById('account-email').value = '';
    document.getElementById('account-imap-server').value = '';
    document.getElementById('account-imap-port').value = '993';
    document.getElementById('account-password').value = '';
    document.getElementById('account-active').checked = true;
    document.getElementById('imap-preset').value = 'gmail';
    applyIMAPPreset(); // Apply Gmail preset by default
}

async function editAccount(accountId) {
    try {
        const response = await fetch(`${API_BASE}/email-accounts/${accountId}`);
        const account = await response.json();
        
        currentAccountId = accountId;
        document.getElementById('account-form').style.display = 'block';
        document.getElementById('account-form-title').textContent = 'Edit Email Account';
        
        document.getElementById('account-name').value = account.account_name;
        document.getElementById('account-email').value = account.email_address;
        document.getElementById('account-imap-server').value = account.imap_server;
        document.getElementById('account-imap-port').value = account.imap_port;
        document.getElementById('account-password').value = ''; // Don't show encrypted password
        document.getElementById('account-active').checked = account.is_active;
        
        // Set preset based on server
        const preset = Object.keys(IMAP_PRESETS).find(key => 
            IMAP_PRESETS[key].server === account.imap_server
        );
        document.getElementById('imap-preset').value = preset || '';
        
        // Scroll form into view
        document.getElementById('account-form').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch (error) {
        alert('Error loading account');
    }
}

async function saveAccount() {
    const name = document.getElementById('account-name').value.trim();
    const email = document.getElementById('account-email').value.trim();
    const server = document.getElementById('account-imap-server').value.trim();
    const port = parseInt(document.getElementById('account-imap-port').value);
    const password = document.getElementById('account-password').value;
    const isActive = document.getElementById('account-active').checked;
    const preset = document.getElementById('imap-preset').value;
    
    // When editing, password is optional (only required if changing it)
    if (!currentAccountId && !password) {
        alert('Password is required for new accounts');
        return;
    }
    
    if (!name || !email || !server) {
        alert('Please fill in all required fields');
        return;
    }
    
    // Validate email domain matches the selected platform
    if (preset && preset !== '' && IMAP_PRESETS[preset]) {
        const emailDomain = email.split('@')[1]?.toLowerCase();
        const allowedDomains = IMAP_PRESETS[preset].domains;
        
        if (!emailDomain || !allowedDomains.includes(emailDomain)) {
            alert(`Email domain does not match the selected platform. Expected: @${allowedDomains.join(' or @')}`);
            return;
        }
    }
    
    try {
        const accountData = {
            account_name: name,
            email_address: email,
            imap_server: server,
            imap_port: port,
            is_active: isActive
        };
        
        // Only include password if it's provided
        if (password) {
            accountData.password = password;
        }
        
        let response;
        if (currentAccountId) {
            // Update existing account
            response = await fetch(`${API_BASE}/email-accounts/${currentAccountId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(accountData)
            });
        } else {
            // Create new account
            response = await fetch(`${API_BASE}/email-accounts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(accountData)
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            hideAccountForm();
            loadAccounts();
            alert(currentAccountId ? 'Account updated successfully!' : 'Account added successfully!');
        } else {
            alert(result.message || 'Error saving account');
        }
    } catch (error) {
        alert('Error saving account: ' + error.message);
    }
}

async function toggleAccount(accountId) {
    try {
        const response = await fetch(`${API_BASE}/email-accounts/${accountId}/toggle`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadAccounts();
        }
    } catch (error) {
        alert('Error toggling account');
    }
}

async function deleteAccount(accountId, accountName) {
    if (!confirm(`Are you sure you want to delete the account "${accountName}"?`)) {
        return;
    }
    
    try {
        await fetch(`${API_BASE}/email-accounts/${accountId}`, {
            method: 'DELETE'
        });
        
        loadAccounts();
    } catch (error) {
        alert('Error deleting account');
    }
}

// SLA Color Coding Helper
function getSLAStatusColor(createdAt, slaHours = 24) {
    const now = new Date();
    const created = new Date(createdAt);
    const hoursDiff = (now - created) / (1000 * 60 * 60);
    
    if (hoursDiff <= slaHours) {
        return { color: '#10b981', label: 'On Time', class: 'sla-green' }; // Green
    } else if (hoursDiff <= slaHours * 2) {
        return { color: '#f59e0b', label: 'Warning', class: 'sla-amber' }; // Amber
    } else {
        return { color: '#ef4444', label: 'Overdue', class: 'sla-red' }; // Red
    }
}

function formatSLABadge(createdAt, slaHours = 24) {
    const status = getSLAStatusColor(createdAt, slaHours);
    const now = new Date();
    const created = new Date(createdAt);
    const hoursDiff = Math.round((now - created) / (1000 * 60 * 60));
    
    return `<span class="badge ${status.class}" style="background: ${status.color}; color: white; padding: 4px 8px; border-radius: 3px; font-size: 12px;">
        ${status.label} (${hoursDiff}h)
    </span>`;
}

// Actions Management
let currentActionId = null;

function showActionPriorityTab(priority) {
    document.querySelectorAll('#actions .sub-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('#actions .priority-content').forEach(content => {
        content.classList.remove('active');
    });
    
    event.target.classList.add('active');
    document.getElementById(`action-priority-${priority}`).classList.add('active');
}

async function loadActions() {
    try {
        const response = await fetch(`${API_BASE}/actions`);
        const actions = await response.json();
        
        const highList = document.getElementById('actions-high-list');
        const importantList = document.getElementById('actions-important-list');
        const lowList = document.getElementById('actions-low-list');
        
        highList.innerHTML = '';
        importantList.innerHTML = '';
        lowList.innerHTML = '';
        
        const highActions = actions.filter(a => a.priority === 'High Priority');
        const importantActions = actions.filter(a => a.priority === 'Important');
        const lowActions = actions.filter(a => a.priority === 'Low Priority');
        
        renderActionList(highActions, highList);
        renderActionList(importantActions, importantList);
        renderActionList(lowActions, lowList);
        
    } catch (error) {
        console.error('Error loading actions:', error);
    }
}

function renderActionList(actions, container) {
    if (actions.length === 0) {
        container.innerHTML = '<p class="help-text">No actions defined yet</p>';
        return;
    }
    
    actions.forEach(action => {
        const actionCard = document.createElement('div');
        actionCard.className = 'card';
        actionCard.style.marginBottom = '15px';
        
        const typeBadge = action.action_type === 'auto' ? 
            '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">AUTO</span>' :
            '<span style="background: #ffc107; color: #000; padding: 2px 8px; border-radius: 3px; font-size: 12px;">HITL</span>';
        
        actionCard.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 10px 0;">${action.action_name} ${typeBadge}</h3>
                    <p style="margin: 5px 0; color: #666;">${action.description || 'No description'}</p>
                    <p style="margin: 5px 0; font-size: 14px;"><strong>SLA:</strong> ${action.sla_hours} hours</p>
                    <p style="margin: 5px 0; font-size: 14px;"><strong>Linked Templates:</strong> ${action.template_count || 0}</p>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button onclick="editAction(${action.id})" class="btn" style="padding: 5px 15px;">Edit</button>
                    <button onclick="deleteAction(${action.id}, '${action.action_name}')" class="btn" style="padding: 5px 15px; background: #dc3545;">Delete</button>
                </div>
            </div>
        `;
        
        container.appendChild(actionCard);
    });
}

function showActionForm(priority = 'High Priority') {
    const form = document.getElementById('action-form');
    form.style.display = 'block';
    document.getElementById('action-form-title').textContent = 'Create Action';
    document.getElementById('action-priority').value = priority;
    currentActionId = null;
    
    document.getElementById('action-name').value = '';
    document.getElementById('action-type').value = 'auto';
    document.getElementById('action-description').value = '';
    document.getElementById('action-sla-hours').value = '24';
    
    loadTemplateLinks();
    
    // Scroll form into view
    setTimeout(() => {
        form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function hideActionForm() {
    document.getElementById('action-form').style.display = 'none';
    currentActionId = null;
}

async function loadTemplateLinks() {
    try {
        const response = await fetch(`${API_BASE}/templates`);
        const templates = await response.json();
        
        const container = document.getElementById('action-template-links');
        container.innerHTML = '';
        
        if (templates.length === 0) {
            container.innerHTML = '<p class="help-text">No templates available</p>';
            return;
        }
        
        let currentActionTemplates = [];
        if (currentActionId) {
            const linkResponse = await fetch(`${API_BASE}/actions/${currentActionId}/templates`);
            currentActionTemplates = await linkResponse.json();
        }
        
        templates.forEach(template => {
            const isLinked = currentActionTemplates.some(t => t.template_id === template.id);
            const checkbox = document.createElement('div');
            checkbox.style.marginBottom = '8px';
            checkbox.innerHTML = `
                <label>
                    <input type="checkbox" class="template-link-checkbox" value="${template.id}" ${isLinked ? 'checked' : ''}>
                    ${template.template_name} 
                    <span class="priority-badge ${template.priority?.toLowerCase().replace(' ', '-') || 'important'}">${template.priority || 'Important'}</span>
                </label>
            `;
            container.appendChild(checkbox);
        });
    } catch (error) {
        console.error('Error loading template links:', error);
    }
}

async function saveAction() {
    const actionData = {
        action_name: document.getElementById('action-name').value,
        priority: document.getElementById('action-priority').value,
        action_type: document.getElementById('action-type').value,
        description: document.getElementById('action-description').value,
        sla_hours: parseInt(document.getElementById('action-sla-hours').value) || 24
    };
    
    if (!actionData.action_name) {
        alert('Please enter an action name');
        return;
    }
    
    try {
        let response;
        if (currentActionId) {
            response = await fetch(`${API_BASE}/actions/${currentActionId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(actionData)
            });
        } else {
            response = await fetch(`${API_BASE}/actions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(actionData)
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            const actionId = currentActionId || result.id;
            
            const linkedTemplates = Array.from(document.querySelectorAll('.template-link-checkbox:checked'))
                .map(cb => parseInt(cb.value));
            
            await fetch(`${API_BASE}/actions/${actionId}/templates`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ template_ids: linkedTemplates })
            });
            
            // Show success message
            const formTitle = document.getElementById('action-form-title');
            const originalTitle = formTitle.textContent;
            formTitle.textContent = '✓ Saved Successfully!';
            formTitle.style.color = '#10b981';
            
            setTimeout(() => {
                hideActionForm();
                formTitle.textContent = originalTitle;
                formTitle.style.color = '';
                loadActions();
            }, 1000);
        } else {
            alert(result.message || 'Error saving action');
        }
    } catch (error) {
        alert('Error saving action');
    }
}

async function editAction(actionId) {
    try {
        const response = await fetch(`${API_BASE}/actions/${actionId}`);
        const action = await response.json();
        
        currentActionId = actionId;
        const form = document.getElementById('action-form');
        form.style.display = 'block';
        document.getElementById('action-form-title').textContent = 'Edit Action';
        
        document.getElementById('action-name').value = action.action_name;
        document.getElementById('action-priority').value = action.priority;
        document.getElementById('action-type').value = action.action_type;
        document.getElementById('action-description').value = action.description || '';
        document.getElementById('action-sla-hours').value = action.sla_hours;
        
        await loadTemplateLinks();
        
        // Scroll form into view
        setTimeout(() => {
            form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    } catch (error) {
        alert('Error loading action');
    }
}

async function deleteAction(actionId, actionName) {
    if (!confirm(`Are you sure you want to delete the action "${actionName}"?`)) {
        return;
    }
    
    try {
        await fetch(`${API_BASE}/actions/${actionId}`, {
            method: 'DELETE'
        });
        
        loadActions();
    } catch (error) {
        alert('Error deleting action');
    }
}

loadStats();
