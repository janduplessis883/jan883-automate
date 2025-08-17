import imaplib
import email
from email.header import decode_header
import os
from utils.notionhelper import NotionHelper
from datetime import datetime
from dateutil import parser
from utils.ollama import ask_ollama

# Initialize NotionHelper
notion_helper = NotionHelper(os.getenv('NOTION_API_KEY'))
notion_database_id = "20efdfd68a97804e8c50ff1168adcf27"
# Step 1: Connect to Gmail
def connect_gmail(user, password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, password)
    mail.select("inbox")
    return mail
# Step 2: Fetch unread emails
def fetch_unread_emails(mail):
    status, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()
    return email_ids
# Step 3: Parse email
def parse_email(raw_email):
    msg = email.message_from_bytes(raw_email)

    # Get subject
    subject, encoding = decode_header(msg.get("Subject", "No Subject"))[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or 'utf-8', errors='ignore')

    # Get sender email address (simplified)
    sender = msg.get("From", "Unknown Sender")

    # Get date received
    date_received_str = msg.get("Date")
    date_received = "Unknown Date"
    if date_received_str:
        try:
            date_received = parser.parse(date_received_str)
        except Exception as e:
            print(f"Error parsing date string '{date_received_str}': {str(e)}")
            date_received = "Unknown Date"

    # Get body (try to get plain text first)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # Look for text/plain parts, skip attachments
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                try:
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                         body = payload.decode(errors='ignore')
                         break # Found plain text body, use it
                except Exception as e:
                    print(f"Error decoding text/plain part: {e}")
                    continue # Try next part
    else:
        # If not multipart, get payload directly
        try:
            payload = msg.get_payload(decode=True)
            if isinstance(payload, bytes):
                body = payload.decode(errors='ignore')
            elif isinstance(payload, str):
                body = payload
            else:
                body = str(payload)
        except Exception as e:
            print(f"Error decoding single part payload: {e}")
            body = str(msg.get_payload(decode=True))

    # Clean up body whitespace (optional, depending on desired output)
    # if body:
    #     import re
    #     body = re.sub(r'\s+', ' ', body).strip()

    return subject, sender, date_received, body
# Step 4: Use GPT to classify
def classify_email(subject, body):
    prompt = f"""Classify this email into one of: '🅾️ Action Required', 'Spam', or 'Low Priority'.

    Subject: {subject}
    Body: {body}

    Classification:"""
    try:
        content = ask_ollama(prompt)
        if isinstance(content, str) and content: # Check if content is a non-empty string
            return content.strip()
        else:
            print("Warning: Ollama API returned empty or invalid content.")
            return "Unknown" # Default classification
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        return "Unknown" # Default classification on API error
# Step 5: Main driver
def triage_emails(user, password):
    mail = connect_gmail(user, password)
    email_ids = fetch_unread_emails(mail)
    for eid in email_ids:
        # Check status of fetch operation
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status == 'OK' and msg_data and isinstance(msg_data, list) and len(msg_data) > 0 and isinstance(msg_data[0], tuple) and len(msg_data[0]) > 1:
            raw_email = msg_data[0][1]
            subject, sender, date_received, body = parse_email(raw_email)
            label = classify_email(subject, body)

            print(f"\nFrom: {sender}")
            print(f"Date: {date_received}")
            print(f"Subject: {subject}")
            print(f"Classification: {label}")

            # If classified as 'Action Required', write to file and Notion
            if label == "🅾️ Action Required":
                # Write to local file
                try:
                    with open("action_emails.txt", "a", encoding="utf-8") as f:
                        f.write(f"--- Action Required Email ---\n")
                        f.write(f"Received Date: {date_received}\n")
                        f.write(f"Subject: {subject}\n")
                        f.write(f"Classification: {label}\n")
                        f.write(f"Body:\n{body}\n")
                        f.write(f"-----------------------------\n\n")
                    print(f"Successfully wrote email '{subject}' to action_emails.txt.")
                except Exception as file_e:
                    print(f"Failed to write email '{subject}' to action_emails.txt: {str(file_e)}")


                # Write to Notion database
                try:
                    page_properties = {
                        # must match the database “title” field name
                        "Subject": {
                            "title": [
                                {
                                    "type": "text",
                                    "text": {"content": subject}
                                }
                            ]
                        },

                        # any rich-text field name you created
                        "Body": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": body[:2000]} # Truncate body for Notion
                                }
                            ]
                        },

                        # email field
                        "From": {
                            "email": sender
                        },

                        # date field
                        "Date": {
                            "date": {
                                "start": date_received.isoformat() if isinstance(date_received, datetime) else None   # ISO 8601
                            }
                        }
                    }
                    notion_helper.new_page_to_db(notion_database_id, page_properties)
                    print(f"Successfully wrote email '{subject}' to Notion.")
                except Exception as notion_e:
                    print(f"Failed to write email '{subject}' to Notion: {str(notion_e)}")


        else:
            print(f"Error fetching or processing email ID {eid}: Status {status}, Data: {msg_data}")
# Example usage
triage_emails("drjanduplessis.pm@gmail.com", "mbcd snhw kaqu pmwx")
