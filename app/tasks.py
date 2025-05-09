import os
from email.message import EmailMessage
import smtplib


def send_contact_email(name, email, message_content):
        '''
            * A function to be called from the 'contact' route
            * Executed as a background worker using Redis Queues
        '''
        conn = smtplib.SMTP("smtp.gmail.com")
        my_email = os.getenv("GMAIL_USER_EMAIL")
        my_password = os.getenv("GMAIL_APP_PASSWORD")
        message = EmailMessage()
        message["From"] = my_email
        message["To"] = my_email
        message["subject"] = f"""{name} ({email}) has reached out from EventHub."""
        message.set_content(message_content)
        conn.starttls()
        conn.login(
            user = my_email,
            password = my_password
        )
        conn.send_message(message)
        conn.close()