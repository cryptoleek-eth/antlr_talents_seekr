# Startup Founder Template Example

## 🚀 Antler AI Founder Outreach

This template is specifically designed for reaching out to potential AI founders about startup opportunities with Antler funding.

## Template Details

**Template ID**: `startup_founder`
**Subject**: "Startup opportunity with Antler - {name}"

## Email Content

```
Hi {name},

I came across your impressive work in AI and wanted to reach out about an exciting opportunity.

Antler is one of the most active early-stage AI investors globally, and we're constantly seeking to identify emerging founders before they incorporate a company or enter the traditional VC funnel.

Based on your technical contributions and community engagement, you seem like exactly the type of builder we're looking for. We're particularly interested in founders who are:
• Publishing code and sharing ideas
• Launching tools and engaging with communities
• Building in the AI space with early-stage momentum

Would you be interested in discussing the possibility of building a startup with potential funding from Antler?

Best regards,
{sender_name}
```

## Usage Example

```bash
curl -X POST "http://localhost:8001/api/v1/outreach/sendEmail" \
  -H "Content-Type: application/json" \
  -d '{
    "send_to_email": "founder@example.com",
    "name": "Sarah Johnson",
    "company": "Antler",
    "position": "AI Founder",
    "template_id": "startup_founder",
    "message": "Your recent work on AI tools and community engagement really caught our attention."
  }'
```

## Perfect For

✅ **AI Developers** - Building tools and libraries  
✅ **Community Builders** - Engaging on GitHub, Twitter, Discord  
✅ **Early Innovators** - Sharing ideas and launching projects  
✅ **Technical Founders** - Before company incorporation  
✅ **Non-LinkedIn Talent** - Active on alternative platforms  

## Key Benefits

🎯 **Targeted Messaging** - Specifically for AI founders  
💰 **Funding Focus** - Clear mention of Antler investment  
🚀 **Startup Intent** - Asks about building companies  
🌐 **Platform Agnostic** - Reaches talent across all platforms  
📧 **Professional Tone** - Business-like but engaging  

## Template Variables Used

- `{name}` - Recipient's name
- `{sender_name}` - Your name/company
- Custom message can be appended for personalization

## Response Tracking

The system will track:
- Email delivery status
- Open rates
- Response rates
- Template effectiveness

This helps optimize your outreach strategy for finding the best AI founders.
