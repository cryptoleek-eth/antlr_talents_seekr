#!/usr/bin/env python3
"""
Quick Email Service Test
Run this script to test if the Resend email integration is working.
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

async def quick_test():
    """Quick test of the email service"""
    print("🧪 Quick Email Service Test")
    print("=" * 40)
    
    # Initialize email service
    email_service = EmailService()
    
    # Check configuration
    config = email_service.get_configuration_status()
    print("📋 Configuration:")
    for key, value in config.items():
        print(f"   • {key}: {value}")
    
    if not email_service.is_configured:
        print("\n❌ Email service not configured properly")
        print("Please check your RESEND_API_KEY in the .env file")
        return False
    
    print("\n✅ Email service configured with Resend")
    
    # Send test email
    print("\n📧 Sending test email...")
    try:
        success = await email_service.send_email(
            to_email="delivered@resend.dev",  # Resend's test email
            subject="Quick Test from TalentSeeker",
            body="""
            <h2>🎉 Email Test Successful!</h2>
            <p>This email confirms that your Resend integration is working correctly.</p>
            <p><strong>Test Details:</strong></p>
            <ul>
                <li>✅ API Key: Valid</li>
                <li>✅ Email Service: Operational</li>
                <li>✅ HTML Support: Working</li>
            </ul>
            <p>Your TalentSeeker API is ready to send emails! 🚀</p>
            """,
            sender_info={
                "name": "TalentSeeker Test",
                "email": "onboarding@resend.dev"
            },
            tracking_id="quick-test-" + str(int(asyncio.get_event_loop().time())),
            is_html=True
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print("📬 Check the Resend dashboard: https://resend.com/emails")
            print("💡 You can now use the email service in your API")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

async def main():
    """Main function"""
    success = await quick_test()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Email service is working correctly!")
        print("\n💡 Next steps:")
        print("   • Test via API: http://localhost:8001/docs")
        print("   • Send real emails using /api/v1/outreach/contact")
        print("   • Create campaigns using /api/v1/outreach/campaign")
    else:
        print("⚠️  Email service test failed")
        print("\n🔧 Troubleshooting:")
        print("   • Check RESEND_API_KEY in .env file")
        print("   • Verify API key in Resend dashboard")
        print("   • Ensure internet connection is working")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)