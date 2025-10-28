# Email Automation App

## Overview
An intelligent email processing and automation system that monitors incoming emails, classifies them using AI, extracts key information, and generates draft responses for human review.

## Project Architecture
- **Backend**: Python Flask web application
- **Database**: PostgreSQL for storing configurations, templates, and email drafts
- **Email Integration**: AgentMail for receiving and managing emails
- **AI Integration**: OpenAI (via Replit AI Integrations) for classification, sentiment analysis, and entity extraction
- **Frontend**: HTML/JavaScript interface for configuration and draft review

## Key Features
1. **Multi-Account Support**: Process emails from multiple accounts (Gmail, Yahoo, Outlook, iCloud, AOL, etc.)
2. **Email Ingestion**: Monitor mailboxes for new emails across all active accounts
3. **Sender Validation**: Whitelist/blacklist management with categories (Unsubscribe/Permanent Delete)
4. **Content Processing**: Normalize and clean email content
5. **AI Classification**: Categorize emails by topic/intent using Gemini 2.0 Flash
6. **Priority Analysis**: Assign urgency levels and sentiment scores
7. **Entity Extraction**: Extract structured data from emails
8. **Draft Generation**: Create response drafts using templates
9. **Human Review**: All drafts require human approval before sending
10. **Account Tracking**: Each draft linked to its source email account

## Recent Changes
- 2025-10-28: Initial project setup with Flask, database schema design
- 2025-10-28: Integrated Gemini 2.0 Flash for AI processing
- 2025-10-28: Built complete email automation system with web UI
- 2025-10-28: Implemented IMAP email monitoring, AI classification, and draft generation
- 2025-10-28: Added blacklist categorization (Unsubscribe/Permanent Delete)
- 2025-10-28: Implemented multi-account email support with encrypted password storage

## User Preferences
- None specified yet

## Dependencies
- Flask: Web framework
- PostgreSQL: Database for configurations, accounts, and drafts
- Gemini 2.0 Flash: AI-powered email analysis via Google GenAI
- IMAP: Direct email integration via imap-tools library
- Cryptography: Secure password encryption for email accounts

## Important Notes
- Multi-account support allows processing emails from unlimited email providers
- Passwords encrypted using Fernet (symmetric encryption) with PBKDF2 key derivation
- Environment variable credentials (`EMAIL_IMAP_SERVER`, `EMAIL_USER`, `EMAIL_PASSWORD`) automatically migrated to first account on startup
- Email account passwords stored encrypted in database
- Each email draft tracks its source account for proper response handling
- Supports Gmail, Yahoo, Outlook, iCloud, AOL, and custom IMAP servers
