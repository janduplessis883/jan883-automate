# Email Automation Toolkit

A Python-based email automation system that processes emails from Gmail and iCloud, classifies them using AI, and manages action items through Notion integration.

## Features

- **Multi-Provider Email Processing**: Supports both Gmail (IMAP) and iCloud email accounts
- **AI-Powered Classification**: Uses Ollama AI to categorize emails as Action Required, Spam, or Low Priority
- **Notion Integration**: Automatically creates entries in Notion databases for action items
- **Automated Backups**: Configurable backup system for important directories
- **Secure Password Generation**: Cryptographically secure password generator

## Scripts

- `gmail_triage.py` - Process Gmail emails and extract action items
- `icloud_triage.py` - Process iCloud emails and extract action items  
- `backup.py` - Automated backup of configured directories
- `password.py` - Generate secure passwords for websites

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Chilkat SDK manually from https://www.chilkatsoft.com/ (required for iCloud processing)

3. Set up Ollama server (default: http://localhost:11434) or configure `OLLAMA_API_URL` environment variable

4. Configure Notion API token in the NotionHelper initialization

## Usage

### Email Processing
```bash
# Process Gmail emails
python gmail_triage.py

# Process iCloud emails  
python icloud_triage.py
```

### Generate Passwords
```bash
python password.py "example.com"
```

### Run Backups
```bash
python backup.py
```

## Configuration

- Update email credentials in the respective triage scripts
- Modify Notion database ID in the scripts (currently hardcoded)
- Configure backup paths in `backup.py`
- Set Ollama API endpoint via `OLLAMA_API_URL` environment variable

## Output

- Action-required emails are saved to `action_emails.txt`
- Action items are automatically created in the configured Notion database
- Backup files are timestamped and stored in the configured destination

## Security Notes

⚠️ **Important**: Email credentials are currently hardcoded in the scripts. Consider moving them to environment variables for better security.