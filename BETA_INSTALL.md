# 📧 Email Automation App - Beta Installation Guide

Welcome, Beta Tester! Thank you for testing our AI-powered email automation system.

## 🎯 What This App Does

- **Multi-Account Email Processing**: Connect Gmail, Yahoo, Outlook, iCloud, and custom IMAP accounts
- **AI-Powered Intelligence**: Uses Google Gemini 2.0 Flash to analyze, classify, and prioritize emails
- **Smart Triaging**: Automatically categorizes emails as High Priority, Important, or Low Priority
- **Draft Generation**: Creates response drafts for emails requiring action
- **Security Alerts**: Special category for security-related emails with bulk management
- **Human-in-the-Loop**: All drafts require your approval before sending

---

## 📋 Prerequisites

Before installation, ensure you have:

1. **Docker & Docker Compose**
   - **Windows/Mac**: [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - **Linux**: Install Docker Engine + Docker Compose
     ```bash
     # Ubuntu/Debian
     sudo apt-get update
     sudo apt-get install docker.io docker-compose
     
     # Add your user to docker group
     sudo usermod -aG docker $USER
     # Log out and back in for this to take effect
     ```

2. **Gemini API Key** (FREE)
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with Google account
   - Click "Create API Key"
   - **Free Tier**: 50 requests/day, 10 requests/minute
   - **Cost**: Each email = 2 API calls (you can process ~20-25 emails/day free)

3. **Email Account App Password** (for Gmail)
   - Regular Gmail password will NOT work
   - Enable 2-Factor Authentication on your Google account
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password (no spaces)

---

## 🚀 Installation Steps

### Step 1: Extract Files

Extract the package to your preferred location:

```bash
# Example
mkdir ~/email-automation
cd ~/email-automation
tar -xzf email-automation-beta-v1.0.tar.gz
```

### Step 2: Configure Environment

1. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your details:
   ```bash
   nano .env  # or use any text editor
   ```

3. **Required**: Set your Gemini API key:
   ```
   GEMINI_API_KEY=your-actual-api-key-here
   ```

4. **Recommended**: Change database password:
   ```
   PGPASSWORD=choose-a-strong-password
   ```

5. **Recommended**: Set a secret key:
   ```bash
   # Generate a random secret key
   python3 -c "import secrets; print(secrets.token_hex(32))"
   
   # Copy output to .env
   SECRET_KEY=paste-generated-key-here
   ```

6. **Optional**: Pre-configure first email account (or add via web UI later):
   ```
   EMAIL_PROVIDER=gmail
   EMAIL_USER=youremail@gmail.com
   EMAIL_PASSWORD=your-16-char-app-password
   EMAIL_IMAP_SERVER=imap.gmail.com
   EMAIL_IMAP_PORT=993
   ```

### Step 3: Start the Application

```bash
# Build and start containers
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

**First startup takes 2-3 minutes** to:
- Download Docker images
- Build the application
- Initialize the database
- Start all services

### Step 4: Access the Application

1. Open your browser
2. Navigate to: **http://localhost:5000**
3. You should see the Email Automation Dashboard

---

## 🎨 First-Time Setup

### 1. Add Email Accounts

If you didn't pre-configure an email account in `.env`:

1. Click the **"Email Accounts"** tab
2. Click **"Add Email Account"**
3. Fill in details:
   - **Account Name**: e.g., "Work Gmail"
   - **Email Provider**: Select from dropdown (Gmail, Yahoo, Outlook, etc.)
   - **Email Address**: your-email@gmail.com
   - **Password**: Your app-specific password (NOT regular password)
   - IMAP server auto-fills based on provider

4. Click **"Add Account"**

### 2. Configure Priority Rules

1. Go to **"Configuration"** tab
2. Set up whitelists and keywords:
   - **High Priority Senders**: VIP email addresses
   - **High Priority Keywords**: Urgent, Critical, Deadline, etc.
   - **Important Senders**: Regular business contacts
   - **Subscriptions Whitelist**: Newsletters you want to keep

### 3. Create Response Templates

1. Go to **"Templates"** tab
2. Create templates for common responses:
   - Out of office
   - Meeting confirmation
   - General inquiry response

### 4. Process Emails

1. Return to **"Dashboard"** tab
2. Click **"Process New Emails"**
3. Wait for processing (shows progress)
4. View summaries in expandable sections

### 5. Review & Approve Drafts

1. Go to **"Review Drafts"** tab
2. Click on any email to expand
3. Edit the draft if needed
4. Click **"Approve"** (Note: Actual sending not yet implemented in beta)

---

## ⚙️ Configuration Options

### Theme Selection

Choose from 8 color themes in the **Settings** tab:
- Default Blue
- Ocean Teal
- Forest Green
- Sunset Purple
- Rose Pink
- Amber Gold
- Slate Gray
- **Dark Mode**

### Priority Levels

- **P0/P1 (High Priority)**: Red gradient, < 24h SLA = Green
- **P2 (Important)**: Orange gradient
- **P3 (Low Priority)**: Gray gradient
- **Security Alerts**: Special section with bulk delete

### SLA Color Coding

- 🟢 **Green**: < 24 hours old
- 🟠 **Amber**: 24-48 hours old
- 🔴 **Red**: > 48 hours old

---

## 🔧 Management Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Just the app
docker-compose logs -f app

# Just the database
docker-compose logs -f postgres
```

### Stop the Application
```bash
docker-compose stop
```

### Start (after stopping)
```bash
docker-compose start
```

### Restart
```bash
docker-compose restart
```

### Complete Shutdown (removes containers but keeps data)
```bash
docker-compose down
```

### Reset Everything (⚠️ DELETES ALL DATA)
```bash
docker-compose down -v
docker-compose up -d
```

### Update to New Version
```bash
# Stop current version
docker-compose down

# Extract new package files (overwrites old ones)
tar -xzf email-automation-beta-v2.0.tar.gz

# Rebuild and start
docker-compose up -d --build
```

---

## 🐛 Troubleshooting

### Port 5000 Already in Use

**Error**: `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solution**: Change port in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```
Then access via http://localhost:8080

### Database Connection Failed

**Error**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check if database is healthy
docker-compose ps

# If postgres is unhealthy, restart it
docker-compose restart postgres

# Wait 10 seconds, then restart app
docker-compose restart app
```

### Gemini API Quota Exceeded

**Error**: `429 Resource has been exhausted`

**Solution**:
- Free tier: 50 requests/day, 10/minute
- Each email = 2 API calls
- Wait until quota resets (next day)
- Or upgrade to paid tier at https://ai.google.dev/pricing

### Gmail Authentication Failed

**Error**: `Authentication failed` or `Login failed`

**Solution**:
1. Verify you're using **App Password**, not regular password
2. Check 2FA is enabled on Google account
3. Generate new App Password if needed
4. Remove spaces from App Password

### Can't Access from Other Devices

The app runs on `localhost` by default, only accessible from the same machine.

**To access from other devices on your network**:

1. Find your computer's local IP:
   ```bash
   # Linux/Mac
   ip addr show | grep inet
   
   # Windows
   ipconfig
   ```

2. Edit `docker-compose.yml`:
   ```yaml
   ports:
     - "0.0.0.0:5000:5000"  # Listen on all interfaces
   ```

3. Restart:
   ```bash
   docker-compose restart app
   ```

4. Access from other devices: `http://YOUR-IP:5000`

---

## 📊 Beta Testing Checklist

Please test and provide feedback on:

- [ ] **Installation**: Was setup smooth? Any errors?
- [ ] **Email Account Connection**: Did your provider (Gmail/Yahoo/Outlook) work?
- [ ] **Email Processing**: Did it correctly categorize emails?
- [ ] **AI Analysis**: Are summaries accurate and useful?
- [ ] **Priority Classification**: Are priorities assigned correctly?
- [ ] **Draft Generation**: Are response drafts relevant and well-written?
- [ ] **Security Alerts**: Are security emails correctly identified?
- [ ] **Performance**: How fast does it process emails?
- [ ] **UI/UX**: Is the interface intuitive?
- [ ] **Bugs**: Any crashes, errors, or unexpected behavior?

---

## 📧 Feedback & Support

**For Beta Testing Period**:

- **Email**: beta@yourdomain.com
- **Report Issues**: Include screenshots and error logs
- **Feature Requests**: Tell us what's missing
- **Performance**: Share your email volume and processing times

**Get Logs for Bug Reports**:
```bash
docker-compose logs app > app-logs.txt
docker-compose logs postgres > db-logs.txt
```

---

## ⚠️ Beta Limitations

This is a **beta version** for testing purposes:

- ✅ Full email processing and AI analysis
- ✅ Multi-account support
- ✅ Draft generation and review
- ❌ **Actual email sending** not yet implemented (drafts can be approved but won't send)
- ❌ No license activation (will be added for production)
- ❌ No automatic updates (manual update process)

---

## 🔐 Data Privacy

- **All data stored locally** on your machine (PostgreSQL database)
- **Email passwords encrypted** using industry-standard encryption
- **No data sent to our servers** (only to Google Gemini for AI analysis)
- **You control your data** - can delete anytime with `docker-compose down -v`

---

## 📦 What's Included

```
email-automation-beta/
├── Dockerfile                 # Container build instructions
├── docker-compose.yml         # Service orchestration
├── requirements.txt           # Python dependencies
├── .env.example              # Configuration template
├── BETA_INSTALL.md           # This file
├── src/                      # Application source code
│   ├── app.py               # Main Flask application
│   ├── database.py          # Database operations
│   ├── email_service.py     # Email IMAP processing
│   ├── ai_processor.py      # Gemini AI integration
│   └── encryption.py        # Password encryption
├── templates/               # HTML templates
│   └── index.html
└── static/                  # Frontend assets
    ├── app.js
    └── style.css
```

---

## 🎉 Getting Started

1. ✅ Complete installation steps above
2. ✅ Add your first email account
3. ✅ Click "Process New Emails"
4. ✅ Explore the Email Summaries
5. ✅ Review and edit drafts
6. ✅ Provide feedback!

**Enjoy testing the future of email automation!** 🚀

---

*Beta Version | December 2025 | Email Automation Platform*
