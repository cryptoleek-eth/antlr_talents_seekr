# sendEmail API Endpoint Examples

The new `sendEmail` endpoint provides a simple way to send emails using predefined templates.

## Endpoint

```
POST /api/v1/outreach/sendEmail
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `send_to_email` | string | ✅ | Recipient email address |
| `name` | string | ✅ | Recipient name |
| `company` | string | ❌ | Company name (default: TalentSeeker) |
| `position` | string | ❌ | Job position (default: Recruiter) |
| `message` | string | ❌ | Custom message to append |
| `template_id` | string | ❌ | Template to use (default: professional_intro) |

## Available Templates

### 1. startup_founder ⭐ NEW
- **Subject**: "Startup opportunity with Antler - {name}"
- **Use case**: Reaching out to potential AI founders about startup opportunities with Antler funding
- **Perfect for**: Early-stage AI builders, developers, and innovators

### 2. professional_intro
- **Subject**: "Exciting opportunity for {name}"
- **Use case**: General professional outreach

### 3. technical_role
- **Subject**: "Senior Developer Opportunity at {company}"
- **Use case**: Technical role recruitment

### 4. networking
- **Subject**: "Connecting with {name}"
- **Use case**: Professional networking

### 5. job_opportunity
- **Subject**: "Exciting {position} role at {company}"
- **Use case**: Specific job opportunities

## Examples

### Basic Usage

```bash
curl -X POST "http://localhost:8001/api/v1/outreach/sendEmail" \
  -H "Content-Type: application/json" \
  -d '{
    "send_to_email": "john.doe@example.com",
    "name": "John Doe"
  }'
```

### With Company and Position

```bash
curl -X POST "http://localhost:8001/api/v1/outreach/sendEmail" \
  -H "Content-Type: application/json" \
  -d '{
    "send_to_email": "jane.smith@example.com",
    "name": "Jane Smith",
    "company": "TechCorp",
    "position": "Senior Developer"
  }'
```

### Using Specific Template

```bash
curl -X POST "http://localhost:8001/api/v1/outreach/sendEmail" \
  -H "Content-Type: application/json" \
  -d '{
    "send_to_email": "bob.wilson@example.com",
    "name": "Bob Wilson",
    "company": "StartupXYZ",
    "position": "ML Engineer",
    "template_id": "job_opportunity"
  }'
```

### Startup Founder Outreach

```bash
curl -X POST "http://localhost:8001/api/v1/outreach/sendEmail" \
  -H "Content-Type: application/json" \
  -d '{
    "send_to_email": "alex.chen@example.com",
    "name": "Alex Chen",
    "company": "Antler",
    "position": "AI Founder",
    "template_id": "startup_founder",
    "message": "Your recent work on AI tools and community engagement really caught our attention."
  }'
```

### With Custom Message

```bash
curl -X POST "http://localhost:8001/api/v1/outreach/sendEmail" \
  -H "Content-Type: application/json" \
  -d '{
    "send_to_email": "alice.johnson@example.com",
    "name": "Alice Johnson",
    "company": "Innovation Labs",
    "position": "Full Stack Developer",
    "template_id": "technical_role",
    "message": "We have an exciting project involving React and Node.js that I think would be perfect for you."
  }'
```

## Response Format

### Success Response

```json
{
  "success": true,
  "message": "Email sent successfully to john.doe@example.com",
  "email_id": "contact-uuid-123",
  "template_used": "professional_intro",
  "subject": "Exciting opportunity for John Doe"
}
```

### Error Response

```json
{
  "detail": "Template 'invalid_template' not found. Available templates: ['professional_intro', 'technical_role', 'networking', 'job_opportunity']"
}
```

## Template Variables

The templates support these variables that get replaced with actual values:

- `{name}` - Recipient name
- `{company}` - Company name
- `{position}` - Job position
- `{sender_name}` - Sender name (default: TalentSeeker Team)

## Special Template: startup_founder

The `startup_founder` template is specifically designed for reaching out to potential AI founders about startup opportunities with Antler. It includes:

- **Antler Introduction**: Explains Antler's role as an early-stage AI investor
- **Founder Criteria**: Lists what Antler looks for in founders
- **Call to Action**: Asks about interest in building a startup with funding
- **Professional Tone**: Maintains a business-like approach while being engaging

## Testing

1. Make sure your API server is running: `http://localhost:8001`
2. Use the test script: `python test_send_email.py`
3. Or use curl commands above with real email addresses

## Notes

- The endpoint uses the existing email service (Resend)
- Emails are sent from `onboarding@resend.dev` by default
- Template rendering is simple string formatting
- All emails include tracking capabilities
- The system logs all email activities for monitoring
