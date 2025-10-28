import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

from database import init_db, get_db
from email_service import EmailService
from ai_processor import classify_email, analyze_priority_sentiment, extract_entities, generate_draft_response

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

# Initialize database on startup
with app.app_context():
    init_db()


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
                    'value': config['config_value']
                })
            
            return jsonify(result)
    
    elif request.method == 'POST':
        data = request.json
        config_type = data.get('config_type')
        config_key = data.get('config_key')
        config_value = data.get('config_value')
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO configurations (config_type, config_key, config_value)
                VALUES (%s, %s, %s)
                ON CONFLICT (config_type, config_key)
                DO UPDATE SET config_value = %s, updated_at = CURRENT_TIMESTAMP
            ''', (config_type, config_key, config_value, config_value))
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Configuration updated'})


@app.route('/api/config/<config_type>/<config_key>', methods=['DELETE'])
def delete_config(config_type, config_key):
    """Delete a configuration entry"""
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
                INSERT INTO email_templates (name, subject_template, body_template, category)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name)
                DO UPDATE SET 
                    subject_template = %s,
                    body_template = %s,
                    category = %s,
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                data['name'],
                data.get('subject_template'),
                data['body_template'],
                data.get('category'),
                data.get('subject_template'),
                data['body_template'],
                data.get('category')
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
    Fetches new emails, processes them, and creates drafts
    """
    try:
        # Get email credentials from system settings
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_key, setting_value FROM system_settings WHERE setting_key IN ('imap_server', 'email_user', 'email_password')")
            settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
        
        if not all(k in settings for k in ['imap_server', 'email_user', 'email_password']):
            return jsonify({'success': False, 'error': 'Email credentials not configured'}), 400
        
        # Initialize email service
        email_service = EmailService(
            settings['imap_server'],
            settings['email_user'],
            settings['email_password']
        )
        
        # Fetch new emails
        new_emails = email_service.fetch_new_emails(limit=10)
        
        # Get whitelist and blacklist
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT config_value FROM configurations WHERE config_type = 'whitelist'")
            whitelist = [row['config_value'] for row in cursor.fetchall()]
            
            cursor.execute("SELECT config_value FROM configurations WHERE config_type = 'blacklist'")
            blacklist = [row['config_value'] for row in cursor.fetchall()]
        
        processed = []
        
        for email_data in new_emails:
            sender_email = email_data['sender_email']
            
            # Validate sender
            validation_result = email_service.validate_sender(sender_email, whitelist, blacklist)
            
            if validation_result == 'blacklisted':
                # Skip blacklisted emails
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO email_processing_log 
                        (email_id, sender_email, subject, received_at, processing_status, validation_result)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (
                        email_data['id'],
                        sender_email,
                        email_data['subject'],
                        email_data['date'],
                        'rejected',
                        validation_result
                    ))
                continue
            
            # Normalize content
            normalized_content = email_service.normalize_content(
                email_data.get('body_html', ''),
                email_data.get('body_text', '')
            )
            
            # AI Processing
            classification = classify_email(email_data['subject'], normalized_content)
            priority_sentiment = analyze_priority_sentiment(
                email_data['subject'],
                normalized_content,
                sender_email
            )
            entities = extract_entities(email_data['subject'], normalized_content)
            
            # Generate draft response
            draft = generate_draft_response(
                email_data['subject'],
                normalized_content,
                sender_email,
                classification.get('category', 'General Inquiry')
            )
            
            # Save draft to database
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO email_drafts 
                    (original_email_id, sender_email, recipient_email, subject, body, 
                     classification, priority, sentiment, extracted_data, original_content, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    email_data['id'],
                    settings['email_user'],
                    sender_email,
                    draft.get('subject'),
                    draft.get('body'),
                    classification.get('category'),
                    priority_sentiment.get('priority'),
                    priority_sentiment.get('sentiment'),
                    json.dumps(entities),
                    normalized_content,
                    'pending'
                ))
                draft_id = cursor.fetchone()['id']
                
                # Log processing
                cursor.execute('''
                    INSERT INTO email_processing_log 
                    (email_id, sender_email, subject, received_at, processing_status, 
                     classification, priority, sentiment, validation_result)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    email_data['id'],
                    sender_email,
                    email_data['subject'],
                    email_data['date'],
                    'processed',
                    classification.get('category'),
                    priority_sentiment.get('priority'),
                    priority_sentiment.get('sentiment'),
                    validation_result
                ))
            
            processed.append({
                'email_id': email_data['id'],
                'draft_id': draft_id,
                'classification': classification.get('category'),
                'priority': priority_sentiment.get('priority')
            })
        
        return jsonify({
            'success': True,
            'processed_count': len(processed),
            'processed': processed
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/drafts', methods=['GET'])
def get_drafts():
    """Get all pending drafts for review"""
    status = request.args.get('status', 'pending')
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM email_drafts 
            WHERE status = %s 
            ORDER BY created_at DESC
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
            
            # Don't expose password in response
            if 'email_password' in settings:
                settings['email_password'] = '***'
            
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
