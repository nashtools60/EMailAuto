# Email Automation App - Setup Guide

## Quick Start

### Step 1: Configure Email Credentials (Recommended: Environment Secrets)

For better security, store your email credentials as environment secrets:

1. Click on "Secrets" in the Replit sidebar (lock icon)
2. Add these three secrets:
   - `EMAIL_IMAP_SERVER` - Your IMAP server (e.g., `imap.gmail.com`)
   - `EMAIL_USER` - Your email address
   - `EMAIL_PASSWORD` - Your app-specific password

#### Getting an App Password

**Gmail:**
1. Enable 2-factor authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Create an app password for "Mail"
4. Use this password (not your regular Google password)

**Outlook/Office 365:**
- Use your regular password or create an app password at https://account.live.com/proofs/AppPassword

**Yahoo:**
1. Enable 2-factor authentication
2. Go to Account Security → Generate app password
3. Use this password

### Step 2: Gemini API Key

Your Gemini API key is already configured: ✓ `GEMINI_API_KEY`

### Step 3: Configure Email Processing Rules

1. Open the application dashboard
2. Go to the **Configuration** tab
3. Add VIP Senders (Whitelist):
   - Add important email addresses or domains
   - Example: `boss@company.com` or `@importantclient.com`

4. Add Blocked Senders (Blacklist):
   - Add spam or unwanted email addresses
   - Example: `spam@example.com`

### Step 4: Create Email Templates (Optional)

1. Go to the **Templates** tab
2. Click "Create New Template"
3. Fill in:
   - Template name
   - Category (Sales, Support, etc.)
   - Subject template (optional)
   - Body template

### Step 5: Process Emails

1. Go to the **Dashboard** tab
2. Click "Process New Emails"
3. The system will:
   - Fetch unread emails from your inbox
   - Validate senders against your rules
   - Classify and analyze each email with AI
   - Generate draft responses
   - Mark processed emails as read (to avoid duplicates)

### Step 6: Review and Approve Drafts

1. Go to the **Review Drafts** tab
2. For each draft:
   - Review the AI-generated response
   - View the original email
   - See classification, priority, and sentiment
   - Edit the subject or body if needed
   - Click "Approve & Send" or "Reject"

## Alternative Setup (Database Storage)

If you don't want to use environment secrets, you can configure email credentials via the **Settings** tab in the web interface. However, this is less secure and not recommended for production use.

## Security Best Practices

✓ **DO:**
- Use environment secrets for email credentials
- Use app-specific passwords, never your main password
- Enable 2-factor authentication on your email account
- Regularly rotate your app passwords

✗ **DON'T:**
- Store credentials in the database settings (less secure)
- Use your main email password
- Share your API keys or passwords
- Leave sensitive data in code

## Troubleshooting

### "Email credentials not configured"
- Make sure you've added `EMAIL_IMAP_SERVER`, `EMAIL_USER`, and `EMAIL_PASSWORD` as environment secrets
- OR configure them via the Settings tab

### "Connection failed"
- Verify your IMAP server address is correct
- Check that you're using an app password, not your regular password
- Ensure your email provider allows IMAP access (may need to enable in settings)

### "No emails processed"
- Make sure you have unread emails in your inbox
- Check that emails aren't being blocked by your blacklist
- Verify the Gemini API key is working

### Duplicate Drafts
- This has been fixed: emails are now marked as read after processing
- Old unread emails may be reprocessed once; after that, only new emails will be processed

## What Gets Processed

- ✓ Unread emails in your INBOX
- ✗ Read emails (already processed)
- ✗ Emails in other folders (Spam, Trash, etc.)
- ✗ Blacklisted senders (logged but not processed)

## Database Schema

The app uses PostgreSQL with these tables:
- `configurations` - Whitelist/blacklist rules
- `email_templates` - Response templates
- `email_drafts` - AI-generated drafts awaiting review
- `email_processing_log` - Processing history
- `system_settings` - (Optional) Email credentials

## Support

For issues or questions:
1. Check the console logs in the Replit workspace
2. Review the README.md for feature documentation
3. Check the database to verify data is being saved correctly
