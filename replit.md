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
- 2025-10-29: Redesigned Configuration with separate tabs for High Priority, Important, Low Priority, and Subscriptions
- 2025-10-29: Added priority classification to email templates (High Priority, Important, Low Priority)
- 2025-10-29: Created database tables for actions management system (actions, action_templates, action_execution_log)
- 2025-10-29: Renamed blacklist to Subscriptions Whitelist for managing newsletter subscriptions to keep
- 2025-10-29: Implemented complete Actions management tab with priority-based organization
- 2025-10-29: Added action-template linking with many-to-many relationships and execution ordering
- 2025-10-29: Implemented SLA time-based color coding (Green: 0-24h, Amber: 24-48h, Red: >48h)
- 2025-10-29: Created full CRUD API endpoints for actions management and template linking
- 2025-10-29: Fixed subscription validation logic to properly detect and filter unwanted newsletters
- 2025-10-30: Added Email Summaries Report to Dashboard with expandable sections for High Priority and Important emails
- 2025-10-30: Implemented color-coded summary buttons (red gradient for High Priority, orange for Important)
- 2025-10-30: Added SLA status badges and email metadata display in summary cards
- 2025-10-30: Implemented AI-generated bullet-point email summaries using Gemini 2.0 Flash
- 2025-10-30: Added summary column to email_drafts table and generate_email_summary() function in ai_processor.py
- 2025-10-30: Updated email processing workflow to generate 2-4 bullet points per email with key information
- 2025-10-30: Added styled summary display in Email Summaries section with color-coded boxes
- 2025-10-30: **MAJOR OPTIMIZATION**: Combined 4 separate AI calls into 1 call (analyze_email_combined function)
- 2025-10-30: Reduced API usage by 60% - from 5 calls per email to 2 calls (analysis + draft)
- 2025-10-30: Improved email processing speed - can now process 4-5 emails per minute instead of 2
- 2025-10-30: Redesigned Email Summaries with mailbox filter dropdown and one-line email display
- 2025-10-30: Changed email sorting to reverse chronological order (oldest first) in Email Summaries
- 2025-10-30: Removed Sentiment, Category, and Mailbox labels from summary display
- 2025-10-30: Implemented single-line email display: SLA | Date/Time | Sender Email | Subject
- 2025-10-30: Added click-to-expand functionality to display email summaries when clicking on email lines
- 2025-10-30: Fixed sender/recipient email field swap in database insertion
- 2025-10-30: Implemented triaging matrix logic to apply sender whitelist, subject keywords, and body keywords
- 2025-10-30: Priority override system now properly checks configured keywords and upgrades email priority accordingly
- 2025-10-30: Subject keywords like "Urgent", "Deadline", "Critical" now correctly trigger High Priority classification
- 2025-10-30: Changed email summary format from bullet points to narrative paragraphs with highlighted actions
- 2025-10-30: Updated AI prompt to generate 2-3 sentence narrative summaries with clear "Action:" statements
- 2025-10-30: Enhanced summary display with improved typography and action highlighting
- 2025-10-30: Implemented automatic permanent deletion of pure advertising emails from mailbox
- 2025-10-30: Added is_advertisement() function to identify marketing emails not in subscriptions whitelist
- 2025-10-30: Added delete_email() method to EmailService for IMAP-based permanent deletion
- 2025-10-30: Reorganized Review Drafts to match Email Summaries layout with priority sections
- 2025-10-30: Added one-line draft display format: SLA | Date/Time | Sender Email | Subject
- 2025-10-30: Implemented click-to-expand for draft editing with High Priority, Important, and Low Priority sections
- 2025-10-30: Added mailbox filter dropdown to Review Drafts tab
- 2025-10-30: Implemented AI-powered action detection - only creates drafts for emails requiring action
- 2025-10-30: Added action_required field to CombinedEmailAnalysis schema for intelligent draft filtering
- 2025-10-30: Informational emails (newsletters, notifications, FYI messages) now skip draft generation
- 2025-10-30: Processing logs track no_action_required status for informational emails
- 2025-10-30: Updated AI analysis to include attachment information in email summaries
- 2025-10-30: Email summaries now mention number of attachments and file types/names
- 2025-10-30: Added Security Alerts & Warnings category to Email Summaries page
- 2025-10-30: Implemented bulk select and delete functionality for security alerts
- 2025-10-30: Updated AI to classify security-related emails (alerts, warnings, threats, breaches, vulnerabilities)
- 2025-10-30: Added /api/delete-alerts endpoint for bulk deletion of selected security alerts
- 2025-10-30: Created complete Docker-based self-hosted deployment package for beta testing
- 2025-10-30: Built comprehensive installation package with Dockerfile, docker-compose.yml, and environment configuration
- 2025-10-30: Created automated packaging script (create-beta-package.sh) for distribution
- 2025-10-30: Wrote detailed beta installation guide (BETA_INSTALL.md) with troubleshooting
- 2025-10-30: Created comprehensive User Manual (USER_MANUAL.md) with installation, operation, and troubleshooting guides

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
