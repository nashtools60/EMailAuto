import os
import re
import html2text
from bs4 import BeautifulSoup
from imap_tools.mailbox import MailBox
from imap_tools.query import AND
from datetime import datetime
from typing import List, Dict, Optional
import email
from email.header import decode_header

class EmailService:
    """Service for email ingestion and processing"""
    
    def __init__(self, imap_server: str, email_user: str, email_password: str):
        self.imap_server = imap_server
        self.email_user = email_user
        self.email_password = email_password
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
    
    def connect(self):
        """Connect to the IMAP mailbox"""
        try:
            return MailBox(self.imap_server).login(self.email_user, self.email_password)
        except Exception as e:
            print(f"Error connecting to mailbox: {e}")
            raise
    
    def fetch_new_emails(self, folder: str = "INBOX", limit: int = 10) -> List[Dict]:
        """
        Fetch new unread emails from the specified folder
        """
        emails = []
        try:
            with self.connect() as mailbox:
                mailbox.folder.set(folder)
                
                # Fetch unread emails
                for msg in mailbox.fetch(AND(seen=False), limit=limit, reverse=True):
                    email_data = {
                        'id': msg.uid,
                        'subject': msg.subject or '(No Subject)',
                        'sender': msg.from_,
                        'sender_email': self._extract_email(msg.from_),
                        'recipient': msg.to,
                        'date': msg.date,
                        'body_html': msg.html,
                        'body_text': msg.text,
                        'has_attachments': len(msg.attachments) > 0,
                        'attachments': [
                            {
                                'filename': att.filename,
                                'content_type': att.content_type,
                                'size': len(att.payload)
                            } for att in msg.attachments
                        ] if msg.attachments else []
                    }
                    emails.append(email_data)
            
            return emails
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def _extract_email(self, from_field: str) -> str:
        """Extract email address from From field"""
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_field)
        return match.group(0) if match else from_field
    
    def validate_sender(self, sender_email: str, whitelist: List[str], subscriptions_whitelist: List[str]) -> str:
        """
        Validate sender against whitelist and subscriptions whitelist
        Returns: 'whitelisted', 'subscription_not_whitelisted', or 'unknown'
        """
        sender_lower = sender_email.lower()
        sender_domain = sender_email.split('@')[-1].lower() if '@' in sender_email else ''
        
        # Check whitelist (high priority senders)
        for allowed in whitelist:
            if allowed.lower() in sender_lower or allowed.lower() == sender_domain:
                return 'whitelisted'
        
        # Detect subscription/newsletter emails using common patterns
        subscription_indicators = [
            'newsletter', 'noreply', 'no-reply', 'notifications', 
            'updates', 'mailer', 'news', 'marketing', 'promo',
            'automated', 'digest', 'subscriptions', 'campaigns'
        ]
        
        is_subscription = any(indicator in sender_lower for indicator in subscription_indicators)
        
        if is_subscription:
            # Check if this subscription is whitelisted (allowed to keep)
            for allowed_sub in subscriptions_whitelist:
                if allowed_sub.lower() in sender_lower or allowed_sub.lower() == sender_domain:
                    return 'unknown'  # Process normally (it's a wanted subscription)
            
            # Subscription not in whitelist - should be unsubscribed/deleted
            return 'subscription_not_whitelisted'
        
        # Not a subscription, process normally
        return 'unknown'
    
    def normalize_content(self, body_html: str, body_text: str) -> str:
        """
        Normalize email content by removing extraneous data
        - Remove HTML formatting
        - Remove disclaimers and signatures
        - Remove previous reply chains
        - Extract core message
        """
        # Prefer text version if available, otherwise convert HTML
        if body_text:
            content = body_text
        elif body_html:
            content = self.html_converter.handle(body_html)
        else:
            return ""
        
        # Remove common email artifacts
        content = self._remove_reply_chains(content)
        content = self._remove_signatures(content)
        content = self._clean_whitespace(content)
        
        return content
    
    def _remove_reply_chains(self, content: str) -> str:
        """Remove previous email replies from the content"""
        # Common reply indicators
        reply_patterns = [
            r'On .+ wrote:.*$',
            r'From:.*?Sent:.*?To:.*?Subject:.*$',
            r'-----Original Message-----.*$',
            r'________________________________.*$',
        ]
        
        for pattern in reply_patterns:
            content = re.split(pattern, content, flags=re.MULTILINE | re.DOTALL)[0]
        
        return content.strip()
    
    def _remove_signatures(self, content: str) -> str:
        """Remove email signatures"""
        # Common signature patterns
        signature_markers = ['--', '___', 'Best regards', 'Sincerely', 'Thanks,', 'Regards,']
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if any(marker in line for marker in signature_markers):
                # Keep content before signature
                return '\n'.join(lines[:i]).strip()
        
        return content
    
    def _clean_whitespace(self, content: str) -> str:
        """Clean up excessive whitespace"""
        # Remove multiple blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in content.split('\n')]
        return '\n'.join(lines).strip()
    
    def mark_as_read(self, email_id: str):
        """Mark an email as read"""
        try:
            with self.connect() as mailbox:
                mailbox.flag(email_id, '\\Seen', True)
        except Exception as e:
            print(f"Error marking email as read: {e}")
    
    def delete_email(self, email_id: str):
        """
        Permanently delete an email from the mailbox
        Marks it as deleted and expunges it from the server
        """
        try:
            with self.connect() as mailbox:
                # Mark email as deleted
                mailbox.delete([email_id])
                # Expunge to permanently remove
                mailbox.expunge()
                print(f"Permanently deleted email ID: {email_id}")
                return True
        except Exception as e:
            print(f"Error deleting email {email_id}: {e}")
            return False
    
    def send_draft_email(self, to_email: str, subject: str, body: str):
        """
        This is a placeholder for sending emails.
        In production, you would use SMTP or an email service API
        """
        print(f"Draft email to {to_email}:")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        # TODO: Implement actual email sending via SMTP or email service
