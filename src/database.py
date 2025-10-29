import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DATABASE_URL = os.environ.get('DATABASE_URL')

def _migrate_env_credentials(conn):
    """Auto-migrate environment variable credentials to email_accounts table"""
    cursor = conn.cursor()
    
    # Check if any accounts exist
    cursor.execute('SELECT COUNT(*) as count FROM email_accounts')
    account_count = cursor.fetchone()['count']
    
    if account_count > 0:
        # Accounts already exist, skip migration
        return
    
    # Check for environment variable credentials
    imap_server = os.environ.get('EMAIL_IMAP_SERVER')
    email_user = os.environ.get('EMAIL_USER')
    email_password = os.environ.get('EMAIL_PASSWORD')
    
    if all([imap_server, email_user, email_password]):
        print("Migrating environment variable credentials to email_accounts...")
        
        # Verify PGPASSWORD is set before attempting encryption
        if not os.environ.get('PGPASSWORD'):
            print("ERROR: PGPASSWORD environment variable is required for secure password encryption")
            print("Skipping migration - please add email accounts manually through the web interface")
            return
        
        try:
            from encryption import encrypt_password
            encrypted_password = encrypt_password(email_password)
            
            cursor.execute('''
                INSERT INTO email_accounts 
                (account_name, email_address, imap_server, imap_port, encrypted_password, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                'Primary Account (from env)',
                email_user,
                imap_server,
                993,
                encrypted_password,
                True
            ))
            conn.commit()
            print("Environment credentials migrated successfully")
        except Exception as e:
            print(f"Migration error: {e}")
            print("Skipping migration - please add email accounts manually through the web interface")
            conn.rollback()

def get_db_connection():
    """Create a database connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database schema"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Email accounts table - MUST be created first as it's referenced by other tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_accounts (
                id SERIAL PRIMARY KEY,
                account_name VARCHAR(255) NOT NULL,
                email_address VARCHAR(255) NOT NULL UNIQUE,
                imap_server VARCHAR(255) NOT NULL,
                imap_port INTEGER DEFAULT 993,
                encrypted_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Configurations table - stores VIP senders, blacklist, etc.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configurations (
                id SERIAL PRIMARY KEY,
                config_type VARCHAR(50) NOT NULL,
                config_key VARCHAR(255) NOT NULL,
                config_value TEXT NOT NULL,
                category VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(config_type, config_key)
            )
        ''')
        
        # Email templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_templates (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                subject_template TEXT,
                body_template TEXT NOT NULL,
                category VARCHAR(100),
                priority VARCHAR(50) DEFAULT 'Important',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add priority column to existing templates if it doesn't exist
        cursor.execute('''
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='email_templates' AND column_name='priority'
                ) THEN
                    ALTER TABLE email_templates ADD COLUMN priority VARCHAR(50) DEFAULT 'Important';
                END IF;
            END $$;
        ''')
        
        # Email drafts table - stores generated drafts awaiting human review
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_drafts (
                id SERIAL PRIMARY KEY,
                original_email_id VARCHAR(255),
                sender_email VARCHAR(255) NOT NULL,
                recipient_email VARCHAR(255) NOT NULL,
                subject TEXT,
                body TEXT NOT NULL,
                classification VARCHAR(100),
                priority VARCHAR(20),
                sentiment VARCHAR(20),
                extracted_data JSONB,
                original_content TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                account_id INTEGER REFERENCES email_accounts(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                sent_at TIMESTAMP
            )
        ''')
        
        # Email processing log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_processing_log (
                id SERIAL PRIMARY KEY,
                email_id VARCHAR(255),
                sender_email VARCHAR(255),
                subject TEXT,
                received_at TIMESTAMP,
                processing_status VARCHAR(50),
                classification VARCHAR(100),
                priority VARCHAR(20),
                sentiment VARCHAR(20),
                validation_result VARCHAR(50),
                error_message TEXT,
                account_id INTEGER REFERENCES email_accounts(id),
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id SERIAL PRIMARY KEY,
                setting_key VARCHAR(100) NOT NULL UNIQUE,
                setting_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Actions table - stores auto and human-in-the-loop actions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                action_type VARCHAR(50) NOT NULL,
                trigger_priority VARCHAR(50) NOT NULL,
                is_auto BOOLEAN DEFAULT FALSE,
                config JSONB,
                sla_hours INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Action-Template join table for many-to-many relationship
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_templates (
                id SERIAL PRIMARY KEY,
                action_id INTEGER REFERENCES actions(id) ON DELETE CASCADE,
                template_id INTEGER REFERENCES email_templates(id) ON DELETE CASCADE,
                ordering INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(action_id, template_id)
            )
        ''')
        
        # Action execution log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_execution_log (
                id SERIAL PRIMARY KEY,
                action_id INTEGER REFERENCES actions(id),
                draft_id INTEGER REFERENCES email_drafts(id),
                execution_type VARCHAR(50),
                execution_status VARCHAR(50),
                sla_due TIMESTAMP,
                completed_at TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migrate blacklist entries to subscriptions_whitelist
        cursor.execute('''
            UPDATE configurations 
            SET config_type = 'subscriptions_whitelist' 
            WHERE config_type = 'blacklist'
        ''')
        
        conn.commit()
        print("Database initialized successfully")
        
        # Auto-migrate environment variable credentials to email_accounts table
        _migrate_env_credentials(conn)
