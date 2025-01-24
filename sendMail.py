# sendMail.py
import smtplib
import ssl
from email.mime.text import MIMEText
import base64 as b64

def d(e):
    d_b = b64.b64decode(e)
    return d_b.decode("utf-8")

def send_email(sender_email, receiver_email, password, subject, body):
    msg = MIMEText(body, "html")  # Specify HTML content
    msg["Subject"] = subject
    msg["From"] = d(sender_email)
    msg["To"] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(d(sender_email), d(password))
        server.sendmail(d(sender_email), receiver_email, msg.as_string())