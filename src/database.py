import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DATABASE_URL = os.environ.get('DATABASE_URL')

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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
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
        
        conn.commit()
        print("Database initialized successfully")
