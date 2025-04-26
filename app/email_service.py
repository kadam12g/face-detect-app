#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models import Subscriber
from app import db

class EmailService:
    """
    A service for sending email notifications to subscribers.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def get_subscribers(self):
        """Returns a list of active subscriber emails."""
        subscribers = Subscriber.query.filter_by(active=True).all()
        return [sub.email for sub in subscribers]
    
    def send_notification(self, image_data):
        """
        Sends a notification to all active subscribers about a new image upload.
        
        Args:
            image_data: Dictionary containing image details
        """
        subscribers = self.get_subscribers()
        if not subscribers:
            return
        
        subject = "New Image Uploaded with Face Detection"
        
        # Create message body
        body = f"""
        A new image has been uploaded!
        
        Description: {image_data['description']}
        Faces Detected: {image_data['faces_detected']}
        
        View it at: {image_data['url']}
        
        ---
        To unsubscribe, click here: {image_data['unsubscribe_url']}
        """
        
        # Send email to each subscriber
        for email in subscribers:
            self._send_email(email, subject, body)
    
    def _send_email(self, to_email, subject, body):
        """
        Sends an email using the configured mail relay.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
        """

        if os.environ.get('FLASK_ENV') == 'development':
            print(f"[DEV MODE] Would send email to {to_email} with subject: {subject}")
            print(f"Body: {body}")
            return
        
        msg = MIMEMultipart()
        msg['From'] = 'noreply@face-detection-app.com'
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.host, self.port)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
