#!/usr/bin/env python3
"""Test email connection to verify Gmail access"""

import sys
from email_service import EmailService
from encryption import decrypt_password
from database import get_db

def test_email_connection(account_id=None, test_email=None, test_password=None):
    """Test email connection for a specific account"""
    
    if test_email and test_password:
        # Test with provided credentials
        print(f"\n🔍 Testing connection to {test_email}...")
        print(f"IMAP Server: imap.gmail.com:993")
        
        try:
            service = EmailService('imap.gmail.com', test_email, test_password)
            emails = service.fetch_new_emails(limit=5)
            
            print(f"✅ SUCCESS! Connected to {test_email}")
            print(f"📧 Found {len(emails)} email(s)")
            
            for i, email in enumerate(emails[:3], 1):
                print(f"\nEmail {i}:")
                print(f"  From: {email.get('from', 'Unknown')}")
                print(f"  Subject: {email.get('subject', 'No Subject')}")
                print(f"  Date: {email.get('date', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"❌ FAILED to connect to {test_email}")
            print(f"Error: {str(e)}")
            print(f"\n💡 For Gmail, make sure you're using an App Password, not your regular password")
            print(f"   Generate one at: https://myaccount.google.com/apppasswords")
            return False
    
    else:
        # Test with database account
        with get_db() as conn:
            cursor = conn.cursor()
            
            if account_id:
                cursor.execute('SELECT * FROM email_accounts WHERE id = %s', (account_id,))
            else:
                cursor.execute('SELECT * FROM email_accounts WHERE is_active = true LIMIT 1')
            
            account = cursor.fetchone()
            
            if not account:
                print("❌ No email account found in database")
                return False
            
            print(f"\n🔍 Testing connection to {account['email_address']}...")
            print(f"Account: {account['account_name']}")
            print(f"IMAP: {account['imap_server']}:{account['imap_port']}")
            
            try:
                password = decrypt_password(account['encrypted_password'])
                service = EmailService(
                    account['imap_server'],
                    account['email_address'],
                    password
                )
                emails = service.fetch_new_emails(limit=5)
                
                print(f"✅ SUCCESS! Connected to {account['email_address']}")
                print(f"📧 Found {len(emails)} email(s)")
                
                for i, email in enumerate(emails[:3], 1):
                    print(f"\nEmail {i}:")
                    print(f"  From: {email.get('from', 'Unknown')}")
                    print(f"  Subject: {email.get('subject', 'No Subject')}")
                    print(f"  Date: {email.get('date', 'Unknown')}")
                
                return True
                
            except Exception as e:
                print(f"❌ FAILED to connect to {account['email_address']}")
                print(f"Error: {str(e)}")
                print(f"\n💡 For Gmail, make sure you're using an App Password")
                print(f"   Generate one at: https://myaccount.google.com/apppasswords")
                return False

if __name__ == '__main__':
    if len(sys.argv) > 2:
        # Test with email and password from command line
        test_email_connection(test_email=sys.argv[1], test_password=sys.argv[2])
    elif len(sys.argv) > 1:
        # Test specific account ID
        test_email_connection(account_id=int(sys.argv[1]))
    else:
        # Test first active account
        test_email_connection()
