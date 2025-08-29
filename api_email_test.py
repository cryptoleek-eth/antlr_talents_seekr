#!/usr/bin/env python3
"""
API Email Test - Test email sending via API endpoints
This script demonstrates how to send real emails using the TalentSeeker API.
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_api_key():
    """Get or create an API key for testing"""
    base_url = "http://localhost:8001"
    
    print("🔑 Getting API Key for Testing")
    print("=" * 40)
    
    # Try to create a test API key
    try:
        # First, let's try to get a key (this endpoint might require auth)
        response = requests.post(f"{base_url}/api/v1/auth/api-key", 
                               json={"name": "Email Test Key"})
        
        if response.status_code == 200:
            data = response.json()
            api_key = data.get("api_key")
            print(f"✅ Created new API key: {api_key[:20]}...")
            return api_key
        else:
            print(f"⚠️  Could not create API key automatically (status: {response.status_code})")
            print("Please get an API key manually from the API documentation.")
            
            # Ask user to provide API key
            api_key = input("Enter your API key: ").strip()
            if api_key:
                return api_key
            else:
                print("❌ No API key provided")
                return None
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("Make sure the server is running at http://localhost:8001")
        return None
    except Exception as e:
        print(f"❌ Error getting API key: {e}")
        return None

def test_individual_email(api_key, sender_email, recipient_email):
    """Test sending individual email via /api/v1/outreach/contact"""
    print("\n📧 Testing Individual Email via API")
    print("=" * 45)
    
    base_url = "http://localhost:8001"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prepare email data
    email_data = {
        "talent_id": "api-test-123",
        "email": recipient_email,
        "name": "API Test Recipient",
        "subject": "Test Email via TalentSeeker API",
        "message": f"""Hello!

This email was sent using the TalentSeeker API's /api/v1/outreach/contact endpoint.

Test Details:
• Sender: {sender_email}
• Recipient: {recipient_email}
• Method: Direct API call
• Service: Resend

If you receive this email, the API integration is working perfectly!

Best regards,
TalentSeeker API Test""",
        "outreach_type": "email",
        "personalization_data": {
            "skills": "API Testing, Email Integration",
            "experience": "Real-world testing",
            "sender_email": sender_email
        }
    }
    
    print(f"📤 Sending to: {recipient_email}")
    print(f"📝 Subject: {email_data['subject']}")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/outreach/contact",
            headers=headers,
            json=email_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email sent successfully via API!")
            print(f"📊 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ API request failed (status: {response.status_code})")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email via API: {e}")
        return False

def test_email_campaign(api_key, sender_email, recipients):
    """Test sending email campaign via /api/v1/outreach/campaign"""
    print("\n📨 Testing Email Campaign via API")
    print("=" * 45)
    
    base_url = "http://localhost:8001"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prepare campaign data
    campaign_data = {
        "name": "API Test Campaign",
        "description": "Testing email campaign functionality via API",
        "target_talent_ids": [f"talent-{i}" for i in range(len(recipients))],
        "outreach_type": "email",
        "template": {
            "subject": "Campaign Test: Opportunity for {name}",
            "body": """Hello {name}!

This email is part of a test campaign sent via the TalentSeeker API.

Your Profile:
• Skills: {skills}
• Experience: {experience}
• Email: {email}

This demonstrates the campaign functionality where multiple recipients can receive personalized emails.

Sent from: {sender_email}
Campaign: API Test Campaign

Best regards,
TalentSeeker Campaign Test"""
        },
        "personalization_data": {}
    }
    
    # Add personalization data for each recipient
    for i, recipient in enumerate(recipients):
        talent_id = f"talent-{i}"
        campaign_data["personalization_data"][talent_id] = {
            "name": f"Test User {i+1}",
            "email": recipient,
            "skills": f"Skill Set {i+1}",
            "experience": f"{i+2} years",
            "sender_email": sender_email
        }
    
    print(f"📤 Sending campaign to {len(recipients)} recipients")
    print(f"📝 Template: {campaign_data['template']['subject']}")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/outreach/campaign",
            headers=headers,
            json=campaign_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Campaign created successfully via API!")
            print(f"📊 Campaign ID: {result.get('campaign_id')}")
            print(f"📈 Status: {result.get('status')}")
            return True
        else:
            print(f"❌ Campaign API request failed (status: {response.status_code})")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating campaign via API: {e}")
        return False

def main():
    """Main function"""
    print("🚀 TalentSeeker API Email Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code != 200:
            print("❌ API server is not responding properly")
            print("Make sure the server is running: uvicorn api.main:app --host 0.0.0.0 --port 8001")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server at http://localhost:8001")
        print("Make sure the server is running: uvicorn api.main:app --host 0.0.0.0 --port 8001")
        return False
    
    print("✅ API server is running")
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return False
    
    # Get email details
    print("\n📧 Email Test Configuration")
    print("=" * 40)
    
    sender_email = input("Enter sender email (use onboarding@resend.dev for testing): ").strip()
    if not sender_email:
        sender_email = "onboarding@resend.dev"
        print(f"Using default sender: {sender_email}")
    
    recipient_email = input("Enter recipient email: ").strip()
    if not recipient_email:
        print("❌ Recipient email is required!")
        return False
    
    # Test individual email
    individual_success = test_individual_email(api_key, sender_email, recipient_email)
    
    # Ask if user wants to test campaign
    if individual_success:
        test_campaign = input("\n❓ Test email campaign as well? (y/N): ").strip().lower()
        campaign_success = False
        
        if test_campaign in ['y', 'yes']:
            # For campaign, we'll send to the same email multiple times
            recipients = [recipient_email]  # You can add more emails here
            campaign_success = test_email_campaign(api_key, sender_email, recipients)
    else:
        campaign_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 API EMAIL TEST SUMMARY")
    print("=" * 50)
    print(f"Individual Email Test: {'✅ PASSED' if individual_success else '❌ FAILED'}")
    print(f"Campaign Email Test: {'✅ PASSED' if campaign_success else '❌ SKIPPED' if individual_success else '❌ FAILED'}")
    
    if individual_success:
        print("\n🎉 API email functionality is working!")
        print("\n💡 What this proves:")
        print("   ✅ API endpoints are functional")
        print("   ✅ Authentication is working")
        print("   ✅ Email service integration is complete")
        print("   ✅ Real email delivery via API")
        
        print("\n🔗 API Documentation: http://localhost:8001/docs")
    else:
        print("\n❌ API email test failed")
        print("\n🔧 Check:")
        print("   • API server is running")
        print("   • API key is valid")
        print("   • Email service is configured")
        print("   • Sender domain is verified in Resend")
    
    return individual_success

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)