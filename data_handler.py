import csv
import os
from datetime import datetime

SENT_FILE = "Sent_Emails.csv"
FAILED_FILE = "Failed_Emails.csv"

def initialize_files():
    """Creates log files with headers if they don't exist."""
    if not os.path.exists(SENT_FILE):
        with open(SENT_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Email", "Name", "Timestamp", "Template_ID"])

    if not os.path.exists(FAILED_FILE):
        with open(FAILED_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Email", "Name", "Timestamp", "Error_Message"])


def load_recipients(filepath):
    """Reads input CSV. Expects 'Name' and 'Email' columns."""
    recipients = []
    try:
        with open(filepath, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # Normalize headers to lowercase to be safe
            reader.fieldnames = [name.lower() for name in reader.fieldnames]
            
            if 'name' not in reader.fieldnames or 'email' not in reader.fieldnames:
                raise ValueError("CSV must contain 'Name' and 'Email' columns.")
            
            for row in reader:
                if row.get('email'):
                    recipients.append({"name": row['name'], "email": row['email']})
    except Exception as e:
        raise Exception(f"Error reading CSV: {str(e)}")
    return recipients


def get_sent_history():
    """Returns a Set of emails that have already been sent."""
    sent_emails = set()
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Email'):
                    sent_emails.add(row['Email'])
    return sent_emails


def filter_recipients(raw_list):
    """Returns only recipients who haven't received an email yet."""
    initialize_files()
    sent_history = get_sent_history()
    return [r for r in raw_list if r['email'] not in sent_history]


def log_success(email, name, template_id):
    with open(SENT_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([email, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), template_id])


def log_failure(email, name, error_msg):
    with open(FAILED_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([email, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(error_msg)])

