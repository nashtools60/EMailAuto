const API_BASE = '/api';

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
    if (tabName === 'config') loadConfig();
    if (tabName === 'templates') loadTemplates();
    if (tabName === 'settings') loadSettings();
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
    } catch (error) {
        console.error('Error loading stats:', error);
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
                        <div class="draft-meta">
                            <span class="badge badge-${draft.priority.toLowerCase()}">${draft.priority}</span>
                            <span class="badge badge-${draft.sentiment.toLowerCase()}">${draft.sentiment}</span>
                            <span class="badge">${draft.classification}</span>
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
    loadConfigList('whitelist', 'whitelist-items');
    loadConfigList('blacklist', 'blacklist-items');
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
                    <button class="delete-btn" onclick="deleteConfig('${type}', '${item.key}')">Remove</button>
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

async function addBlacklist() {
    const input = document.getElementById('blacklist-input');
    const categorySelect = document.getElementById('blacklist-category');
    const value = input.value.trim();
    const category = categorySelect.value;
    
    if (!value) return;
    
    try {
        await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                config_type: 'blacklist',
                config_key: value,
                config_value: value,
                category: category
            })
        });
        
        input.value = '';
        loadConfigList('blacklist', 'blacklist-items');
    } catch (error) {
        alert('Error adding blacklist entry');
    }
}

async function deleteConfig(type, key) {
    try {
        await fetch(`${API_BASE}/config/${type}/${key}`, { method: 'DELETE' });
        loadConfigList(type, `${type}-items`);
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
        
        container.innerHTML = templates.map(template => `
            <div class="template-card">
                <div class="template-header">
                    <div>
                        <strong>${template.name}</strong>
                        <span class="badge">${template.category || 'General'}</span>
                    </div>
                    <button class="delete-btn" onclick="deleteTemplate(${template.id})">Delete</button>
                </div>
                ${template.subject_template ? `<div style="margin-top: 10px;"><strong>Subject:</strong> ${template.subject_template}</div>` : ''}
                <div style="margin-top: 10px;"><strong>Body:</strong></div>
                <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 5px; white-space: pre-wrap;">${template.body_template}</pre>
            </div>
        `).join('');
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
    document.getElementById('template-subject').value = '';
    document.getElementById('template-body').value = '';
}

async function saveTemplate() {
    const name = document.getElementById('template-name').value.trim();
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
            body: JSON.stringify({ name, category, subject_template: subject, body_template: body })
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

loadStats();
