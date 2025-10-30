import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

from database import init_db, get_db
from email_service import EmailService
from ai_processor import generate_draft_response, analyze_email_combined
from encryption import encrypt_password, decrypt_password

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

# Initialize database on startup
with app.app_context():
    init_db()


def get_priority_level(priority):
    """Convert priority string to numeric level for comparison (lower is higher priority)"""
    priority_levels = {
        'P0': 0,
        'P1': 1,
        'P2': 2,
        'P3': 3
    }
    return priority_levels.get(priority, 2)


def is_advertisement(classification, sender_email, subscriptions_whitelist):
    """
    Determine if an email is a pure advertisement that should be deleted.
    
    Criteria for pure adverts:
    - Classified as Marketing, Spam, Promotional, Newsletter, or similar
    - NOT in the subscriptions whitelist (emails you want to keep)
    - Contains typical marketing/promotional language
    
    Returns True if the email should be permanently deleted
    """
    # Marketing-related classifications that indicate adverts
    advert_classifications = [
        'marketing',
        'spam',
        'promotional',
        'advertisement',
        'newsletter',
        'sales',
        'offer'
    ]
    
    # Check if classification matches advert patterns
    classification_lower = classification.lower()
    is_marketing = any(advert_type in classification_lower for advert_type in advert_classifications)
    
    if not is_marketing:
        return False
    
    # Check if sender is in subscriptions whitelist (keep these)
    sender_lower = sender_email.lower()
    for whitelisted in subscriptions_whitelist:
        whitelisted_lower = whitelisted.lower()
        if whitelisted_lower in sender_lower or sender_lower.endswith(whitelisted_lower):
            return False  # Keep whitelisted newsletters
    
    # It's marketing and not whitelisted = pure advert to delete
    return True


def apply_triaging_matrix(sender_email, subject, body, ai_priority, sender_priorities, subject_keywords, body_keywords):
    """
    Apply triaging matrix rules to determine final priority.
    Priority order: Sender whitelist > Subject keywords > Body keywords > AI priority
    Priority levels: High Priority = P0/P1, Important = P2, Low Priority = P3
    """
    priority_map = {
        'High Priority': 'P0',
        'Important': 'P2',
        'Low Priority': 'P3'
    }
    
    final_priority = ai_priority
    
    # Check sender whitelist (highest priority)
    for sender_config in sender_priorities:
        sender_pattern = sender_config['config_value'].lower()
        category = sender_config.get('category', '')
        
        if sender_pattern in sender_email.lower() or sender_email.lower().endswith(sender_pattern):
            if category in priority_map:
                final_priority = priority_map[category]
                break
    
    # Check subject keywords (second priority)
    subject_lower = subject.lower()
    for keyword_config in subject_keywords:
        keywords_str = keyword_config['config_value']
        category = keyword_config.get('category', '')
        
        # Split by comma to handle multiple keywords in one entry
        keywords = [k.strip().lower() for k in keywords_str.split(',')]
        
        for keyword in keywords:
            if keyword and keyword in subject_lower:
                if category in priority_map:
                    mapped_priority = priority_map[category]
                    # Only upgrade priority, never downgrade
                    if get_priority_level(mapped_priority) < get_priority_level(final_priority):
                        final_priority = mapped_priority
                break
    
    # Check body keywords (third priority)
    body_lower = body.lower()
    for keyword_config in body_keywords:
        keywords_str = keyword_config['config_value']
        category = keyword_config.get('category', '')
        
        # Split by comma to handle multiple keywords in one entry
        keywords = [k.strip().lower() for k in keywords_str.split(',')]
        
        for keyword in keywords:
            if keyword and keyword in body_lower:
                if category in priority_map:
                    mapped_priority = priority_map[category]
                    # Only upgrade priority, never downgrade
                    if get_priority_level(mapped_priority) < get_priority_level(final_priority):
                        final_priority = mapped_priority
                break
    
    return final_priority


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    """Get or update system configuration"""
    if request.method == 'GET':
        config_type = request.args.get('type', 'all')
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            if config_type == 'all':
                cursor.execute('SELECT * FROM configurations ORDER BY config_type, config_key')
            else:
                cursor.execute('SELECT * FROM configurations WHERE config_type = %s', (config_type,))
            
            configs = cursor.fetchall()
            
            # Group by config_type
            result = {}
            for config in configs:
                config_type = config['config_type']
                if config_type not in result:
                    result[config_type] = []
                result[config_type].append({
                    'key': config['config_key'],
                    'value': config['config_value'],
                    'category': config.get('category')
                })
            
            return jsonify(result)
    
    elif request.method == 'POST':
        data = request.json
        config_type = data.get('config_type')
        config_key = data.get('config_key')
        config_value = data.get('config_value')
        category = data.get('category')
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO configurations (config_type, config_key, config_value, category)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (config_type, config_key)
                DO UPDATE SET config_value = %s, category = %s, updated_at = CURRENT_TIMESTAMP
            ''', (config_type, config_key, config_value, category, config_value, category))
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Configuration updated'})


@app.route('/api/config/<config_type>/<config_key>', methods=['PUT', 'DELETE'])
def update_or_delete_config(config_type, config_key):
    """Update or delete a configuration entry"""
    if request.method == 'PUT':
        data = request.json
        new_key = data.get('config_key')
        new_value = data.get('config_value')
        category = data.get('category')
        
        with get_db() as conn:
            cursor = conn.cursor()
            # Delete old entry
            cursor.execute('DELETE FROM configurations WHERE config_type = %s AND config_key = %s',
                          (config_type, config_key))
            # Insert new entry
            cursor.execute('''
                INSERT INTO configurations (config_type, config_key, config_value, category)
                VALUES (%s, %s, %s, %s)
            ''', (config_type, new_key, new_value, category))
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Configuration updated'})
    
    elif request.method == 'DELETE':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM configurations WHERE config_type = %s AND config_key = %s',
                          (config_type, config_key))
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Configuration deleted'})


@app.route('/api/templates', methods=['GET', 'POST'])
def manage_templates():
    """Get or create email templates"""
    if request.method == 'GET':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM email_templates ORDER BY category, name')
            templates = cursor.fetchall()
            return jsonify(list(templates))
    
    elif request.method == 'POST':
        data = request.json
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO email_templates (name, subject_template, body_template, category, priority)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (name)
                DO UPDATE SET 
                    subject_template = %s,
                    body_template = %s,
                    category = %s,
                    priority = %s,
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                data['name'],
                data.get('subject_template'),
                data['body_template'],
                data.get('category'),
                data.get('priority', 'Important'),
                data.get('subject_template'),
                data['body_template'],
                data.get('category'),
                data.get('priority', 'Important')
            ))
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Template saved'})


@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete an email template"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM email_templates WHERE id = %s', (template_id,))
        conn.commit()
    
    return jsonify({'success': True, 'message': 'Template deleted'})


@app.route('/api/process-emails', methods=['POST'])
def process_emails():
    """
    Manually trigger email processing
    Fetches new emails from all active accounts, processes them, and creates drafts
    """
    try:
        # Get all active email accounts
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, account_name, email_address, imap_server, imap_port, encrypted_password
                FROM email_accounts 
                WHERE is_active = TRUE
                ORDER BY id
            ''')
            accounts = cursor.fetchall()
        
        if not accounts:
            return jsonify({'success': False, 'error': 'No active email accounts configured. Please add an email account in the Email Accounts tab.'}), 400
        
        all_processed = []
        
        # Process emails from each account
        for account in accounts:
            try:
                # Decrypt password
                password = decrypt_password(account['encrypted_password'])
                
                # Initialize email service for this account
                email_service = EmailService(
                    account['imap_server'],
                    account['email_address'],
                    password
                )
                
                # Fetch new emails
                new_emails = email_service.fetch_new_emails(limit=10)
                
                # Get whitelist, subscriptions whitelist, subject keywords, and body keywords
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT config_value FROM configurations WHERE config_type = 'whitelist'")
                    whitelist = [row['config_value'] for row in cursor.fetchall()]
                    
                    cursor.execute("SELECT config_value FROM configurations WHERE config_type = 'subscriptions_whitelist'")
                    subscriptions_whitelist = [row['config_value'] for row in cursor.fetchall()]
                    
                    # Get priority-based sender whitelists
                    cursor.execute("SELECT config_value, category FROM configurations WHERE config_type = 'whitelist'")
                    sender_priorities = cursor.fetchall()
                    
                    # Get priority-based subject keywords
                    cursor.execute("SELECT config_value, category FROM configurations WHERE config_type = 'subject_keyword'")
                    subject_keywords = cursor.fetchall()
                    
                    # Get priority-based body keywords
                    cursor.execute("SELECT config_value, category FROM configurations WHERE config_type = 'body_keyword'")
                    body_keywords = cursor.fetchall()
                
                # Process emails from this account
                for email_data in new_emails:
                    sender_email = email_data['sender_email']
                    
                    # Validate sender
                    validation_result = email_service.validate_sender(sender_email, whitelist, subscriptions_whitelist)
                    
                    if validation_result == 'subscription_not_whitelisted':
                        # Skip subscription emails not in whitelist (auto-unsubscribe/delete)
                        with get_db() as conn:
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO email_processing_log 
                                (email_id, sender_email, subject, received_at, processing_status, validation_result, account_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ''', (
                                email_data['id'],
                                sender_email,
                                email_data['subject'],
                                email_data['date'],
                                'rejected',
                                validation_result,
                                account['id']
                            ))
                        continue
                    
                    # Normalize content
                    normalized_content = email_service.normalize_content(
                        email_data.get('body_html', ''),
                        email_data.get('body_text', '')
                    )
                    
                    # AI Processing - COMBINED (1 API call instead of 4)
                    analysis = analyze_email_combined(
                        email_data['subject'],
                        normalized_content,
                        sender_email
                    )
                    
                    # Extract results from combined analysis
                    classification = analysis.get('classification', 'General Inquiry')
                    ai_priority = analysis.get('priority', 'P2')
                    sentiment = analysis.get('sentiment', 'Neutral')
                    entities = analysis.get('entities', [])
                    summary_narrative = analysis.get('summary_narrative', '')
                    summary_text = summary_narrative
                    action_required = analysis.get('action_required', False)
                    
                    # Check if this is a pure advert (marketing email not in subscriptions whitelist)
                    is_pure_advert = is_advertisement(classification, sender_email, subscriptions_whitelist)
                    
                    if is_pure_advert:
                        # Permanently delete pure adverts from mailbox
                        email_service.delete_email(email_data['id'])
                        
                        # Log the deletion
                        with get_db() as conn:
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO email_processing_log 
                                (email_id, sender_email, subject, received_at, processing_status, 
                                 classification, priority, sentiment, validation_result, account_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ''', (
                                email_data['id'],
                                sender_email,
                                email_data['subject'],
                                email_data['date'],
                                'deleted_advert',
                                classification,
                                ai_priority,
                                sentiment,
                                'pure_advertisement',
                                account['id']
                            ))
                        continue  # Skip to next email
                    
                    # Apply triaging matrix to determine final priority
                    priority = apply_triaging_matrix(
                        sender_email,
                        email_data['subject'],
                        normalized_content,
                        ai_priority,
                        sender_priorities,
                        subject_keywords,
                        body_keywords
                    )
                    
                    # Check if email requires action (skip draft creation for informational emails)
                    if not action_required:
                        # Mark email as read and log as no action required
                        email_service.mark_as_read(email_data['id'])
                        
                        with get_db() as conn:
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO email_processing_log 
                                (email_id, sender_email, subject, received_at, processing_status, 
                                 classification, priority, sentiment, validation_result, account_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ''', (
                                email_data['id'],
                                sender_email,
                                email_data['subject'],
                                email_data['date'],
                                'no_action_required',
                                classification,
                                priority,
                                sentiment,
                                'informational_only',
                                account['id']
                            ))
                        continue  # Skip draft generation
                    
                    # Generate draft response (1 API call) - only for actionable emails
                    draft = generate_draft_response(
                        email_data['subject'],
                        normalized_content,
                        sender_email,
                        classification
                    )
                    
                    # Save draft to database
                    with get_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO email_drafts 
                            (original_email_id, sender_email, recipient_email, subject, body, 
                             classification, priority, sentiment, extracted_data, original_content, summary, status, account_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        ''', (
                            email_data['id'],
                            sender_email,
                            account['email_address'],
                            draft.get('subject'),
                            draft.get('body'),
                            classification,
                            priority,
                            sentiment,
                            json.dumps(entities),
                            normalized_content,
                            summary_text,
                            'pending',
                            account['id']
                        ))
                        draft_id = cursor.fetchone()['id']
                        
                        # Log processing
                        cursor.execute('''
                            INSERT INTO email_processing_log 
                            (email_id, sender_email, subject, received_at, processing_status, 
                             classification, priority, sentiment, validation_result, account_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            email_data['id'],
                            sender_email,
                            email_data['subject'],
                            email_data['date'],
                            'processed',
                            classification,
                            priority,
                            sentiment,
                            validation_result,
                            account['id']
                        ))
                    
                    # Mark email as read so it won't be reprocessed
                    email_service.mark_as_read(email_data['id'])
                    
                    all_processed.append({
                        'account_name': account['account_name'],
                        'email_id': email_data['id'],
                        'draft_id': draft_id,
                        'classification': classification,
                        'priority': priority
                    })
            
            except Exception as e:
                print(f"Error processing account {account['account_name']}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'processed_count': len(all_processed),
            'processed': all_processed
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/drafts', methods=['GET'])
def get_drafts():
    """Get all pending drafts for review"""
    status = request.args.get('status', 'pending')
    account_id = request.args.get('account_id', '')
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        if account_id:
            cursor.execute('''
                SELECT d.*, a.account_name, a.email_address as account_email
                FROM email_drafts d
                LEFT JOIN email_accounts a ON d.account_id = a.id
                WHERE d.status = %s AND d.account_id = %s
                ORDER BY d.created_at DESC
            ''', (status, account_id))
        else:
            cursor.execute('''
                SELECT d.*, a.account_name, a.email_address as account_email
                FROM email_drafts d
                LEFT JOIN email_accounts a ON d.account_id = a.id
                WHERE d.status = %s 
                ORDER BY d.created_at DESC
            ''', (status,))
        
        drafts = cursor.fetchall()
        return jsonify(list(drafts))


@app.route('/api/drafts/<int:draft_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_draft(draft_id):
    """Get, update, or delete a specific draft"""
    if request.method == 'GET':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM email_drafts WHERE id = %s', (draft_id,))
            draft = cursor.fetchone()
            return jsonify(draft) if draft else ('', 404)
    
    elif request.method == 'PUT':
        data = request.json
        action = data.get('action')
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            if action == 'approve':
                cursor.execute('''
                    UPDATE email_drafts 
                    SET status = 'approved', reviewed_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                ''', (draft_id,))
                # TODO: Actually send the email here
                
            elif action == 'reject':
                cursor.execute('''
                    UPDATE email_drafts 
                    SET status = 'rejected', reviewed_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                ''', (draft_id,))
            
            elif action == 'update':
                cursor.execute('''
                    UPDATE email_drafts 
                    SET subject = %s, body = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                ''', (data.get('subject'), data.get('body'), draft_id))
            
            conn.commit()
        
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM email_drafts WHERE id = %s', (draft_id,))
            conn.commit()
        
        return jsonify({'success': True})


@app.route('/api/settings', methods=['GET', 'POST'])
def manage_settings():
    """Get or update system settings"""
    if request.method == 'GET':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT setting_key, setting_value FROM system_settings')
            settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
            
            # SECURITY: Never expose credentials in API responses
            if 'email_password' in settings:
                settings['email_password'] = '***REDACTED***'
            
            return jsonify(settings)
    
    elif request.method == 'POST':
        data = request.json
        
        with get_db() as conn:
            cursor = conn.cursor()
            for key, value in data.items():
                cursor.execute('''
                    INSERT INTO system_settings (setting_key, setting_value)
                    VALUES (%s, %s)
                    ON CONFLICT (setting_key)
                    DO UPDATE SET setting_value = %s, updated_at = CURRENT_TIMESTAMP
                ''', (key, value, value))
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Settings updated'})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get processing statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM email_drafts WHERE status = %s', ('pending',))
        pending_drafts = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM email_drafts WHERE status = %s', ('approved',))
        approved_drafts = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM email_processing_log')
        total_processed = cursor.fetchone()['count']
        
        cursor.execute('''
            SELECT classification, COUNT(*) as count 
            FROM email_processing_log 
            WHERE classification IS NOT NULL
            GROUP BY classification
        ''')
        by_category = cursor.fetchall()
        
        return jsonify({
            'pending_drafts': pending_drafts,
            'approved_drafts': approved_drafts,
            'total_processed': total_processed,
            'by_category': list(by_category)
        })


@app.route('/api/email-summaries', methods=['GET'])
def get_email_summaries():
    """Get email summaries grouped by priority (High Priority and Important)"""
    account_id = request.args.get('account_id', None)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        if account_id:
            cursor.execute('''
                SELECT 
                    ed.id,
                    ed.subject as original_subject,
                    ed.sender_email,
                    ed.priority,
                    ed.sentiment,
                    ed.classification,
                    ed.summary,
                    ed.created_at as received_at,
                    ea.account_name,
                    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - ed.created_at))/3600 as hours_old
                FROM email_drafts ed
                LEFT JOIN email_accounts ea ON ed.account_id = ea.id
                WHERE ed.status = 'pending'
                  AND ed.priority IN ('P0', 'P1', 'P2')
                  AND ed.account_id = %s
                ORDER BY ed.created_at ASC
            ''', (account_id,))
        else:
            cursor.execute('''
                SELECT 
                    ed.id,
                    ed.subject as original_subject,
                    ed.sender_email,
                    ed.priority,
                    ed.sentiment,
                    ed.classification,
                    ed.summary,
                    ed.created_at as received_at,
                    ea.account_name,
                    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - ed.created_at))/3600 as hours_old
                FROM email_drafts ed
                LEFT JOIN email_accounts ea ON ed.account_id = ea.id
                WHERE ed.status = 'pending'
                  AND ed.priority IN ('P0', 'P1', 'P2')
                ORDER BY ed.created_at ASC
            ''')
        
        all_emails = cursor.fetchall()
        
        high_priority = []
        important = []
        
        for email in all_emails:
            email_dict = dict(email)
            email_dict['sla_status'] = get_sla_status(email_dict['hours_old'])
            
            if email['priority'] == 'P0':
                high_priority.append(email_dict)
            elif email['priority'] in ('P1', 'P2'):
                important.append(email_dict)
        
        return jsonify({
            'high_priority': high_priority,
            'important': important
        })


def get_sla_status(hours_old):
    """Get SLA status color based on age"""
    if hours_old <= 24:
        return 'green'
    elif hours_old <= 48:
        return 'amber'
    else:
        return 'red'


@app.route('/api/email-accounts', methods=['GET', 'POST'])
def manage_email_accounts():
    """Get or create email accounts"""
    if request.method == 'GET':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, account_name, email_address, imap_server, imap_port, is_active, 
                       created_at, updated_at
                FROM email_accounts 
                ORDER BY created_at DESC
            ''')
            accounts = cursor.fetchall()
            return jsonify(list(accounts))
    
    elif request.method == 'POST':
        data = request.json
        email_address = data['email_address']
        imap_server = data['imap_server']
        
        # Validate email domain matches the IMAP server platform
        email_domain = email_address.split('@')[-1].lower() if '@' in email_address else ''
        
        # Platform domain mappings
        platform_domains = {
            'imap.gmail.com': ['gmail.com', 'googlemail.com'],
            'outlook.office365.com': ['outlook.com', 'hotmail.com', 'live.com'],
            'imap.mail.yahoo.com': ['yahoo.com', 'ymail.com', 'rocketmail.com'],
            'imap.mail.me.com': ['icloud.com', 'me.com', 'mac.com'],
            'imap.aol.com': ['aol.com']
        }
        
        # Check if the IMAP server is a known platform and validate domain
        if imap_server in platform_domains:
            allowed_domains = platform_domains[imap_server]
            if email_domain not in allowed_domains:
                return jsonify({
                    'success': False, 
                    'message': f'Email domain does not match the selected platform. Expected: @{" or @".join(allowed_domains)}'
                }), 400
        
        # Check if email exists in whitelist or subscriptions whitelist
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check whitelist
            cursor.execute('''
                SELECT COUNT(*) as count FROM configurations 
                WHERE config_type = 'whitelist' AND config_key = %s
            ''', (email_address,))
            in_whitelist = cursor.fetchone()['count'] > 0
            
            # Check subscriptions whitelist
            cursor.execute('''
                SELECT COUNT(*) as count FROM configurations 
                WHERE config_type = 'subscriptions_whitelist' AND config_key = %s
            ''', (email_address,))
            in_subscriptions = cursor.fetchone()['count'] > 0
            
            if in_whitelist:
                return jsonify({'success': False, 'message': 'This email address already exists in the Whitelist'}), 400
            
            if in_subscriptions:
                return jsonify({'success': False, 'message': 'This email address already exists in the Subscriptions Whitelist'}), 400
        
        encrypted_password = encrypt_password(data['password'])
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO email_accounts 
                    (account_name, email_address, imap_server, imap_port, encrypted_password, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                data['account_name'],
                data['email_address'],
                data['imap_server'],
                data.get('imap_port', 993),
                encrypted_password,
                data.get('is_active', True)
            ))
            account_id = cursor.fetchone()['id']
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Email account added', 'id': account_id})


@app.route('/api/email-accounts/<int:account_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_email_account(account_id):
    """Get, update, or delete an email account"""
    if request.method == 'GET':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM email_accounts WHERE id = %s', (account_id,))
            account = cursor.fetchone()
            
            if not account:
                return jsonify({'success': False, 'message': 'Account not found'}), 404
            
            return jsonify(dict(account))
    
    elif request.method == 'PUT':
        data = request.json
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            if 'password' in data and data['password']:
                encrypted_password = encrypt_password(data['password'])
                cursor.execute('''
                    UPDATE email_accounts 
                    SET account_name = %s, email_address = %s, imap_server = %s, 
                        imap_port = %s, encrypted_password = %s, is_active = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                ''', (
                    data['account_name'],
                    data['email_address'],
                    data['imap_server'],
                    data.get('imap_port', 993),
                    encrypted_password,
                    data.get('is_active', True),
                    account_id
                ))
            else:
                cursor.execute('''
                    UPDATE email_accounts 
                    SET account_name = %s, email_address = %s, imap_server = %s, 
                        imap_port = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                ''', (
                    data['account_name'],
                    data['email_address'],
                    data['imap_server'],
                    data.get('imap_port', 993),
                    data.get('is_active', True),
                    account_id
                ))
            
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Email account updated'})
    
    elif request.method == 'DELETE':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM email_accounts WHERE id = %s', (account_id,))
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Email account deleted'})


@app.route('/api/email-accounts/<int:account_id>/toggle', methods=['POST'])
def toggle_email_account(account_id):
    """Toggle email account active status"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE email_accounts 
            SET is_active = NOT is_active, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING is_active
        ''', (account_id,))
        result = cursor.fetchone()
        conn.commit()
    
    return jsonify({'success': True, 'is_active': result['is_active']})


# Actions Management API
@app.route('/api/actions', methods=['GET', 'POST'])
def manage_actions():
    """Get all actions or create a new action"""
    if request.method == 'GET':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, COUNT(at.template_id) as template_count
                FROM actions a
                LEFT JOIN action_templates at ON a.id = at.action_id
                GROUP BY a.id
                ORDER BY 
                    CASE a.priority
                        WHEN 'High Priority' THEN 1
                        WHEN 'Important' THEN 2
                        WHEN 'Low Priority' THEN 3
                    END,
                    a.created_at DESC
            ''')
            actions = cursor.fetchall()
        
        return jsonify(actions)
    
    elif request.method == 'POST':
        data = request.json
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO actions (action_name, priority, action_type, description, sla_hours)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                data['action_name'],
                data['priority'],
                data['action_type'],
                data.get('description', ''),
                data.get('sla_hours', 24)
            ))
            action_id = cursor.fetchone()['id']
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Action created', 'id': action_id})


@app.route('/api/actions/<int:action_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_action(action_id):
    """Get, update, or delete a specific action"""
    if request.method == 'GET':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM actions WHERE id = %s', (action_id,))
            action = cursor.fetchone()
        
        if not action:
            return jsonify({'error': 'Action not found'}), 404
        
        return jsonify(action)
    
    elif request.method == 'PUT':
        data = request.json
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE actions
                SET action_name = %s, priority = %s, action_type = %s, 
                    description = %s, sla_hours = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (
                data['action_name'],
                data['priority'],
                data['action_type'],
                data.get('description', ''),
                data.get('sla_hours', 24),
                action_id
            ))
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Action updated'})
    
    elif request.method == 'DELETE':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM action_templates WHERE action_id = %s', (action_id,))
            cursor.execute('DELETE FROM actions WHERE id = %s', (action_id,))
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Action deleted'})


@app.route('/api/actions/<int:action_id>/templates', methods=['GET', 'POST'])
def manage_action_templates(action_id):
    """Get or update template links for an action"""
    if request.method == 'GET':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT at.*, t.template_name, t.priority
                FROM action_templates at
                JOIN email_templates t ON at.template_id = t.id
                WHERE at.action_id = %s
                ORDER BY at.execution_order
            ''', (action_id,))
            templates = cursor.fetchall()
        
        return jsonify(templates)
    
    elif request.method == 'POST':
        data = request.json
        template_ids = data.get('template_ids', [])
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM action_templates WHERE action_id = %s', (action_id,))
            
            for order, template_id in enumerate(template_ids, start=1):
                cursor.execute('''
                    INSERT INTO action_templates (action_id, template_id, execution_order)
                    VALUES (%s, %s, %s)
                ''', (action_id, template_id, order))
            
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Template links updated'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
