# 📧 Email Automation App - User Manual

**Version 1.0** | Self-Hosted Email Processing Platform

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [First-Time Setup](#first-time-setup)
5. [Daily Operations](#daily-operations)
6. [Features Guide](#features-guide)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [FAQ](#faq)

---

## Introduction

### What is Email Automation App?

Email Automation App is an intelligent email processing system that uses artificial intelligence to help you manage your inbox more efficiently. It monitors your email accounts, automatically categorizes incoming messages, determines priority levels, and generates draft responses for your review.

### Key Benefits

✅ **Save Time** - Process emails 10x faster with AI assistance  
✅ **Never Miss Important Emails** - Automatic priority classification  
✅ **Consistent Responses** - Template-based draft generation  
✅ **Multi-Account Management** - Handle Gmail, Yahoo, Outlook, and more  
✅ **Security First** - Self-hosted on your infrastructure, you control your data  
✅ **Human Oversight** - All drafts require your approval before sending

### How It Works

```
Your Email Accounts
        ↓
Monitor for New Emails (IMAP)
        ↓
AI Analysis (Classification, Priority, Sentiment)
        ↓
Apply Your Rules (Whitelists, Keywords)
        ↓
Generate Draft Response (If Action Required)
        ↓
Present for Your Review
        ↓
You Approve or Edit
```

---

## System Requirements

### Hardware Requirements

**Minimum**:
- CPU: 1 core / 2 GHz
- RAM: 2 GB
- Storage: 5 GB available space
- Network: Stable internet connection

**Recommended**:
- CPU: 2+ cores / 2.5 GHz
- RAM: 4 GB
- Storage: 10 GB available space
- Network: Broadband connection

### Software Requirements

**Required**:
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (usually included with Docker Desktop)

**Operating System Support**:
- ✅ Windows 10/11 (Pro, Enterprise, or Education)
- ✅ macOS 10.15 (Catalina) or later
- ✅ Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+, or similar)

### Internet Services Required

- **Google Gemini API Account** (Free tier available)
  - Free: 50 requests/day, 10 requests/minute
  - Paid: Higher limits available
  - Sign up: https://aistudio.google.com/app/apikey

- **Email Account(s)**
  - Supports: Gmail, Yahoo, Outlook, iCloud, AOL, custom IMAP servers
  - Requires: IMAP access enabled
  - Security: App-specific passwords required (not your main password)

---

## Installation

### Step 1: Install Docker

#### Windows

1. Download **Docker Desktop** from https://www.docker.com/products/docker-desktop/
2. Run the installer
3. Follow the installation wizard
4. **Important**: Enable WSL 2 during installation if prompted
5. Restart your computer when prompted
6. Launch Docker Desktop
7. Wait for Docker to start (you'll see a green icon in the system tray)

#### macOS

1. Download **Docker Desktop** from https://www.docker.com/products/docker-desktop/
2. Open the `.dmg` file
3. Drag Docker to your Applications folder
4. Launch Docker from Applications
5. Grant necessary permissions when prompted
6. Wait for Docker to start (you'll see a whale icon in the menu bar)

#### Linux (Ubuntu/Debian)

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group (avoid using sudo)
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect

# Verify installation
docker --version
docker compose version
```

### Step 2: Verify Docker Installation

Open a terminal/command prompt and run:

```bash
docker --version
docker compose version
```

You should see version numbers displayed (e.g., `Docker version 24.0.0`).

### Step 3: Extract Email Automation Package

**Windows**:
1. Right-click `email-automation-beta-v1.0.tar.gz`
2. Extract to a folder (e.g., `C:\EmailAutomation\`)
3. Open Command Prompt or PowerShell
4. Navigate to the folder: `cd C:\EmailAutomation`

**macOS/Linux**:
```bash
# Create installation directory
mkdir ~/email-automation
cd ~/email-automation

# Extract package
tar -xzf /path/to/email-automation-beta-v1.0.tar.gz

# Verify extraction
ls -la
```

You should see files like `docker-compose.yml`, `.env.example`, `Dockerfile`, etc.

### Step 4: Configure Environment

1. **Copy the configuration template**:

   **Windows (Command Prompt)**:
   ```cmd
   copy .env.example .env
   ```

   **Windows (PowerShell)**:
   ```powershell
   Copy-Item .env.example .env
   ```

   **macOS/Linux**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file**:

   **Windows**: Right-click `.env` → Open with Notepad  
   **macOS**: Open with TextEdit  
   **Linux**: `nano .env` or use your preferred editor

3. **Required: Set Gemini API Key**:

   ```env
   GEMINI_API_KEY=your-actual-api-key-here
   ```

   **How to get a Gemini API key**:
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with your Google account
   - Click **"Create API Key"**
   - Copy the key (starts with `AIza...`)
   - Paste it into your `.env` file

4. **Recommended: Change Database Password**:

   ```env
   PGPASSWORD=your-secure-password-here
   ```

   Choose a strong password (mix of letters, numbers, symbols).

5. **Recommended: Set Secret Key**:

   Generate a random secret key:

   **Windows (PowerShell)**:
   ```powershell
   -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
   ```

   **macOS/Linux**:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

   Copy the output and paste into `.env`:
   ```env
   SECRET_KEY=paste-generated-key-here
   ```

6. **Optional: Pre-configure First Email Account**:

   If you want to add an email account during installation, uncomment and fill in:

   ```env
   EMAIL_PROVIDER=gmail
   EMAIL_USER=youremail@gmail.com
   EMAIL_PASSWORD=your-app-specific-password
   EMAIL_IMAP_SERVER=imap.gmail.com
   EMAIL_IMAP_PORT=993
   ```

   **Note**: You can also add email accounts later via the web interface.

7. **Save and close** the `.env` file.

### Step 5: Start the Application

Open a terminal/command prompt in your installation folder and run:

```bash
docker compose up -d
```

**What this does**:
- Downloads required Docker images (~500 MB, first time only)
- Builds the application container
- Starts PostgreSQL database
- Starts the Email Automation App
- Runs in the background (`-d` flag)

**First startup takes 2-3 minutes**. Subsequent starts are much faster (~10 seconds).

**Monitor startup progress**:
```bash
docker compose logs -f
```

Press `Ctrl+C` to stop viewing logs (the app keeps running).

### Step 6: Access the Application

1. Open your web browser
2. Navigate to: **http://localhost:5000**
3. You should see the **Email Automation Dashboard**

**If you see a connection error**, wait 30 seconds and refresh - the app may still be starting up.

---

## First-Time Setup

### 1. Add Your First Email Account

**Gmail Example**:

1. **Generate App Password** (do NOT use your regular Gmail password):
   - Go to: https://myaccount.google.com/apppasswords
   - Sign in to your Google account
   - If you don't see this option, enable **2-Step Verification** first
   - Select App: **Mail**
   - Select Device: **Other** (type "Email Automation")
   - Click **Generate**
   - Copy the 16-character password (remove spaces)

2. **Add Account in App**:
   - Click the **"Email Accounts"** tab
   - Click **"+ Add Email Account"**
   - Fill in the form:
     - **Account Name**: `My Gmail` (or any name you prefer)
     - **Email Provider**: Select **Gmail** from dropdown
     - **Email Address**: `youremail@gmail.com`
     - **Password**: Paste the 16-character app password
     - **IMAP Server**: Auto-filled as `imap.gmail.com`
     - **IMAP Port**: Auto-filled as `993`
   - Click **"Add Account"**

3. **Verify Connection**:
   - You should see your account listed
   - Status should show as active

**Other Email Providers**:

| Provider | IMAP Server | Port |
|----------|-------------|------|
| **Yahoo** | imap.mail.yahoo.com | 993 |
| **Outlook/Hotmail** | outlook.office365.com | 993 |
| **iCloud** | imap.mail.me.com | 993 |
| **AOL** | imap.aol.com | 993 |
| **Custom** | Ask your IT department | Usually 993 |

### 2. Configure Priority Rules

Priority rules help the AI categorize your emails correctly.

#### High Priority Senders

Add email addresses or domains of your most important contacts:

1. Go to **Configuration** → **High Priority** tab
2. Under **Sender Whitelist**, add emails like:
   - `boss@company.com`
   - `ceo@company.com`
   - `@importantclient.com` (entire domain)
3. Click **"Save Configuration"**

#### High Priority Keywords

Add keywords that indicate urgent emails:

1. Under **Subject Keywords**, add terms like:
   - `Urgent`
   - `Critical`
   - `Deadline`
   - `ASAP`
   - `Emergency`
2. Under **Body Keywords**, add phrases like:
   - `immediate attention`
   - `by end of day`
   - `time sensitive`
3. Click **"Save Configuration"**

**How it works**: If an email subject/body contains these keywords, it's automatically classified as High Priority, even if the sender isn't whitelisted.

#### Important Senders (P2 Priority)

1. Go to **Configuration** → **Important** tab
2. Add regular business contacts
3. Add keywords like:
   - `Important`
   - `Action Required`
   - `Please Review`

#### Subscriptions Whitelist

Add newsletters and subscriptions you want to KEEP:

1. Go to **Configuration** → **Subscriptions** tab
2. Add sender emails/domains like:
   - `newsletter@industry-news.com`
   - `@linkedin.com`
   - `@medium.com`
3. Click **"Save Configuration"**

**Important**: Emails from subscription-like senders NOT in this list will be automatically deleted if they're pure marketing/advertising.

### 3. Create Response Templates (Optional)

Templates help the AI generate better draft responses.

1. Go to the **Templates** tab
2. Click **"+ Add Template"**
3. Fill in:
   - **Template Name**: `Sales Inquiry Response`
   - **Category**: `Sales Inquiry`
   - **Priority**: `High Priority` (P0-P1)
   - **Subject Template**: `Re: Your inquiry about [product/service]`
   - **Body Template**:
     ```
     Thank you for your interest in our [product/service].
     
     I'd be happy to provide more information about [specific topic mentioned].
     
     [Add relevant details here]
     
     Would you be available for a call this week to discuss further?
     
     Best regards,
     [Your Name]
     ```
4. Click **"Create Template"**

Create templates for common scenarios:
- Sales inquiries
- Support requests
- Meeting confirmations
- General information requests

### 4. Choose Your Theme (Optional)

1. Go to the **Settings** tab
2. Select a theme from the dropdown:
   - Default Blue (Professional)
   - Ocean Teal (Calm)
   - Forest Green (Natural)
   - Sunset Purple (Creative)
   - Rose Pink (Warm)
   - Amber Gold (Energetic)
   - Slate Gray (Minimal)
   - **Dark Mode** (Low light)
3. Your preference is saved automatically

---

## Daily Operations

### Processing New Emails

**How Often**: Run this whenever you want to check for new emails (daily, hourly, etc.)

1. Go to the **Dashboard** tab
2. Click **"Process New Emails"**
3. Wait while the system:
   - Connects to your email accounts
   - Fetches unread emails
   - Analyzes each email with AI
   - Generates drafts for emails requiring action
   - Creates summaries for all emails
4. You'll see a status message: "Successfully processed X emails"

**Processing Time**:
- ~2-3 seconds per email
- 10 emails ≈ 30 seconds
- 50 emails ≈ 2-3 minutes

**What Happens to Processed Emails**:
- Marked as "read" in your mailbox (won't be processed again)
- Stored in the database with full content and analysis
- Pure advertising emails (not in subscriptions whitelist) are permanently deleted from your mailbox
- Informational emails (newsletters, notifications) are logged but no draft is created
- Emails requiring action get draft responses generated

### Reviewing Email Summaries

**Purpose**: Quickly scan all incoming emails without opening them

1. Go to the **Dashboard** tab
2. Scroll to **"Email Summaries by Priority"**
3. Use the **Mailbox** filter if you have multiple accounts
4. Expand sections:
   - 🔴 **High Priority Emails** (P0-P1)
   - 🟠 **Important Emails** (P2)
   - ⚠️ **Security Alerts & Warnings**

**Understanding Email Lines**:

```
[SLA Badge] | Date/Time | sender@example.com | Email Subject
```

**SLA Status Colors**:
- 🟢 **Green** (< 24h): Fresh, recently received
- 🟠 **Amber** (24-48h): Getting older, should address soon
- 🔴 **Red** (> 48h): Old, needs immediate attention

**Click on any email line** to expand and see:
- Full AI-generated summary (2-3 sentence narrative)
- Action items highlighted (if any)
- Attachment information (if present)

**Example**:
```
🟢 < 24h | 10/30/2025 2:45 PM | john@client.com | Proposal Review Request

[Click to expand]

This is a request from John Smith at ClientCo to review their 
Q4 proposal. The email includes 2 attachments: proposal.pdf 
and budget.xlsx. They need feedback by Friday. 
Action: Review attached proposal and provide feedback by EOW.
```

### Reviewing and Editing Drafts

**Purpose**: Approve, edit, or reject AI-generated email responses

1. Go to the **Review Drafts** tab
2. Filter by mailbox if needed
3. Expand priority sections (High Priority, Important, Low Priority)
4. **Click on any email line** to expand the full draft editor

**Draft Editor Sections**:

**Original Email**:
- From/To/Date
- Subject
- Body content

**AI Analysis**:
- **Classification**: Type of email (Sales Inquiry, Support, etc.)
- **Sentiment**: Positive, Neutral, Negative, Urgent
- **Priority**: P0 (Critical) → P3 (Low)
- **Summary**: Brief overview with action items

**Draft Response** (Editable):
- **Subject**: Pre-filled (you can edit)
- **Body**: AI-generated response (you can edit)

**Actions**:

1. **Approve** ✅
   - Marks draft as approved
   - *Note: Actual sending not yet implemented - this is for workflow tracking*
   - Future versions will send the email automatically

2. **Update** 💾
   - Saves your edits to the draft
   - Use this to refine the response before approving
   - Can update multiple times

3. **Delete** 🗑️
   - Permanently removes the draft
   - Use for emails that don't need a response after all

**Workflow Example**:

1. Expand draft
2. Read AI-generated response
3. Edit if needed (fix tone, add details, personalize)
4. Click **"Update"** to save changes
5. Click **"Approve"** when ready
6. Draft moves to approved status

**Pro Tip**: The AI drafts are starting points. Always review and personalize before approving, especially for important emails.

### Managing Security Alerts

**Purpose**: Quickly triage and delete security-related notifications

1. Go to **Dashboard** → **Email Summaries**
2. Expand **⚠️ Security Alerts & Warnings** section
3. Review security-related emails (password resets, login alerts, etc.)

**Bulk Delete**:
1. Check the boxes next to alerts you want to remove
2. Click **"Delete Selected"** button
3. Confirm deletion
4. Selected alerts are permanently removed

**When to use**:
- False alarm security notifications
- Expired security alerts
- Login confirmations from recognized devices
- Routine security updates

**When NOT to delete**:
- Unexpected password reset requests (could indicate compromise)
- Unknown device login alerts
- Suspicious activity notifications

---

## Features Guide

### Email Account Management

**Add Multiple Accounts**:
- Support for unlimited email accounts
- Each account processed separately
- Drafts linked to source account for proper reply routing

**Account Status**:
- **Active**: Account is being monitored
- **Error**: Connection issue (check password, IMAP settings)

**Edit Account**:
- Update password (if you changed app password)
- Modify IMAP settings
- Rename account

**Remove Account**:
- Stops monitoring the account
- Existing drafts remain in the system
- Can re-add later if needed

### Priority Classification System

**Automatic Priority Assignment**:

The system uses a **triaging matrix** with multiple rules:

1. **Sender Whitelist** (Highest priority)
   - If sender is in High Priority whitelist → P0/P1
   - If sender is in Important whitelist → P2
   - If sender is in Low Priority whitelist → P3

2. **Subject Keywords**
   - Contains "Urgent", "Critical" → Upgraded to P0/P1
   - Contains "Important" → Upgraded to P2

3. **Body Keywords**
   - Contains urgent phrases → Priority upgrade

4. **AI Classification**
   - Security alerts → Special category
   - Based on email content and context

**Priority Levels**:

| Level | Label | SLA | Use Case |
|-------|-------|-----|----------|
| **P0** | Critical | < 4h | System outages, legal issues, executive requests |
| **P1** | High | < 24h | Sales opportunities, customer complaints, deadlines |
| **P2** | Important | < 48h | Regular business, meeting requests, project updates |
| **P3** | Low | < 7d | Newsletters, FYI emails, non-urgent communication |

### AI-Powered Analysis

**What the AI Analyzes**:

1. **Classification** (15+ categories):
   - Sales Inquiry
   - Technical Support
   - Invoice/Billing
   - HR Request
   - Partnership Proposal
   - Customer Complaint
   - General Inquiry
   - Newsletter/Marketing
   - Security Alert/Warning
   - And more...

2. **Sentiment**:
   - **Positive**: Happy, satisfied, grateful
   - **Neutral**: Informational, factual
   - **Negative**: Complaint, frustrated, angry
   - **Urgent**: Time-sensitive, demanding attention

3. **Entity Extraction**:
   - Customer names
   - Company names
   - Order IDs / Reference numbers
   - Dates and deadlines
   - Monetary amounts
   - Product/service mentions

4. **Action Detection**:
   - **Action Required**: Email needs a response
   - **No Action Required**: Informational only (newsletter, notification, FYI)

5. **Summary Generation**:
   - 2-3 sentence narrative summary
   - Highlights key information
   - Mentions action items
   - Notes attachments if present

**API Usage**:
- Free Tier: 50 requests/day, 10 requests/minute
- Each email = 2 API calls (analysis + draft)
- Can process ~25 emails/day on free tier
- Paid tier available for higher volume

### Template System

**How Templates Work**:

1. You create templates for common email categories
2. AI uses template as a framework when generating drafts
3. AI fills in specific details from the original email
4. Result: Consistent, professional responses

**Template Variables** (Future feature):
- `[customer_name]` - Extracted from email
- `[order_id]` - Extracted order/reference number
- `[date]` - Current date or extracted deadline
- `[product]` - Product/service mentioned

**Template Priority Matching**:
- High Priority templates used for P0/P1 emails
- Important templates used for P2 emails
- Low Priority templates used for P3 emails

### Actions System

**Purpose**: Automate sequences of operations for specific email types

**Example Actions**:
- "Forward to Support Team" → Category: Technical Support
- "Add to CRM" → Category: Sales Inquiry
- "Schedule Follow-up" → Priority: High
- "Archive After Review" → Category: Newsletter

**How to Configure** (Advanced):
1. Go to **Actions** tab
2. Create action with name, description, category, priority
3. Link to templates
4. Set execution order
5. System will suggest actions for matching emails

*Note: Full action automation is a premium feature (future enhancement)*

### Subscriptions Management

**Auto-Delete Marketing Emails**:

The system automatically identifies pure advertising emails (promotions, spam, marketing) that are:
- NOT in your Subscriptions Whitelist
- Clearly promotional in nature
- Not requiring any action

**These are permanently deleted from your mailbox** to keep your inbox clean.

**To Keep a Subscription**:
1. Add sender to **Subscriptions Whitelist**
2. Examples: LinkedIn newsletters, industry updates, Medium digests
3. These will be logged but not deleted

**To Stop a Subscription**:
1. Don't add to whitelist
2. System will auto-delete on next processing
3. Or manually unsubscribe before processing

### Theme Customization

**8 Professional Themes**:

1. **Default Blue**: Professional, corporate
2. **Ocean Teal**: Calm, soothing
3. **Forest Green**: Natural, eco-friendly
4. **Sunset Purple**: Creative, modern
5. **Rose Pink**: Warm, approachable
6. **Amber Gold**: Energetic, enthusiastic
7. **Slate Gray**: Minimal, sleek
8. **Dark Mode**: Low light, WCAG compliant

**Saved Automatically**: Theme preference stored in browser, persists across sessions

---

## Advanced Configuration

### Email Processing Schedule

**Manual Processing** (Current):
- Click "Process New Emails" when you want to check
- On-demand processing
- You control when emails are fetched

**Automated Processing** (Future feature):
- Set schedule: hourly, every 4 hours, daily, etc.
- Background processing
- Will require additional setup

### Database Backup

**Important**: Your email data is stored in a PostgreSQL database running in Docker.

**Backup Your Data**:

```bash
# Create backup
docker compose exec postgres pg_dump -U emailapp emailautomation > backup_$(date +%Y%m%d).sql

# Restore from backup (if needed)
cat backup_20251030.sql | docker compose exec -T postgres psql -U emailapp emailautomation
```

**Backup Schedule Recommendation**:
- Daily: If processing important business emails
- Weekly: For personal use
- Before Updates: Always backup before updating to new version

### Performance Tuning

**For High Email Volume**:

Edit `docker-compose.yml` to increase resources:

```yaml
app:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
```

Then restart:
```bash
docker compose down
docker compose up -d
```

### Multi-Device Access

**Access from Other Devices on Your Network**:

1. Find your computer's local IP address:

   **Windows**: `ipconfig` (look for IPv4 Address)  
   **macOS**: System Preferences → Network  
   **Linux**: `ip addr show`

2. Edit `docker-compose.yml`:
   ```yaml
   app:
     ports:
       - "0.0.0.0:5000:5000"  # Listen on all interfaces
   ```

3. Restart:
   ```bash
   docker compose restart app
   ```

4. Access from other devices: `http://YOUR-IP:5000`
   - Example: `http://192.168.1.100:5000`

**Security Warning**: This exposes the app to your local network. Only use on trusted networks.

### Custom IMAP Configuration

For email providers not in the dropdown:

1. Select **"Custom IMAP Server"** as provider
2. Fill in manually:
   - **IMAP Server**: Ask your IT department or email provider
   - **IMAP Port**: Usually 993 (SSL/TLS)
3. **Common Settings**:
   - SSL/TLS: Enabled (port 993)
   - STARTTLS: Alternative (port 143, then upgrade)

### Data Retention

**Emails are stored indefinitely** in the database until you delete them.

**To Clear Old Data**:

```bash
# Connect to database
docker compose exec postgres psql -U emailapp emailautomation

# Delete old drafts (example: older than 30 days)
DELETE FROM email_drafts WHERE created_at < NOW() - INTERVAL '30 days';

# Delete old processing logs
DELETE FROM email_processing_log WHERE processed_at < NOW() - INTERVAL '90 days';

# Exit
\q
```

---

## Troubleshooting

### Installation Issues

**Problem**: Docker Desktop won't start (Windows)

**Solution**:
1. Enable WSL 2: Open PowerShell as Admin, run:
   ```powershell
   wsl --install
   ```
2. Restart computer
3. Launch Docker Desktop again

**Problem**: "Cannot connect to Docker daemon"

**Solution**:
- **Windows/Mac**: Make sure Docker Desktop is running (check system tray/menu bar)
- **Linux**: Start Docker service:
  ```bash
  sudo systemctl start docker
  ```

**Problem**: Port 5000 already in use

**Solution**:
1. Edit `docker-compose.yml`
2. Change port mapping:
   ```yaml
   ports:
     - "8080:5000"  # Use port 8080 instead
   ```
3. Restart: `docker compose up -d`
4. Access at: http://localhost:8080

### Email Connection Issues

**Problem**: "Authentication failed" (Gmail)

**Solution**:
1. Verify you're using an **App Password**, NOT your regular password
2. Check that 2-Factor Authentication is enabled
3. Generate a new App Password: https://myaccount.google.com/apppasswords
4. Remove spaces from the app password
5. Update in Email Accounts tab

**Problem**: "Connection timed out" or "Cannot connect to IMAP server"

**Solution**:
1. Check your internet connection
2. Verify IMAP is enabled in your email account settings:
   - **Gmail**: Settings → Forwarding and POP/IMAP → Enable IMAP
   - **Yahoo**: Settings → More Settings → Mailboxes → Enable IMAP
   - **Outlook**: Already enabled by default
3. Check firewall isn't blocking port 993
4. Try from a different network (some corporate networks block IMAP)

**Problem**: "SSL Certificate Verification Failed"

**Solution**:
- Usually a temporary server issue
- Wait 15 minutes and try again
- Check email provider's status page

### Processing Issues

**Problem**: "Gemini API quota exceeded"

**Solution**:
- Free tier: 50 requests/day, 10 requests/minute
- Wait until quota resets (next day)
- Or upgrade to paid tier at https://ai.google.dev/pricing
- Each email = 2 API calls, so you can process ~25 emails/day free

**Problem**: Emails not being processed

**Solution**:
1. Check that emails are marked as "unread" in your mailbox
2. Verify email account is connected (Email Accounts tab)
3. Check logs:
   ```bash
   docker compose logs app | tail -50
   ```
4. Look for error messages

**Problem**: Drafts not generated for some emails

**Explanation**: This is expected behavior for:
- Newsletters and informational emails (no action required)
- Automated notifications
- FYI emails
- The system only creates drafts for emails that need responses

### Performance Issues

**Problem**: Processing is very slow

**Solution**:
1. Check your internet speed (AI analysis requires API calls)
2. Process smaller batches (10-20 emails at a time)
3. Increase container resources (see Advanced Configuration)
4. Check if other applications are using bandwidth

**Problem**: Web interface is slow or unresponsive

**Solution**:
1. Close and reopen browser
2. Clear browser cache
3. Try a different browser (Chrome, Firefox, Safari)
4. Restart the application:
   ```bash
   docker compose restart app
   ```

### Database Issues

**Problem**: "Database connection error"

**Solution**:
1. Check if database is running:
   ```bash
   docker compose ps
   ```
2. If `postgres` is unhealthy, restart it:
   ```bash
   docker compose restart postgres
   ```
3. Wait 10 seconds, then restart app:
   ```bash
   docker compose restart app
   ```

**Problem**: Lost all data after restart

**Cause**: Likely ran `docker compose down -v` (the `-v` flag deletes volumes including database)

**Prevention**:
- Use `docker compose stop` for temporary shutdown
- Use `docker compose down` for shutdown (keeps data)
- NEVER use `docker compose down -v` unless you want to delete everything

**Recovery**: Restore from backup (if you have one):
```bash
cat backup.sql | docker compose exec -T postgres psql -U emailapp emailautomation
```

### Common Error Messages

**"Error: Failed to mark email as read"**
- Email account lost connection
- Re-authenticate in Email Accounts tab

**"Error: Template not found"**
- Create templates in Templates tab
- System works without templates but drafts may be less consistent

**"Warning: No action required, draft not created"**
- This is normal for informational emails
- Not an error, just a notification

**"Error: Attachment too large to process"**
- Attachments >25MB may cause issues
- AI still processes the email text
- Attachment info mentioned in summary

---

## Best Practices

### Email Processing Workflow

**Recommended Daily Routine**:

1. **Morning** (9:00 AM):
   - Process overnight emails
   - Review High Priority summaries
   - Approve time-sensitive drafts

2. **Midday** (12:00 PM):
   - Quick processing for urgent items
   - Review Important emails

3. **End of Day** (5:00 PM):
   - Final processing
   - Handle remaining drafts
   - Plan tomorrow's responses

### Whitelist Configuration

**High Priority Whitelist**:
- ✅ Your boss/manager
- ✅ Executive team
- ✅ Key clients
- ✅ Important stakeholders
- ❌ Don't over-populate (defeats the purpose)

**Important Whitelist**:
- ✅ Regular customers
- ✅ Team members
- ✅ Business partners
- ✅ Vendors

**Subscriptions Whitelist**:
- ✅ Industry newsletters you read
- ✅ Professional development content
- ✅ Company announcements
- ❌ Marketing emails you ignore (let them auto-delete)

### Template Creation

**Template Writing Tips**:

1. **Keep it professional but personable**
2. **Use clear, concise language**
3. **Include placeholders** for AI to fill in specifics
4. **Match your brand voice**
5. **Cover common scenarios** without being too specific

**Good Template Example**:
```
Subject: Re: Your inquiry about [topic]

Hi [name],

Thank you for reaching out about [specific topic from their email].

[Answer their main question or address their concern]

[Provide next steps or call to action]

Please let me know if you need any additional information.

Best regards,
[Your Name]
```

**Poor Template Example**:
```
Subject: Response

Got your email. Will get back to you.

Thanks
```

### Security Best Practices

**Password Security**:
- ✅ Always use App Passwords (never main passwords)
- ✅ Use unique passwords for each email account
- ✅ Store backup of passwords securely (password manager)
- ❌ Never share your `.env` file
- ❌ Never commit `.env` to Git or version control

**Access Control**:
- ✅ Run on trusted devices only
- ✅ Use strong SECRET_KEY in `.env`
- ✅ Change PGPASSWORD from default
- ❌ Don't expose to public internet
- ❌ Don't access over unsecured WiFi

**Data Privacy**:
- ✅ Regular backups
- ✅ Secure your computer (encryption, strong password)
- ✅ Review who has access to your network
- ❌ Don't process sensitive emails on shared computers

### Maintenance

**Weekly**:
- Review and update whitelists
- Check for processing errors
- Delete old security alerts

**Monthly**:
- Backup database
- Review and refine templates
- Check API usage (if on paid tier)
- Clean up old drafts

**Quarterly**:
- Review all configuration settings
- Update email account passwords
- Audit priority classifications
- Consider template improvements

---

## FAQ

### General Questions

**Q: Is my email data secure?**  
A: Yes, all data is stored locally on your machine in an encrypted database. Email passwords are encrypted using industry-standard encryption. No data is sent to any server except Google Gemini for AI analysis.

**Q: Can I use this with multiple email accounts?**  
A: Yes! You can add unlimited email accounts from different providers (Gmail, Yahoo, Outlook, etc.). Each account is processed separately.

**Q: Does this actually send emails?**  
A: Currently, the system generates draft responses that you can approve, but actual sending is not yet implemented. You'll need to manually send approved drafts for now. Email sending will be added in a future update.

**Q: What happens to emails after processing?**  
A: They're marked as "read" in your mailbox and stored in the database with their AI analysis. Pure advertising emails (not in subscriptions whitelist) are permanently deleted from your mailbox.

### Technical Questions

**Q: How much does it cost to run?**  
A: The software is a one-time purchase. Running costs:
- Gemini API: Free tier (25 emails/day) or paid ($7-15/month for higher volume)
- No other ongoing costs (runs on your hardware)

**Q: Can I run this on a server 24/7?**  
A: Yes! It's designed for Docker, so it runs perfectly on:
- Home servers
- NAS devices (Synology, QNAP)
- Cloud servers (AWS, Digital Ocean, etc.)
- Raspberry Pi (with enough RAM)

**Q: How do I update to a new version?**  
A:
```bash
docker compose down
# Extract new version files
tar -xzf email-automation-v2.0.tar.gz
docker compose up -d --build
```

**Q: Can I access this from my phone?**  
A: Yes, if you expose it to your local network (see Advanced Configuration). The web interface is responsive and works on mobile browsers. Dedicated mobile apps may be available in the future.

**Q: What if I want to stop using it?**  
A: Simply run `docker compose down` to stop the app. Your emails remain in your email account untouched. You can export data from the database if needed before uninstalling.

### Feature Questions

**Q: Can it handle attachments?**  
A: Yes, the AI is aware of attachments and mentions them in summaries (file names, types, count). However, it doesn't scan the contents of attachments for now.

**Q: Does it work with email threads?**  
A: Currently it processes individual emails. Thread context (previous messages in conversation) is a planned future feature.

**Q: Can I customize the AI behavior?**  
A: You can influence it through templates and priority rules. Advanced AI customization (custom models, fine-tuning) is planned for future versions.

**Q: What languages does it support?**  
A: The interface is in English. The AI can process emails in multiple languages (Gemini supports 100+ languages), but draft responses are generated in English by default.

### Troubleshooting Questions

**Q: Why aren't all my emails being processed?**  
A: The system only processes "unread" emails to avoid duplicates. If you've already read an email in your mail client, it won't be processed. Also, some emails may be intentionally skipped (pure marketing, etc.).

**Q: Why was my subscription email deleted?**  
A: If it wasn't in your Subscriptions Whitelist and appeared to be pure advertising, it was auto-deleted. Add the sender to your Subscriptions Whitelist to keep future emails.

**Q: The AI classification seems wrong. What can I do?**  
A: The AI learns from your templates and priority rules. Make sure you have:
1. Configured sender whitelists accurately
2. Added relevant keywords
3. Created templates for common categories
The more you configure, the more accurate it becomes.

---

## Getting Help

### Support Resources

**Documentation**:
- This User Manual
- BETA_INSTALL.md (Installation guide)
- QUICK_START.md (Package creator guide)

**Community** (Coming Soon):
- User forum
- FAQ database
- Video tutorials

**Direct Support**:
- Email: support@yourdomain.com
- Response time: Within 24 hours (business days)

### Reporting Issues

When contacting support, include:

1. **System Information**:
   - Operating System (Windows/Mac/Linux)
   - Docker version: `docker --version`
   - Application version

2. **Error Details**:
   - What were you trying to do?
   - What happened instead?
   - Exact error message (if any)

3. **Logs** (if applicable):
   ```bash
   docker compose logs app > app-logs.txt
   ```
   Attach the `app-logs.txt` file

4. **Steps to Reproduce**:
   - Step 1: ...
   - Step 2: ...
   - Step 3: Error occurs

---

## Appendix

### Email Provider Comparison

| Provider | IMAP Address | App Password Required | Notes |
|----------|--------------|------------------------|--------|
| Gmail | imap.gmail.com:993 | Yes | Requires 2FA enabled |
| Yahoo | imap.mail.yahoo.com:993 | Yes | Called "App password" |
| Outlook | outlook.office365.com:993 | No* | Use regular password |
| iCloud | imap.mail.me.com:993 | Yes | Called "App-specific password" |
| AOL | imap.aol.com:993 | Yes | Similar to Yahoo |

*Outlook: App password only required if 2FA is enabled

### Keyboard Shortcuts

| Action | Shortcut | Where |
|--------|----------|-------|
| Refresh Dashboard | F5 | Any tab |
| Next Tab | Ctrl + → | Tab navigation |
| Previous Tab | Ctrl + ← | Tab navigation |
| Process Emails | Ctrl + P | Dashboard |
| Search | Ctrl + F | Browser search |

### System Architecture

```
┌─────────────────────────────────────────┐
│         Your Web Browser                │
│         (localhost:5000)                │
└─────────────────┬───────────────────────┘
                  │ HTTP
┌─────────────────▼───────────────────────┐
│      Flask Web Application              │
│      - Routes & API                     │
│      - Email Processing Logic           │
└─────┬──────────┬──────────┬─────────────┘
      │          │          │
      │          │          │
┌─────▼────┐ ┌──▼──────┐ ┌─▼──────────┐
│PostgreSQL│ │  IMAP   │ │ Gemini API │
│ Database │ │ Servers │ │ (Google)   │
│  (Local) │ │ (Email) │ │  (Cloud)   │
└──────────┘ └─────────┘ └────────────┘
```

### File Structure

```
email-automation/
├── docker-compose.yml       Service orchestration
├── Dockerfile              Container image
├── .env                    Your configuration (SECRET!)
├── requirements.txt        Python dependencies
├── src/
│   ├── app.py             Main application
│   ├── database.py        Database operations
│   ├── email_service.py   IMAP handling
│   ├── ai_processor.py    Gemini integration
│   └── encryption.py      Password encryption
├── templates/
│   └── index.html         Web interface
└── static/
    ├── app.js             Frontend JavaScript
    └── style.css          Styling & themes
```

### Glossary

**IMAP**: Internet Message Access Protocol - how email clients access mailboxes

**Draft**: AI-generated email response awaiting your approval

**Whitelist**: List of approved/prioritized email senders

**SLA**: Service Level Agreement - time-based priority indicator

**App Password**: Special password for third-party apps (more secure than main password)

**Priority**: Urgency level (P0=Critical, P1=High, P2=Important, P3=Low)

**Classification**: Category assigned to email (Sales, Support, etc.)

**Sentiment**: Emotional tone of email (Positive, Negative, Neutral, Urgent)

**Template**: Pre-written response framework for common scenarios

**API**: Application Programming Interface - how the app talks to Gemini

**Docker**: Containerization platform that packages and runs the app

---

## Version History

**Version 1.0** (Current)
- Initial release
- Multi-account email support
- AI-powered classification and drafts
- Priority-based triaging
- Security alerts category
- 8 color themes
- Self-hosted Docker deployment

---

*Email Automation App - User Manual v1.0*  
*Last Updated: October 30, 2025*  
*© 2025 Your Company Name. All rights reserved.*
