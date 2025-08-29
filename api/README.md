# Talent Discovery & Outreach API

A comprehensive REST API for discovering talents across multiple platforms (GitHub, Twitter) and managing automated outreach campaigns via email and social media.

## Features

- **Multi-Source Talent Discovery**: Search across GitHub and Twitter
- **Quality Scoring**: AI-powered talent quality assessment
- **Automated Outreach**: Email and Twitter DM campaigns
- **Campaign Management**: Track and analyze outreach performance
- **Authentication & Security**: API key-based authentication with role-based access
- **Rate Limiting**: Configurable rate limits per user role
- **Analytics**: Comprehensive usage and campaign analytics

## Quick Start

### Prerequisites

- Python 3.8+
- Access to GitHub API (token required)
- Twitter API credentials (optional)
- Notion workspace and database (for talent storage)
- SMTP server for email outreach (optional)

### Installation

1. **Clone and setup the main project**:
   ```bash
   cd talent-seekr
   pip install -r requirements.txt
   ```

2. **Install API dependencies**:
   ```bash
   cd api
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp ../.env.example .env
   # Edit .env with your API credentials
   ```

4. **Start the API server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the API documentation**:
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Environment Configuration

Create a `.env` file in the API directory with the following variables:

```env
# Required: GitHub API
GITHUB_TOKEN=your_github_token_here

# Required: Notion Integration
NOTION_TOKEN=your_notion_token_here
NOTION_DATABASE_ID=your_notion_database_id_here

# Optional: Twitter API
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# Optional: Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Optional: Jina AI (for enhanced search)
JINA_API_TOKEN=your_jina_token_here
```

## API Authentication

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "company": "Tech Corp",
    "role": "basic"
  }'
```

Response:
```json
{
  "success": true,
  "user_id": "user_123",
  "api_key": "tk_1234567890abcdef",
  "message": "User registered successfully"
}
```

### 2. Use API Key for Authentication

Include the API key in the Authorization header:

```bash
curl -H "Authorization: Bearer tk_1234567890abcdef" \
  "http://localhost:8000/api/v1/auth/me"
```

## API Usage Examples

### Talent Discovery

#### Search for Python Developers

```bash
curl -X POST "http://localhost:8000/api/v1/talents/search" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["python", "machine learning"],
    "sources": ["github"],
    "location": "Sydney",
    "min_quality_score": 0.7,
    "limit": 10
  }'
```

Response:
```json
{
  "success": true,
  "talents": [
    {
      "id": "talent_123",
      "name": "John Smith",
      "source": "github",
      "profile_url": "https://github.com/johnsmith",
      "skills": ["Python", "Machine Learning", "Django"],
      "location": "Sydney, Australia",
      "quality_metrics": {
        "overall_score": 0.85,
        "technical_score": 0.9,
        "activity_score": 0.8
      },
      "contact_info": {
        "email": "john@example.com",
        "twitter": "@johnsmith"
      }
    }
  ],
  "total_found": 1,
  "search_time_seconds": 3.2
}
```

### Outreach Campaigns

#### Create Email Campaign

```bash
curl -X POST "http://localhost:8000/api/v1/outreach/campaign" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python Developer Outreach Q1",
    "description": "Recruiting senior Python developers",
    "outreach_type": "email",
    "target_talent_ids": ["talent_123", "talent_456"],
    "email_template": {
      "subject": "Exciting Python Developer Opportunity at {company}",
      "body": "Hi {name},\n\nI came across your impressive work in {skills} and wanted to reach out about an exciting opportunity...\n\nBest regards,\n{sender_name}",
      "sender_name": "Jane Recruiter",
      "sender_email": "jane@techcorp.com"
    }
  }'
```

#### Send Individual Contact

```bash
curl -X POST "http://localhost:8000/api/v1/outreach/contact" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "talent_id": "talent_123",
    "outreach_type": "twitter_dm",
    "twitter_dm_template": {
      "message": "Hi {name}! Love your work on {skills}. Would you be interested in discussing a new opportunity? 🚀"
    }
  }'
```

### Campaign Analytics

#### Get Campaign Status

```bash
curl "http://localhost:8000/api/v1/outreach/campaign/campaign_123" \
  -H "Authorization: Bearer your_api_key"
```

#### Get User Analytics

```bash
curl "http://localhost:8000/api/v1/outreach/analytics?days=30" \
  -H "Authorization: Bearer your_api_key"
```

## API Endpoints

### Authentication (`/api/v1/auth`)

- `POST /register` - Register new user
- `POST /api-key` - Create new API key
- `GET /me` - Get user information
- `GET /api-keys` - List user's API keys
- `DELETE /api-key/{id}` - Revoke API key
- `POST /validate` - Validate API key

### Talent Discovery (`/api/v1/talents`)

- `POST /search` - Search for talents
- `GET /sources` - Get available sources
- `GET /stats` - Get discovery statistics
- `GET /export` - Export talent data

### Outreach Management (`/api/v1/outreach`)

- `POST /campaign` - Create outreach campaign
- `POST /contact` - Send individual contact
- `GET /campaign/{id}` - Get campaign status
- `GET /campaigns` - List campaigns
- `GET /analytics` - Get analytics
- `GET /templates` - Get message templates

### Documentation (`/api/v1/docs`)

- `GET /api-info` - API information
- `GET /usage` - Usage statistics
- `GET /examples` - Usage examples
- `GET /schemas` - API schemas
- `GET /errors` - Error codes

## Rate Limits

| User Role | Requests/Hour | Campaigns/Day | Contacts/Day |
|-----------|---------------|---------------|--------------|
| Basic     | 100           | 5             | 50           |
| Premium   | 1,000         | 25            | 500          |
| Enterprise| 10,000        | 100           | 5,000        |

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

Error responses include detailed information:

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 3600
}
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

```bash
black api/
flake8 api/
```

### Development Server

```bash
uvicorn main:app --reload --log-level debug
```

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Security Considerations

- Store API keys securely
- Use HTTPS in production
- Implement proper CORS policies
- Monitor for unusual usage patterns
- Regularly rotate API keys
- Validate all input data

## Support

For issues and questions:

1. Check the API documentation at `/docs`
2. Review error messages and status codes
3. Check rate limits and quotas
4. Verify environment configuration

## License

This project is licensed under the MIT License.