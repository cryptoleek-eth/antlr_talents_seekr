#!/usr/bin/env python3
"""
Real Email Test - Send emails between real addresses
This script allows you to test the email service with real email addresses.

IMPORTANT: You need to verify your sender domain in Resend first!
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append('/home/dev/coding/talent-seekr')

from api.services.email_service import EmailService

def get_user_input():
    """Get email details from user input"""
    print("📧 Real Email Test Setup")
    print("=" * 40)
    
    # Get sender email (must be verified in Resend)
    print("\n📤 SENDER INFORMATION:")
    print("⚠️  Important: The sender email domain must be verified in your Resend account!")
    print("   For testing, you can use: onboarding@resend.dev (pre-verified)")
    
    sender_email = input("Enter sender email: ").strip()
    if not sender_email:
        sender_email = "onboarding@resend.dev"
        print(f"Using default: {sender_email}")
    
    sender_name = input("Enter sender name (optional): ").strip()
    if not sender_name:
        sender_name = "TalentSeeker Test"
    
    # Get recipient email
    print("\n📥 RECIPIENT INFORMATION:")
    recipient_email = input("Enter recipient email: ").strip()
    if not recipient_email:
        print("❌ Recipient email is required!")
        return None
    
    recipient_name = input("Enter recipient name (optional): ").strip()
    if not recipient_name:
        recipient_name = "Test Recipient"
    
    # Get email content
    print("\n📝 EMAIL CONTENT:")
    subject = input("Enter email subject: ").strip()
    if not subject:
        subject = "Test Email from TalentSeeker API"
    
    print("Enter email message (press Enter twice to finish):")
    message_lines = []
    while True:
        line = input()
        if line == "" and len(message_lines) > 0 and message_lines[-1] == "":
            break
        message_lines.append(line)
    
    # Remove the last empty line
    if message_lines and message_lines[-1] == "":
        message_lines.pop()
    
    message = "\n".join(message_lines)
    if not message:
        message = f"Hello {recipient_name},\n\nThis is a test email from the TalentSeeker API using Resend.\n\nIf you receive this email, the integration is working correctly!\n\nBest regards,\n{sender_name}"
    
    return {
        "sender_email": sender_email,
        "sender_name": sender_name,
        "recipient_email": recipient_email,
        "recipient_name": recipient_name,
        "subject": subject,
        "message": message
    }

async def send_real_email(email_data):
    """Send a real email using the provided data"""
    print("\n🚀 Sending Real Email")
    print("=" * 40)
    
    # Initialize email service
    email_service = EmailService()
    
    # Check configuration
    if not email_service.is_configured:
        print("❌ Email service not configured properly")
        print("Please check your RESEND_API_KEY in the .env file")
        return False
    
    print("✅ Email service configured with Resend")
    
    # Create HTML email body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{email_data['subject']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .content {{ background: white; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; }}
            .footer {{ margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; font-size: 12px; color: #6c757d; }}
            .highlight {{ background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📧 {email_data['subject']}</h2>
                <p><strong>From:</strong> {email_data['sender_name']} &lt;{email_data['sender_email']}&gt;</p>
                <p><strong>To:</strong> {email_data['recipient_name']} &lt;{email_data['recipient_email']}&gt;</p>
            </div>
            
            <div class="content">
                <p>Hello {email_data['recipient_name']},</p>
                
                <div style="white-space: pre-line;">{email_data['message']}</div>
                
                <div class="highlight">
                    <p><strong>🎉 This email was sent successfully using:</strong></p>
                    <ul>
                        <li>✅ TalentSeeker API</li>
                        <li>✅ Resend Email Service</li>
                        <li>✅ Real email addresses</li>
                        <li>✅ HTML formatting</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>This email was sent via TalentSeeker API using Resend.</p>
                <p>Test performed at: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Display email preview
    print(f"📤 From: {email_data['sender_name']} <{email_data['sender_email']}>")
    print(f"📥 To: {email_data['recipient_name']} <{email_data['recipient_email']}>")
    print(f"📝 Subject: {email_data['subject']}")
    print(f"📄 Message Preview: {email_data['message'][:100]}{'...' if len(email_data['message']) > 100 else ''}")
    
    # Confirm before sending
    confirm = input("\n❓ Send this email? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Email sending cancelled")
        return False
    
    print("\n📧 Sending email...")
    
    try:
        # Send the email
        success = await email_service.send_email(
            to_email=email_data['recipient_email'],
            subject=email_data['subject'],
            body=html_body,
            sender_info={
                "name": email_data['sender_name'],
                "email": email_data['sender_email']
            },
            tracking_id=f"real-test-{int(__import__('time').time())}",
            is_html=True
        )
        
        if success:
            print("✅ Email sent successfully!")
            print(f"📬 Check the recipient's inbox: {email_data['recipient_email']}")
            print("📊 Monitor delivery in Resend dashboard: https://resend.com/emails")
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("\n🔧 Common issues:")
        print("   • Sender domain not verified in Resend")
        print("   • Invalid API key")
        print("   • Recipient email address invalid")
        print("   • Rate limiting (too many emails sent)")
        return False

async def main():
    """Main function"""
    print("🚀 TalentSeeker Real Email Test")
    print("=" * 50)
    
    # Important notice about domain verification
    print("\n⚠️  IMPORTANT SETUP REQUIREMENTS:")
    print("   1. Your sender domain must be verified in Resend")
    print("   2. For testing, you can use 'onboarding@resend.dev' (pre-verified)")
    print("   3. To use your own domain, verify it at: https://resend.com/domains")
    print("   4. Make sure your RESEND_API_KEY is valid")
    
    # Get email details from user
    email_data = get_user_input()
    if not email_data:
        print("❌ Invalid input. Exiting.")
        return False
    
    # Send the email
    success = await send_real_email(email_data)
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 Real email test completed successfully!")
        print("\n💡 What this proves:")
        print("   ✅ Resend integration is working")
        print("   ✅ Real email delivery is functional")
        print("   ✅ HTML formatting is supported")
        print("   ✅ Your API is ready for production")
        
        print("\n🚀 Next steps:")
        print("   • Use the API endpoints for automated sending")
        print("   • Set up your own verified domain in Resend")
        print("   • Test with the /api/v1/outreach endpoints")
    else:
        print("❌ Real email test failed")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Verify your sender domain in Resend dashboard")
        print("   2. Check your RESEND_API_KEY is correct")
        print("   3. Ensure recipient email is valid")
        print("   4. Check Resend account limits and status")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)