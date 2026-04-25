"""
Email Integration
================
Send and receive emails (IMAP/SMTP).
"""

import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional


class EmailClient:
    """Email client with IMAP/SMTP support."""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587,
                 imap_server: str = None, imap_port: int = 993):
        self.smtp_server = smtp_server or os.environ.get("SMTP_SERVER", "")
        self.smtp_port = smtp_port
        self.imap_server = imap_server or os.environ.get("IMAP_SERVER", "")
        self.imap_port = imap_port
        self.username = os.environ.get("EMAIL_USER", "")
        self.password = os.environ.get("EMAIL_PASS", "")
        self.connected = False
    
    def configure(self, email: str, password: str, smtp: str = "smtp.gmail.com", imap: str = "imap.gmail.com"):
        """Configure email account."""
        self.username = email
        self.password = password
        self.smtp_server = smtp
        self.imap_server = imap
    
    def send(self, to: str, subject: str, body: str, html: bool = False) -> Dict:
        """Send an email."""
        if not self.username or not self.password:
            return {"error": "Not configured. Use configure() first."}
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.username
            msg["To"] = to
            
            if html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            # Connect to SMTP
            if "gmail" in self.smtp_server:
                server = smtplib.SMTP(self.smtp_server, 587)
                server.starttls()
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            server.login(self.username, self.password)
            server.sendmail(self.username, to, msg.as_string())
            server.quit()
            
            return {"status": "sent", "to": to, "subject": subject}
        except Exception as e:
            return {"error": str(e)}
    
    def receive(self, folder: str = "INBOX", limit: int = 10) -> List[Dict]:
        """Receive emails."""
        if not self.username or not self.password:
            return [{"error": "Not configured"}]
        
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server or "imap.gmail.com")
            mail.login(self.username, self.password)
            mail.select(folder)
            
            result, messages = mail.search(None, "ALL")
            message_ids = result[0].split()[-limit:]
            
            emails = []
            for msg_id in reversed(message_ids):
                result, msg_data = mail.fetch(msg_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                emails.append({
                    "from": msg.get("From"),
                    "subject": msg.get("Subject"),
                    "date": msg.get("Date"),
                    "id": msg_id.decode()
                })
            
            mail.close()
            mail.logout()
            return emails
        except Exception as e:
            return [{"error": str(e)}]
    
    def delete(self, msg_id: str) -> Dict:
        """Delete email by ID."""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server or "imap.gmail.com")
            mail.login(self.username, self.password)
            mail.select("INBOX")
            mail.store(msg_id, "+FLAGS", "\\Deleted")
            mail.close()
            mail.logout()
            return {"status": "deleted", "id": msg_id}
        except Exception as e:
            return {"error": str(e)}


# Global instance
_email_client = None


def get_email_client() -> EmailClient:
    """Get email client."""
    global _email_client
    if _email_client is None:
        _email_client = EmailClient()
    return _email_client


# Easy functions
def send_email(to: str, subject: str, body: str) -> str:
    """Send email."""
    client = get_email_client()
    result = client.send(to, subject, body)
    
    if result.get("error"):
        return f"Error: {result.get('error')}"
    
    return f"Email sent to {to}: {subject}"


def get_emails(limit: int = 5) -> str:
    """Get recent emails."""
    client = get_email_client()
    emails = client.receive(limit=limit)
    
    if not emails:
        return "No emails or not configured"
    
    lines = ["Recent emails:"]
    for e in emails:
        if e.get("error"):
            return e.get("error")
        lines.append(f"From: {e.get('from')}")
        lines.append(f"Subject: {e.get('subject')}")
        lines.append("--")
    
    return "\n".join(lines)


def configure_email(email: str, password: str, smtp: str = "smtp.gmail.com", imap: str = "imap.gmail.com") -> str:
    """Configure email."""
    client = get_email_client()
    client.configure(email, password, smtp, imap)
    return f"Email configured: {email}"


if __name__ == "__main__":
    print("Email Tools")
    print("Configure with: configure_email('you@gmail.com', 'password')")
    print("Send with: send_email('to@example.com', 'Subject', 'Body')")