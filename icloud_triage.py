import chilkat
import os
import sys
from utils.notionhelper import NotionHelper
from datetime import datetime
from dateutil import parser
from utils.ollama import ask_ollama

# Initialize NotionHelper
notion_helper = NotionHelper(os.getenv("NOTION_API_KEY"))
notion_database_id = "20efdfd68a97804e8c50ff1168adcf27"

# Step 1: Connect to iCloud Mail using Chilkat
def connect_icloud(username, password):
    imap = chilkat.CkImap()

    # Connect to the iCloud IMAP Mail Server
    imap.put_Ssl(True)
    imap.put_Port(993)
    success = imap.Connect("imap.mail.me.com")
    if not success:
        print(f"Connection failed: {imap.lastErrorText()}")
        return None

    # Login with credentials
    success = imap.Login(username, password)
    if not success:
        print(f"Login failed: {imap.lastErrorText()}")
        return None

    # Select the Inbox
    success = imap.SelectMailbox("Inbox")
    if not success:
        print(f"Mailbox selection failed: {imap.lastErrorText()}")
        return None

    return imap

# Step 2: Fetch unread emails using Chilkat
def fetch_unread_emails(imap):
    # Search for unread emails
    messageSet = imap.Search("UNSEEN", True)
    if not messageSet:
        return []

    # Get the message UIDs
    email_uids = []
    for i in range(messageSet.get_Count()):
        email_uids.append(messageSet.GetId(i))

    return email_uids

# Step 3: Parse email using Chilkat email object
def parse_email(email_obj):
    # Get subject
    subject = email_obj.subject() if email_obj.subject() else "No Subject"

    # Get sender email address
    sender = email_obj.ck_from() if email_obj.ck_from() else "Unknown Sender"

    # Get date received
    date_received_str = email_obj.getHeaderField("Date")
    date_received = "Unknown Date"
    if date_received_str:
        try:
            # Parse the date string into a datetime object
            date_received = parser.parse(date_received_str)
        except Exception as e:
            print(f"Error parsing date string '{date_received_str}': {str(e)}")
            date_received = "Unknown Date" # Keep as string if parsing fails

    # Get body (try to get plain text first)
    body = email_obj.getPlainTextBody()
    if not body:
        # If no plain text, try to get HTML and strip tags
        html_body = email_obj.getHtmlBody()
        if html_body:
            # Simple HTML tag removal (you could use BeautifulSoup for better parsing)
            import re
            body = re.sub('<[^<]+?>', '', html_body)
        else:
            body = "No body content"

    # Clean up body whitespace
    if body:
        # Replace multiple whitespace characters (including newlines) with a single space
        import re
        body = re.sub(r'\s+', ' ', body).strip()

    return subject, sender, date_received, body

# Step 4: Use GPT to classify
def classify_email(subject, body):
    prompt = f"""Classify this email into exactly one of these categories: '🅾️ Action Required', 'Spam', or 'Low Priority'.

    Subject: {subject}
    Body: {body[:500]}...

    Respond with only the category name:"""
    content = ask_ollama(prompt)
    if isinstance(content, str) and content: # Check if content is a non-empty string
        # Clean up the response to ensure consistent format
        content = content.strip().replace("Classification: ", "").replace("'", "").replace('"', '')
        if content in ["🅾️ Action Required", "Spam", "Low Priority"]:
            return content
        else:
            return "Low Priority"  # Default fallback
    else:
        print("Warning: Ollama API returned empty or invalid content.")
        return "Unknown" # Default classification

# Step 5: Main driver
def triage_emails(username, password):
    imap = connect_icloud(username, password)
    if not imap:
        print("Failed to connect to iCloud mail.")
        return

    email_uids = fetch_unread_emails(imap)

    if not email_uids:
        print("No unread emails found.")
        imap.Disconnect()
        return

    print(f"Found {len(email_uids)} unread emails. Processing...")

    for uid in email_uids:
        try:
            # Fetch email by UID
            email_obj = imap.FetchSingle(uid, True)  # True means fetch by UID
            if not email_obj:
                print(f"Failed to fetch email with UID: {uid}")
                continue

            subject, sender, date_received, body = parse_email(email_obj)
            label = classify_email(subject, body)

            print(f"\nFrom: {sender}")
            print(f"Date: {date_received}")
            print(f"Subject: {subject}")
            print(f"Classification: {label}")

            # If classified as 'Action Required', write to file and Notion
            if label == "🅾️ Action Required":
                # Write to local file
                with open("action_emails.txt", "a", encoding="utf-8") as f:
                    f.write(f"--- Action Required Email ---\n")
                    f.write(f"Received Date: {date_received}\n")
                    f.write(f"Subject: {subject}\n")
                    f.write(f"Classification: {label}\n")
                    f.write(f"Body:\n{body}\n")
                    f.write(f"-----------------------------\n\n")

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
                                    "text": {"content": body[:2000]}
                                }
                            ]
                        },

                        # email field
                        "From": {
                            "email": sender        # plain string
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


        except Exception as e:
            print(f"Error processing email {uid}: {str(e)}")

    # Disconnect from the IMAP server
    imap.Disconnect()

# Example usage
# Note: For iCloud, use just the username part (before @icloud.com)
triage_emails("drjanduplessis", "mayx-eiwe-ypll-gslb")
