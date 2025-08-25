# Setup & Deployment Guide

## Quick Start (3-Day MVP)

### Prerequisites
- Python 3.9 or higher
- Git
- Notion workspace access
- GitHub account
- Text editor or IDE

### Day 1 Setup (30 minutes)

#### 1. Project Setup
```bash
# Clone or create project directory
mkdir talent-seekr
cd talent-seekr

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create project structure
mkdir -p core plugins config utils data
touch main.py requirements.txt config.yaml .env
touch core/__init__.py plugins/__init__.py config/__init__.py utils/__init__.py
```

#### 2. Install Dependencies
```bash
# requirements.txt
pip install -r requirements.txt
```

Create `requirements.txt`:
```
# Core dependencies
notion-client>=2.2.1
python-dotenv>=1.0.0
pyyaml>=6.0.1
requests>=2.31.0
httpx>=0.25.0

# GitHub integration
PyGithub>=1.59.1

# Web scraping (for Twitter)
beautifulsoup4>=4.12.2
lxml>=4.9.3

# Data processing
pandas>=2.1.0

# Development tools
pytest>=7.4.0
pytest-mock>=3.11.1
black>=23.7.0
flake8>=6.0.0
mypy>=1.5.0
```

#### 3. Environment Configuration
Create `.env` file:
```bash
# Notion Integration
NOTION_TOKEN=your_notion_integration_token_here
NOTION_DATABASE_ID=your_database_id_here

# GitHub Integration
GITHUB_TOKEN=your_github_personal_access_token_here

# Twitter Integration (optional)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

#### 4. Basic Configuration
Create `config.yaml`:
```yaml
pipeline:
  schedule: "0 2 * * 0"  # Weekly Sunday 2 AM
  score_threshold: 60
  batch_size: 50
  max_talents_per_run: 100

sources:
  github:
    enabled: true
    rate_limit: 5000
    search_queries:
      - "machine learning location:Australia"
      - "artificial intelligence location:Australia"
      - "tensorflow location:Australia"
      - "pytorch location:Australia"
    min_repos: 2
    min_commits: 10
  
  twitter:
    enabled: true
    scraping_method: "web"
    search_keywords:
      - "machine learning Australia"
      - "AI startup Australia"
      - "GPT finetuning"
    max_results_per_search: 50
    delay_between_requests: 2

notion:
  page_size: 100
  retry_attempts: 3
  timeout_seconds: 30

au_detection:
  email_domains: [".edu.au", ".com.au", ".org.au"]
  locations: 
    - "Australia"
    - "Sydney"
    - "Melbourne"
    - "Brisbane"
    - "Perth"
    - "Adelaide"
    - "Canberra"
  universities:
    - "UNSW"
    - "University of Sydney" 
    - "University of Melbourne"
    - "ANU"
    - "Monash"
    - "UTS"
  organizations:
    - "CSIRO"
    - "Data61"
    - "Atlassian"
    - "Canva"

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/talent-seekr.log"
```

## Development Setup

### IDE Configuration

#### VS Code Setup
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.linting.mypyEnabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".mypy_cache": true
    }
}
```

Create `.vscode/launch.json` for debugging:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Pipeline",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "args": ["--sources", "github,twitter"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### Git Setup
Create `.gitignore`:
```bash
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/
.mypy_cache/

# Environment variables
.env
.env.local
.env.production

# Data and logs
data/
logs/
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
temp/
```

Initialize git repository:
```bash
git init
git add .
git commit -m "Initial project setup"
```

## Local Development

### Running the Pipeline
```bash
# Full pipeline with all enabled sources
python main.py

# Specific sources only
python main.py --sources github

# GitHub and Twitter only  
python main.py --sources github,twitter

# With custom score threshold
python main.py --score-threshold 70

# Dry run (no database writes)
python main.py --dry-run

# Verbose logging
python main.py --verbose
```

### Development Commands
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=core --cov=plugins

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy core/ plugins/

# Run all quality checks
./scripts/quality-check.sh
```

### Development Database
For local development, create a test Notion database:
```bash
# 1. Duplicate your main talent database
# 2. Name it "Talent Pipeline - Dev"
# 3. Update .env with dev database ID:
NOTION_DATABASE_ID_DEV=your_dev_database_id_here

# 4. Use environment-specific config:
python main.py --env development
```

## Testing Setup

### Test Environment
Create `config_test.yaml`:
```yaml
pipeline:
  score_threshold: 0  # Include all for testing
  batch_size: 10
  max_talents_per_run: 5

sources:
  github:
    enabled: true
    rate_limit: 100  # Lower for testing
    search_queries:
      - "test location:Australia"
  
  twitter:
    enabled: false  # Disable for unit tests

notion:
  timeout_seconds: 10
  retry_attempts: 1
```

### Running Tests
```bash
# Unit tests only
pytest tests/unit/

# Integration tests (requires API access)
pytest tests/integration/

# All tests
pytest

# With coverage report
pytest --cov=core --cov=plugins --cov-report=html

# Specific test file
pytest tests/unit/test_scoring.py

# Specific test function
pytest tests/unit/test_scoring.py::test_calculate_talent_score
```

### Test Data Setup
```bash
# Create test fixtures
mkdir tests/fixtures
mkdir tests/fixtures/github_responses
mkdir tests/fixtures/twitter_responses

# Add sample API responses for testing
```

## Production Deployment

### Option 1: Cloud VM Deployment (Recommended)

#### AWS EC2 Setup
```bash
# 1. Launch EC2 instance
# - Instance type: t3.small (2 vCPU, 2 GB RAM)
# - OS: Ubuntu 22.04 LTS
# - Storage: 20 GB GP3
# - Security group: SSH (22) from your IP only

# 2. Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. System setup
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.9 python3.9-venv python3-pip git

# 4. Clone project
git clone https://github.com/your-org/talent-seekr.git
cd talent-seekr

# 5. Setup application
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure environment
sudo cp .env.production .env
sudo nano .env  # Add your API keys

# 7. Setup logging
sudo mkdir -p /var/log/talent-seekr
sudo chown ubuntu:ubuntu /var/log/talent-seekr
```

#### Cron Job Setup
```bash
# Edit crontab
crontab -e

# Add weekly job (Sunday 2 AM AEST)
0 2 * * 0 /home/ubuntu/talent-seekr/scripts/run-pipeline.sh >> /var/log/talent-seekr/cron.log 2>&1
```

Create `/home/ubuntu/talent-seekr/scripts/run-pipeline.sh`:
```bash
#!/bin/bash
set -e

# Navigate to project directory
cd /home/ubuntu/talent-seekr

# Activate virtual environment
source venv/bin/activate

# Run pipeline
python main.py --env production 2>&1

# Log completion
echo "Pipeline completed at $(date)"
```

Make executable:
```bash
chmod +x scripts/run-pipeline.sh
```

### Option 2: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Run pipeline
CMD ["python", "main.py"]
```

#### Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  talent-seekr:
    build: .
    environment:
      - NOTION_TOKEN=${NOTION_TOKEN}
      - NOTION_DATABASE_ID=${NOTION_DATABASE_ID}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

#### Container Commands
```bash
# Build image
docker build -t talent-seekr .

# Run container
docker run --env-file .env talent-seekr

# Using docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Run one-time pipeline
docker-compose run talent-seekr python main.py --sources github
```

### Option 3: Serverless Deployment

#### AWS Lambda Setup
Create `lambda_handler.py`:
```python
import json
import logging
import os
from main import TalentPipeline

def lambda_handler(event, context):
    """AWS Lambda handler for talent discovery pipeline"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = {
            'notion': {
                'token': os.environ['NOTION_TOKEN'],
                'database_id': os.environ['NOTION_DATABASE_ID']
            },
            'github': {
                'token': os.environ['GITHUB_TOKEN']
            }
        }
        
        # Run pipeline
        pipeline = TalentPipeline(config)
        results = pipeline.run_discovery()
        
        logger.info(f"Pipeline completed: {results}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pipeline completed successfully',
                'results': results
            })
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
```

#### Lambda Deployment Package
```bash
# Create deployment package
mkdir lambda-package
cd lambda-package

# Copy code
cp -r ../core ../plugins ../utils .
cp ../main.py ../lambda_handler.py .

# Install dependencies
pip install -r ../requirements.txt -t .

# Create zip file
zip -r talent-seekr-lambda.zip .

# Upload to AWS Lambda via console or CLI
aws lambda update-function-code \
    --function-name talent-seekr \
    --zip-file fileb://talent-seekr-lambda.zip
```

## Monitoring & Maintenance

### Health Checks
Create `scripts/health-check.sh`:
```bash
#!/bin/bash

# Check if pipeline is running
if pgrep -f "main.py" > /dev/null; then
    echo "Pipeline is running"
    exit 0
else
    echo "Pipeline is not running"
    exit 1
fi
```

### Log Monitoring
Create `scripts/check-logs.sh`:
```bash
#!/bin/bash

LOG_FILE="/var/log/talent-seekr/talent-seekr.log"
ERROR_LOG="/var/log/talent-seekr/errors.log"

# Check for recent errors
if tail -n 100 "$LOG_FILE" | grep -i error > "$ERROR_LOG"; then
    echo "Errors found in last 100 log lines:"
    cat "$ERROR_LOG"
    
    # Send alert (configure email/Slack webhook)
    # curl -X POST -H 'Content-type: application/json' \
    #     --data '{"text":"Talent-Seekr pipeline errors detected"}' \
    #     YOUR_SLACK_WEBHOOK_URL
fi
```

### Backup Script
Create `scripts/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp .env "$BACKUP_DIR/env_$DATE"
cp config.yaml "$BACKUP_DIR/config_$DATE.yaml"

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/

# Backup data (if using local SQLite)
if [ -f "data/talents.db" ]; then
    cp "data/talents.db" "$BACKUP_DIR/talents_$DATE.db"
fi

# Clean old backups (keep last 30 days)
find "$BACKUP_DIR" -name "*" -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

### System Monitoring
Create `scripts/system-monitor.sh`:
```bash
#!/bin/bash

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "WARNING: Disk usage is ${DISK_USAGE}%"
fi

# Check memory usage
MEM_USAGE=$(free | awk '/Mem:/ {printf "%.1f", $3/$2*100}')
if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "WARNING: Memory usage is ${MEM_USAGE}%"
fi

# Check API rate limits
python -c "
from core.github_client import GitHubClient
client = GitHubClient()
limits = client.check_rate_limits()
if limits['remaining'] < 500:
    print(f'WARNING: GitHub rate limit low: {limits[\"remaining\"]} remaining')
"
```

## Performance Optimization

### Database Optimization
```python
# Use connection pooling for Notion API
from notion_client import Client
import asyncio

class OptimizedNotionClient:
    def __init__(self, token, max_connections=10):
        self.client = Client(auth=token)
        self.semaphore = asyncio.Semaphore(max_connections)
        
    async def batch_create_with_semaphore(self, talents):
        """Create talents with connection limiting"""
        async def create_single(talent):
            async with self.semaphore:
                return await self.create_talent_record(talent)
        
        tasks = [create_single(talent) for talent in talents]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

### Caching Strategy
```python
# Cache GitHub user data
from functools import lru_cache
import pickle
import os

class CachedGitHubClient:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cached_user(self, username):
        """Get user from cache or API"""
        cache_file = f"{self.cache_dir}/{username}.pkl"
        
        # Check if cache exists and is fresh (< 7 days)
        if os.path.exists(cache_file):
            if time.time() - os.path.getmtime(cache_file) < 604800:  # 7 days
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        
        # Fetch from API and cache
        user_data = self.fetch_user_from_api(username)
        with open(cache_file, 'wb') as f:
            pickle.dump(user_data, f)
        
        return user_data
```

## Troubleshooting

### Common Issues

#### 1. Notion API Errors
```bash
# Error: "Invalid token"
# Solution: Check NOTION_TOKEN in .env file
echo $NOTION_TOKEN

# Error: "Database not found"  
# Solution: Verify database ID and permissions
python -c "
from notion_client import Client
client = Client(auth='$NOTION_TOKEN')
print(client.databases.query(database_id='$NOTION_DATABASE_ID'))
"
```

#### 2. GitHub API Rate Limits
```bash
# Check current rate limit
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/rate_limit

# Solution: Wait for reset or implement better rate limiting
```

#### 3. Memory Issues
```bash
# Monitor memory usage during pipeline
python -m memory_profiler main.py

# Solution: Process in smaller batches
# Edit config.yaml: batch_size: 20
```

#### 4. Network Timeouts
```bash
# Test connectivity
curl -I https://api.github.com
curl -I https://api.notion.com

# Solution: Implement retry logic and increase timeouts
```

### Debug Mode
```bash
# Run with debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG
python main.py --verbose

# Profile performance
python -m cProfile -o profile_stats main.py
python -c "
import pstats
p = pstats.Stats('profile_stats')
p.sort_stats('cumulative').print_stats(20)
"
```

This comprehensive setup guide provides everything needed to deploy and maintain the Talent-Seekr pipeline in various environments, from local development to production cloud deployment.