# 📦 Beta Package Creation Guide

## For Distributing to Beta Testers

### Files to Include in Package

Create a zip file with these files/folders:

```
email-automation-beta.zip
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── BETA_INSTALL.md
├── src/
├── templates/
└── static/
```

### Quick Packaging Commands

**Option 1: Using zip (Linux/Mac)**
```bash
zip -r email-automation-beta.zip \
  Dockerfile \
  docker-compose.yml \
  requirements.txt \
  .env.example \
  BETA_INSTALL.md \
  src/ \
  templates/ \
  static/ \
  -x "*.pyc" "**/__pycache__/*" "*.env" ".git/*"
```

**Option 2: Using tar (Linux/Mac)**
```bash
tar -czf email-automation-beta.tar.gz \
  --exclude="*.pyc" \
  --exclude="__pycache__" \
  --exclude=".env" \
  --exclude=".git" \
  Dockerfile \
  docker-compose.yml \
  requirements.txt \
  .env.example \
  BETA_INSTALL.md \
  src/ \
  templates/ \
  static/
```

**Option 3: Windows (PowerShell)**
```powershell
Compress-Archive -Path Dockerfile,docker-compose.yml,requirements.txt,.env.example,BETA_INSTALL.md,src,templates,static -DestinationPath email-automation-beta.zip
```

### Distribution Methods

#### Method 1: Direct Download Link
1. Upload to cloud storage (Dropbox, Google Drive, etc.)
2. Create shareable link
3. Send to beta testers

#### Method 2: GitHub Private Repository
1. Create private repository
2. Add beta testers as collaborators
3. They clone with: `git clone https://github.com/yourname/email-automation-beta`

#### Method 3: Email Attachment
- If under 25MB, can email directly
- Otherwise, use cloud storage link

### Beta Tester Email Template

```
Subject: Email Automation Beta - Installation Package

Hi [Tester Name],

Thank you for agreeing to beta test our AI-powered Email Automation app!

DOWNLOAD PACKAGE:
[Insert download link here]

INSTALLATION:
1. Extract the zip file
2. Follow instructions in BETA_INSTALL.md
3. Key requirement: Docker Desktop installed
4. Free Gemini API key needed (instructions included)

WHAT TO TEST:
- Email account connection (Gmail, Yahoo, Outlook, etc.)
- AI email classification and priority assignment
- Draft generation quality
- Security alerts detection
- Overall user experience

TIMELINE:
Please test within the next [X] days and provide feedback.

SUPPORT:
If you encounter any issues:
- Email: beta@yourdomain.com
- Include error logs (instructions in BETA_INSTALL.md)

FEEDBACK FORM:
[Insert Google Form / Survey link if you have one]

Looking forward to your feedback!

Best regards,
[Your Name]
```

### Pre-Distribution Checklist

- [ ] All sensitive data removed (.env files, API keys, etc.)
- [ ] .env.example is properly templated
- [ ] BETA_INSTALL.md is clear and complete
- [ ] Test the package yourself first:
  - [ ] Extract to clean directory
  - [ ] Follow BETA_INSTALL.md exactly as written
  - [ ] Verify it works from scratch
- [ ] Verify file structure is intact
- [ ] Check package size (should be < 5MB)

### Version Tracking

Keep track of beta versions:

```
email-automation-beta-v1.0.zip   (Initial release)
email-automation-beta-v1.1.zip   (Bug fixes)
email-automation-beta-v1.2.zip   (New features)
```

Include version number in filename for clarity.

### Security Considerations

⚠️ **Important**:
- Never include actual .env files
- Never include database files
- Never include API keys
- No user data should be in package

✅ **Safe to include**:
- Source code
- Configuration templates (.env.example)
- Documentation
- Docker files

---

## For Future Production Release

When ready for public release, you'll need:
1. License server setup
2. License activation in app
3. Payment integration
4. Public landing page
5. Docker Hub publication
6. Automated updates system

But for beta testing, the simple zip package is perfect!
