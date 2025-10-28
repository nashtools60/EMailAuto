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
1. **Email Ingestion**: Monitor mailbox for new emails
2. **Sender Validation**: Whitelist/blacklist management
3. **Content Processing**: Normalize and clean email content
4. **AI Classification**: Categorize emails by topic/intent
5. **Priority Analysis**: Assign urgency levels and sentiment scores
6. **Entity Extraction**: Extract structured data from emails
7. **Draft Generation**: Create response drafts using templates
8. **Human Review**: All drafts require human approval before sending

## Recent Changes
- 2025-10-28: Initial project setup with Flask, database schema design
- 2025-10-28: Integrated AgentMail and OpenAI for email and AI processing

## User Preferences
- None specified yet

## Dependencies
- Flask: Web framework
- PostgreSQL: Database for configurations and drafts
- OpenAI: AI-powered email analysis (requires API key)
- IMAP: Direct email integration (requires email credentials)

## Important Notes
- User declined managed integrations for AgentMail and OpenAI
- App uses direct API integration with email providers via IMAP and OpenAI API keys
- All credentials stored as environment secrets
