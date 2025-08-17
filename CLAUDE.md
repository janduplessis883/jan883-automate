# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an email automation toolkit that processes emails from multiple providers (Gmail and iCloud) using AI classification, writes action items to files and Notion databases, and includes utilities for backup operations and password generation.

## Core Architecture

### Main Scripts
- `gmail_triage.py` - Processes Gmail emails using IMAP, classifies with Ollama AI, writes action items to `action_emails.txt` and Notion
- `icloud_triage.py` - Similar functionality for iCloud emails using Chilkat library  
- `backup.py` - Automated backup system for multiple directories with configurable skip patterns
- `password.py` - Secure password generator using secrets module

### Utility Modules (`utils/`)
- `notionhelper.py` - Comprehensive Notion API wrapper with database operations, file uploads, DataFrame conversion
- `ollama.py` - Ollama API client for AI text generation and classification

## Key Dependencies

### Email Processing
- `imaplib` (Gmail) and `chilkat` (iCloud) for email access
- `email` for parsing email content
- `dateutil` for date parsing

### AI & APIs
- `requests` for HTTP calls to Ollama and Notion APIs
- Custom `ask_ollama()` function for AI classification

### Data & Utilities
- `pandas` for DataFrame operations in NotionHelper
- `notion_client` for Notion API integration
- `secrets` and `string` for secure password generation

## Configuration

### Environment Variables
- `OLLAMA_API_URL` - Ollama server endpoint (defaults to localhost:11434)
- Notion API token required in NotionHelper constructor

### Hardcoded Configuration
- Notion database ID: `"20efdfd68a97804e8c50ff1168adcf27"`
- Gmail credentials and iCloud credentials are hardcoded in main scripts (should be moved to environment variables)

## Email Classification System

The AI classifies emails into three categories:
- `🅾️ Action Required` - Emails that need user attention (saved to file and Notion)
- `Spam` - Unwanted emails
- `Low Priority` - Informational emails

## Backup System

Configured to backup:
- `/Users/janduplessis/code/janduplessis883` 
- `/Users/janduplessis/Documents`

Destination: `/Volumes/JanBackupHD/AUTO-BACKUPS`

Skips common development files (.git, node_modules, __pycache__, .DS_Store, etc.)

## Security Notes

- Hardcoded email credentials present in main scripts - consider using environment variables
- Password generator uses cryptographically secure `secrets` module
- Backup system properly handles permissions and file access errors

## Common Tasks

### Running Email Triage
```bash
python gmail_triage.py
python icloud_triage.py
```

### Generate Password
```bash
python password.py "example.com"
```

### Run Backup
```bash
python backup.py
```

## Development Environment

- Python environment managed via `.python-version` file (currently: "automation")
- Uses type hints in utility modules
- Error handling implemented throughout email processing and API calls