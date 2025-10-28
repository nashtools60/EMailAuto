# Email Automation App

A parameterized, automatic email processing agent with AI-powered classification, sentiment analysis, and draft response generation.

## Features

### Email Ingestion & Pre-processing
- **Monitor Mailbox**: Continuously check for new emails via IMAP
- **Sender Validation**: Whitelist (VIP senders) and blacklist management
- **Content Normalization**: Remove HTML formatting, disclaimers, and reply chains
- **Attachment Detection**: Identify and track email attachments

### AI Processing (Powered by Gemini 2.0 Flash)
- **Email Classification**: Categorize emails (Sales Inquiry, Technical Support, Invoice/Billing, HR Request, etc.)
- **Priority Analysis**: Assign urgency levels (P0-Critical, P1-High, P2-Medium, P3-Normal)
- **Sentiment Analysis**: Detect sentiment (Positive, Neutral, Negative)
- **Entity Extraction**: Extract structured data (customer names, order IDs, amounts, dates, etc.)
- **Draft Generation**: AI-generated response drafts based on classification and templates

### Human-in-the-Loop
All generated email responses remain in draft status for human review and approval before sending.

## Setup Instructions

### Quick Setup (5 minutes)

See the detailed [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete instructions.

**Required Configuration:**

1. **Email Credentials** (Store as Environment Secrets - Recommended):
   - `EMAIL_IMAP_SERVER` - IMAP server (e.g., `imap.gmail.com`)
   - `EMAIL_USER` - Your email address
   - `EMAIL_PASSWORD` - App-specific password (NOT your main password)

2. **Gemini API Key** (Already configured):
   - `GEMINI_API_KEY` - For AI processing

**Getting Started:**
- See SETUP_GUIDE.md for step-by-step instructions
- Use app-specific passwords for security
- Configure whitelist/blacklist in the Configuration tab

### 2. Configure Email Processing Rules

**Whitelist (VIP Senders)**:
- Add email addresses or domains for high-priority senders
- Examples: `ceo@company.com`, `@importantclient.com`

**Blacklist (Blocked Senders)**:
- Add email addresses or domains to automatically reject
- Choose a category for each blocked sender:
  - **Unsubscribe**: For legitimate senders you want to unsubscribe from
  - **Permanent Delete**: For spam or malicious senders to block permanently
- Examples: `spam@example.com`, `@spammydomain.com`
- Category badges display next to each entry for easy identification

### 3. Create Email Templates (Optional)
Create response templates for common email categories:
- Sales Inquiry responses
- Support ticket acknowledgments
- Billing inquiry templates
- General inquiry responses

## How to Use

### Process Emails
1. Click **"Process New Emails"** on the Dashboard
2. The system will:
   - Fetch unread emails from your inbox
   - Validate senders against whitelist/blacklist
   - Normalize and clean email content
   - Use AI to classify, analyze priority/sentiment, and extract entities
   - Generate draft responses

### Review Drafts
1. Go to the **Review Drafts** tab
2. For each draft you can:
   - View the original email
   - See AI classification, priority, and sentiment
   - Edit the subject and body
   - **Approve** to send (implementation pending)
   - **Reject** to discard
   - **Update** to save changes

### Monitor Progress
The **Dashboard** shows:
- Number of pending drafts awaiting review
- Number of approved drafts
- Total emails processed
- Breakdown by email category

## Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **AI**: Google Gemini 2.0 Flash
- **Email**: IMAP protocol via imap-tools
- **Frontend**: HTML, CSS, JavaScript

## API Endpoints

- `GET /api/stats` - Get processing statistics
- `POST /api/process-emails` - Trigger email processing
- `GET /api/drafts` - Get pending drafts
- `PUT /api/drafts/:id` - Update/approve/reject draft
- `GET/POST /api/config` - Manage whitelist/blacklist
- `GET/POST /api/templates` - Manage email templates
- `GET/POST /api/settings` - Manage system settings

## Database Schema

### Tables
- **configurations**: Whitelist/blacklist entries
- **email_templates**: Reusable response templates
- **email_drafts**: AI-generated drafts awaiting review
- **email_processing_log**: Processing history and analytics
- **system_settings**: IMAP credentials and configuration

## Security Notes

⚠️ **IMPORTANT**: This application currently has **no authentication or authorization**. All API endpoints are publicly accessible.

**Safe for:**
- Personal use in private Replit workspace
- Development and testing environments
- Internal networks with trusted users only

**NOT safe for:**
- Public deployment without adding authentication
- Production use with sensitive emails
- Multi-user environments without access control

**See SECURITY.md for:**
- Detailed security analysis
- How to add authentication
- Production deployment guidelines
- Best practices and recommendations

**Current Security Features:**
- Credentials stored in environment secrets (recommended)
- Email passwords redacted from API responses
- App-specific password usage (never main passwords)
- Database credentials managed by Replit PostgreSQL
- Gemini API key in environment secrets

## Future Enhancements

- Actual email sending via SMTP
- Scheduled automatic email checking
- Advanced attachment processing (OCR, invoice scanning)
- Email thread context (pull previous 2 messages)
- CRM/ERP integration for data validation
- Multi-user support with role-based access
- Email analytics and reporting
- Custom classification categories
- Template variable substitution

## License

MIT License
