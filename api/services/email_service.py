#!/usr/bin/env python3
"""
Email Service
Handles email sending for talent outreach using Resend
"""

import logging
import resend
from typing import Dict, Optional, List
import os
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via Resend"""
    
    def __init__(self):
        # Resend configuration from environment
        self.resend_api_key = os.getenv('RESEND_API_KEY')
        self.default_sender_name = os.getenv('DEFAULT_SENDER_NAME', 'Talent Seeker')
        self.default_sender_email = os.getenv('DEFAULT_SENDER_EMAIL', 'onboarding@resend.dev')
        
        # Email tracking
        self.tracking_enabled = os.getenv('EMAIL_TRACKING_ENABLED', 'true').lower() == 'true'
        self.tracking_domain = os.getenv('EMAIL_TRACKING_DOMAIN', 'localhost:8000')
        
        self.is_configured = bool(self.resend_api_key)
        
        if self.is_configured:
            resend.api_key = self.resend_api_key
            logger.info("Email service configured successfully with Resend")
        else:
            logger.warning("Email service not configured - missing RESEND_API_KEY")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        sender_info: Optional[Dict[str, str]] = None,
        tracking_id: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        is_html: bool = True
    ) -> bool:
        """Send an email using Resend or demo mode"""
        if not self.is_configured:
            # Demo mode - log email details instead of sending
            logger.info(f"[DEMO MODE] Email would be sent:")
            logger.info(f"  To: {to_email}")
            logger.info(f"  Subject: {subject}")
            logger.info(f"  Body: {body[:100]}...")
            logger.info(f"  Sender: {sender_info}")
            logger.info(f"  Tracking ID: {tracking_id}")
            return True
        
        if not to_email:
            logger.error("No recipient email provided")
            return False
        
        try:
            # Prepare sender information
            sender_name = (sender_info or {}).get('name', self.default_sender_name)
            sender_email = (sender_info or {}).get('email', self.default_sender_email)
            reply_to = (sender_info or {}).get('reply_to', sender_email)
            
            # Prepare email body
            email_body = body
            
            # Add tracking pixel if enabled
            if self.tracking_enabled and tracking_id:
                tracking_pixel = f'<img src="http://{self.tracking_domain}/api/v1/tracking/email/{tracking_id}/open" width="1" height="1" style="display:none;">'
                if is_html:
                    email_body += tracking_pixel
                else:
                    # Convert to HTML and add tracking
                    email_body = f"<html><body><pre>{email_body}</pre>{tracking_pixel}</body></html>"
                    is_html = True
            
            # Prepare Resend parameters
            params = {
                "from": f"{sender_name} <{sender_email}>",
                "to": [to_email],
                "subject": subject,
                "reply_to": [reply_to]
            }
            
            # Add body content
            if is_html:
                params["html"] = email_body
            else:
                params["text"] = email_body
            
            # Add custom headers
            headers = {
                "X-Mailer": "TalentSeeker API v1.0",
                "X-Priority": "3"
            }
            
            if tracking_id:
                headers["X-Tracking-ID"] = tracking_id
            
            params["headers"] = headers
            
            # Note: Resend doesn't support file attachments in the same way as SMTP
            # For now, we'll log a warning if attachments are provided
            if attachments:
                logger.warning(f"Attachments not supported with Resend API: {attachments}")
            
            # Send email via Resend
            email_result = resend.Emails.send(params)
            
            if email_result and email_result.get('id'):
                logger.info(f"Email sent successfully to {to_email} (tracking: {tracking_id}, id: {email_result.get('id')})")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}: No response ID from Resend")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_bulk_emails(
        self,
        recipients: List[Dict[str, str]],
        subject_template: str,
        body_template: str,
        sender_info: Optional[Dict[str, str]] = None,
        delay_between_sends: float = 1.0
    ) -> Dict[str, bool]:
        """Send bulk emails with personalization"""
        results = {}
        
        for recipient in recipients:
            email = recipient.get('email')
            if not email:
                continue
            
            # Personalize subject and body
            personalized_subject = subject_template.format(**recipient)
            personalized_body = body_template.format(**recipient)
            
            # Generate tracking ID
            tracking_id = str(uuid.uuid4())
            
            # Send email
            success = await self.send_email(
                to_email=email,
                subject=personalized_subject,
                body=personalized_body,
                sender_info=sender_info,
                tracking_id=tracking_id
            )
            
            results[email] = success
            
            # Delay between sends to avoid rate limiting
            if delay_between_sends > 0:
                import asyncio
                await asyncio.sleep(delay_between_sends)
        
        return results
    
    def create_html_template(
        self,
        content: str,
        sender_name: str = None,
        company_name: str = None,
        unsubscribe_url: str = None
    ) -> str:
        """Create a professional HTML email template"""
        sender_name = sender_name or self.default_sender_name
        company_name = company_name or "TalentSeeker"
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message from {sender_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .email-container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            margin-bottom: 30px;
        }}
        .footer {{
            border-top: 1px solid #eee;
            padding-top: 20px;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
        .cta-button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .cta-button:hover {{
            background-color: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>{company_name}</h1>
        </div>
        
        <div class="content">
            {content}
        </div>
        
        <div class="footer">
            <p>Best regards,<br>{sender_name}</p>
            <hr>
            <p>This email was sent by {company_name}.</p>
            {f'<p><a href="{unsubscribe_url}">Unsubscribe</a></p>' if unsubscribe_url else ''}
        </div>
    </div>
</body>
</html>
        """
        
        return html_template

    def create_antler_startup_template(
        self,
        content: str,
        recipient_name: str,
        custom_message: str = None
    ) -> str:
        """Create a professional Antler-branded HTML email template for startup founder outreach"""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Startup Opportunity with Antler</title>
    <style>
        body {{
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #2d3748;
            max-width: 650px;
            margin: 0 auto;
            padding: 0;
            background-color: #f7fafc;
        }}
        .email-container {{
            background-color: #ffffff;
            margin: 20px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }}
        .header {{
            background: linear-gradient(135deg, #FF4444 0%, #2B5F47 100%);
            padding: 40px 30px;
            text-align: center;
            color: white;
        }}
        .antler-logo {{
            width: 120px;
            height: auto;
            margin-bottom: 20px;
            background-color: white;
            padding: 10px;
            border-radius: 8px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #2d3748;
            margin-bottom: 25px;
        }}
        .main-content {{
            font-size: 16px;
            line-height: 1.8;
            margin-bottom: 30px;
        }}
        .highlight-box {{
            background-color: #f0f9f4;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2B5F47;
            margin: 25px 0;
        }}
        .criteria-list {{
            list-style: none;
            padding: 0;
            margin: 20px 0;
        }}
        .criteria-list li {{
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
        }}
        .criteria-list li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #2B5F47;
            font-weight: bold;
            font-size: 16px;
        }}
        .cta-section {{
            text-align: center;
            margin: 35px 0;
        }}
        .cta-button {{
            display: inline-block;
            padding: 14px 28px;
            background: linear-gradient(135deg, #FF4444 0%, #FF6666 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 16px;
            transition: transform 0.2s;
        }}
        .cta-button:hover {{
            transform: translateY(-2px);
        }}
        .custom-message {{
            background-color: #fef2f2;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #FF4444;
            margin: 25px 0;
            font-style: italic;
        }}
        .signature {{
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid #e2e8f0;
        }}
        .signature-profile {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}
        .profile-image {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin-right: 20px;
            border: 3px solid #e2e8f0;
        }}
        .profile-info {{
            flex: 1;
        }}
        .profile-name {{
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
            margin: 0;
        }}
        .profile-title {{
            font-size: 14px;
            color: #718096;
            margin: 5px 0;
        }}
        .profile-company {{
            font-size: 14px;
            color: #2B5F47;
            font-weight: 500;
        }}
        .footer {{
            background-color: #f7fafc;
            padding: 25px 30px;
            text-align: center;
            font-size: 13px;
            color: #718096;
        }}
        .footer-links {{
            margin-top: 15px;
        }}
        .footer-links a {{
            color: #FF4444;
            text-decoration: none;
            margin: 0 10px;
        }}
        @media (max-width: 600px) {{
            .signature-profile {{
                flex-direction: column;
                text-align: center;
            }}
            .profile-image {{
                margin-right: 0;
                margin-bottom: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <!-- Antler Logo -->
            <div style="width: 200px; height: 100px; margin: 0 auto 20px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                <img src="https://private-user-images.githubusercontent.com/85657906/483545740-7f9266fd-22e0-4860-b672-a37f1e6f265a.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTY0NTgyNDgsIm5iZiI6MTc1NjQ1Nzk0OCwicGF0aCI6Ii84NTY1NzkwNi80ODM1NDU3NDAtN2Y5MjY2ZmQtMjJlMC00ODYwLWI2NzItYTM3ZjFlNmYyNjVhLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA4MjklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwODI5VDA4NTkwOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTYxYTI3MGVkZWVlNzQ4MTA0Y2VhNjkzOWFjNzMzYmUwOTZmMmI2M2MwNDAxOTNkOGY2ZDI3ODhmZTVlNzU4MzQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.eL-WQF6eZxi2OUxVz3i9W1h10yHUqVLEL9I5o0nrs1E" alt="Antler Logo" style="width: 180px; height: auto; max-width: 100%; object-fit: contain;">
            </div>
            <h1>Startup Opportunity</h1>
        </div>
        
        <div class="content">
            <div class="greeting">
                Hi {recipient_name},
            </div>
            
            <div class="main-content">
                I came across your impressive work in AI and wanted to reach out about an exciting opportunity.
            </div>
            
            <div class="highlight-box">
                <strong>Antler</strong> is one of the most active early-stage AI investors globally, and we're constantly seeking to identify emerging founders before they incorporate a company or enter the traditional VC funnel.
            </div>
            
            <div class="main-content">
                Based on your technical contributions and community engagement, you seem like exactly the type of builder we're looking for. We're particularly interested in founders who are:
            </div>
            
            <ul class="criteria-list">
                <li>Publishing code and sharing ideas</li>
                <li>Launching tools and engaging with communities</li>
                <li>Building in the AI space with early-stage momentum</li>
            </ul>
            
            {f'<div class="custom-message"><strong>Personal note:</strong> {custom_message}</div>' if custom_message else ''}
            
            <div class="main-content">
                Would you be interested in discussing the possibility of building a startup with potential funding from Antler?
            </div>
            
            <div class="cta-section">
                <a href="mailto:lee.lagdameo@antler.co?subject=Re: Startup opportunity with Antler" class="cta-button" style="color: white;">
                    Let's Connect
                </a>
            </div>
            
            <div class="signature">
                <div class="signature-profile">
                    <!-- Lee Lagdameo Profile Image -->
                    <div style="width: 80px; height: 80px; border-radius: 50%; overflow: hidden; border: 3px solid #e2e8f0; margin-right: 20px;">
                        <img src="https://media.licdn.com/dms/image/v2/D5603AQGASmfjPL2yKw/profile-displayphoto-shrink_200_200/profile-displayphoto-shrink_200_200/0/1680498963640?e=1759363200&v=beta&t=V3cwn2iF5qXFvQo5_ahbSco7vQ3TCRSeioMGA2PLMVU" alt="Lee Lagdameo" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <div class="profile-info">
                        <div class="profile-name">Lee Lagdameo</div>
                        <div class="profile-title">Investor Relationship Manager</div>
                        <div class="profile-company">Antler</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 Antler. Building the world's most exceptional startups.</p>
            <div class="footer-links">
                <a href="https://antler.co">antler.co</a> |
                <a href="mailto:australia@antler.co">australia@antler.co</a> |
                <a href="https://linkedin.com/company/antler">LinkedIn</a>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def validate_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get_configuration_status(self) -> Dict[str, any]:
        """Get email service configuration status"""
        return {
            "configured": self.is_configured,
            "service": "Resend",
            "api_key_configured": bool(self.resend_api_key),
            "tracking_enabled": self.tracking_enabled,
            "tracking_domain": self.tracking_domain,
            "default_sender": self.default_sender_email
        }