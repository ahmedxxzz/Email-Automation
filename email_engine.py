import smtplib
import ssl
import random
from email.message import EmailMessage

def get_random_template(templates):
    """Selects one random template index and data."""
    idx = random.randint(0, len(templates) - 1)
    return idx + 1, templates[idx]

def render_content(text, name, email):
    """Replaces placeholders."""
    text = text.replace("{Name}", name)
    text = text.replace("{Email}", email)
    return text

def send_email(sender_email, app_password, recipient_data, templates):
    """
    Connects and sends email. 
    Raises exception on failure to trigger 'Stop on Error'.
    """
    t_id, template = get_random_template(templates)
    
    subject = render_content(template['subject'], recipient_data['name'], recipient_data['email'])
    body = render_content(template['body'], recipient_data['name'], recipient_data['email'])

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_data['email']
    msg.set_content(body)

    context = ssl.create_default_context()

    # We connect per email or use a persistent connection. 
    # For safety and error handling in this specific requirement (Stop on Error),
    # a fresh connection ensures we catch auth errors immediately.
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
        return t_id
    except Exception as e:
        raise e