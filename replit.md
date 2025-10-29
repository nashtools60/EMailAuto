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
3. **Priority-Based Triaging Matrix**: 
   - Three-tier sender whitelists (High Priority, Important, Low Priority)
   - Subject line keyword classification by priority
   - Body content keyword classification by priority
4. **Sender Validation**: Whitelist/blacklist management with categories (Unsubscribe/Permanent Delete)
5. **Content Processing**: Normalize and clean email content
6. **AI Classification**: Categorize emails by topic/intent using Gemini 2.0 Flash
7. **Priority Analysis**: Assign urgency levels and sentiment scores based on triaging rules
8. **Entity Extraction**: Extract structured data from emails
9. **Draft Generation**: Create response drafts using templates
10. **Human Review**: All drafts require human approval before sending
11. **Account Tracking**: Each draft linked to its source email account
12. **Theme Customization**: 8 color schemes including Dark Mode

## Recent Changes
- 2025-10-28: Initial project setup with Flask, database schema design
- 2025-10-28: Integrated Gemini 2.0 Flash for AI processing
- 2025-10-28: Built complete email automation system with web UI
- 2025-10-28: Implemented IMAP email monitoring, AI classification, and draft generation
- 2025-10-28: Added blacklist categorization (Unsubscribe/Permanent Delete)
- 2025-10-28: Implemented multi-account email support with encrypted password storage
- 2025-10-29: Implemented priority-based triaging matrix with three-tier classification
- 2025-10-29: Added subject line and body keyword classification by priority
- 2025-10-29: Added 8 color themes including Dark Mode with proper label visibility

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
- Email domain validation ensures platform/domain matches selected email provider
- Priority-based triaging uses sender whitelists, subject keywords, and body keywords to classify emails into High Priority, Important, and Low Priority categories
- Theme preference saved in browser local storage for persistence across sessions
