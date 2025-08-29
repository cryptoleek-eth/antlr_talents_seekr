# Testing the Email Service

The TalentSeeker API now uses Resend for email delivery. Here are several ways to test the email functionality:

## 🚀 Method 1: Using the API Endpoints

### Prerequisites
1. Make sure the API server is running: `http://localhost:8001`
2. Get an API key from the `/api/v1/auth/api-key` endpoint
3. Use the API documentation at `http://localhost:8001/docs`

### Test Individual Email via `/api/v1/outreach/contact`

```bash
curl -X POST "http://localhost:8001/api/v1/outreach/contact" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "talent_id": "test-talent-123",
    "email": "delivered@resend.dev",
    "name": "Test Developer",
    "subject": "Test Email from TalentSeeker",
    "message": "This is a test email to verify our email service is working.",
    "outreach_type": "email",
    "personalization_data": {
      "skills": "Python, FastAPI",
      "experience": "5 years"
    }
  }'
```

### Test Email Campaign via `/api/v1/outreach/campaign`

```bash
curl -X POST "http://localhost:8001/api/v1/outreach/campaign" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Email Campaign",
    "description": "Testing email functionality",
    "target_talent_ids": ["talent-1", "talent-2"],
    "outreach_type": "email",
    "template": {
      "subject": "Opportunity for {name}",
      "body": "Hi {name}, we have an exciting opportunity for someone with {skills}."
    },
    "personalization_data": {
      "talent-1": {"name": "John Doe", "skills": "Python", "email": "delivered@resend.dev"},
      "talent-2": {"name": "Jane Smith", "skills": "JavaScript", "email": "delivered@resend.dev"}
    }
  }'
```

## 🧪 Method 2: Quick Test Script

Create and run this simple test script:

```python
#!/usr/bin/env python3
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
sys.path.append('/home/dev/coding/talent-seekr')

from api.services.email_service import EmailService

async def quick_test():
    email_service = EmailService()
    
    # Check if configured
    if not email_service.is_configured:
        print("❌ Email service not configured")
        return
    
    print("✅ Email service configured with Resend")
    
    # Send test email
    success = await email_service.send_email(
        to_email="delivered@resend.dev",  # Resend test email
        subject="Quick Test Email",
        body="<h2>Test Email</h2><p>This is a quick test of the email service.</p>",
        sender_info={"name": "TalentSeeker", "email": "onboarding@resend.dev"},
        is_html=True
    )
    
    print(f"📧 Email sent: {'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(quick_test())
```

Save as `quick_email_test.py` and run: `python quick_email_test.py`

## 🌐 Method 3: Using the Web Interface

1. Open the API documentation: `http://localhost:8001/docs`
2. Click on "Authorize" and enter your API key
3. Navigate to the "outreach" section
4. Try the `/api/v1/outreach/contact` endpoint:
   - Click "Try it out"
   - Fill in the request body with test data
   - Use `delivered@resend.dev` as the email (Resend's test email)
   - Click "Execute"

## 📊 Method 4: Check Resend Dashboard

After sending emails, you can monitor delivery status:

1. Go to [Resend Dashboard](https://resend.com/emails)
2. Log in with your Resend account
3. View sent emails, delivery status, and analytics

## 🔍 Method 5: Check Server Logs

Monitor the API server logs for email sending activity:

```bash
# The server is already running, check the terminal output
# Look for log messages like:
# INFO: Email sent successfully via Resend
# INFO: Bulk email batch completed
```

## 📝 Test Email Addresses

Resend provides these test email addresses:
- `delivered@resend.dev` - Always delivers successfully
- `bounced@resend.dev` - Always bounces
- `complained@resend.dev` - Always marks as spam

## ⚙️ Configuration Check

To verify your email service configuration:

```python
from api.services.email_service import EmailService

email_service = EmailService()
config = email_service.get_configuration_status()
print(config)
```

Expected output:
```python
{
    'configured': True,
    'service': 'Resend',
    'api_key_configured': True,
    'tracking_enabled': True,
    'tracking_domain': 'localhost:8000',
    'default_sender': 'onboarding@resend.dev'
}
```

## 🚨 Troubleshooting

- **401 Unauthorized**: Check your `RESEND_API_KEY` in `.env`
- **Email not sending**: Verify API key is valid in Resend dashboard
- **Rate limiting**: Resend has sending limits, check your account status
- **Invalid sender**: Make sure sender email is verified in Resend

## 🎯 Production Testing

For production testing:
1. Use real email addresses (not test addresses)
2. Verify sender domain in Resend
3. Set up proper DNS records (SPF, DKIM, DMARC)
4. Monitor delivery rates and bounce rates
5. Test with different email providers (Gmail, Outlook, etc.)