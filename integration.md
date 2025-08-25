# Integration Guide

## Overview

This guide covers all external integrations required for Talent-Seekr, including API setup, authentication, and configuration for each data source and the Notion database.

## Notion Integration

### Setup Requirements
1. **Notion Account**: Team workspace with database creation permissions
2. **Notion API Key**: Internal integration token
3. **Database Setup**: Pre-configured talent database with proper schema

### Step 1: Create Notion Integration
```bash
# 1. Go to https://www.notion.so/my-integrations
# 2. Click "New Integration"  
# 3. Name: "Talent-Seekr"
# 4. Associated workspace: [Your VC workspace]
# 5. Capabilities: Read content, Update content, Insert content
# 6. Copy the "Internal Integration Token"
```

### Step 2: Create Talent Database
```sql
-- Database Name: "🎯 Talent Pipeline"
-- Properties to create:

Name (Title) - Primary identifier
Talent Score (Number, 0-100) - ML-generated score
Status (Select) - New, Contacted, Follow-up, Potential, Reject, Later
AU Connection (Number, 0-100%) - Australian connection strength  
GitHub Profile (URL) - Direct link to GitHub
Twitter Profile (URL) - Direct link to Twitter/X
AI Focus (Multi-select) - Infrastructure, Model Development, Applied AI
Recent Activity (Rich Text) - Summary of latest work/posts
Discovered Date (Date) - When found by system
Last Contact (Date) - Follow-up tracking
Assigned To (People) - Team member responsible
Notes (Rich Text) - Team observations and meeting notes
Source Platforms (Multi-select) - GitHub, Twitter, LinkedIn, etc.
```

### Step 3: Configure Database Access
```bash
# 1. In your Talent Database, click "..." → "Add connections"
# 2. Search for "Talent-Seekr" integration
# 3. Click "Confirm" to grant access
# 4. Copy Database ID from URL:
#    https://notion.so/workspace/DATABASE_ID?v=...
#    The DATABASE_ID is the 32-character string
```

### Step 4: Notion API Configuration
```python
# config.yaml
notion:
  token: "secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  database_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  page_size: 100
  retry_attempts: 3
  timeout_seconds: 30
```

### Notion Python Client Setup
```python
from notion_client import Client

class NotionTalentDB:
    def __init__(self, token: str, database_id: str):
        self.notion = Client(auth=token)
        self.database_id = database_id
        
    def create_talent_record(self, talent: Talent):
        """Create new talent record in Notion"""
        properties = {
            "Name": {
                "title": [{"text": {"content": talent.name}}]
            },
            "Talent Score": {"number": talent.score},
            "Status": {"select": {"name": "New"}},
            "AU Connection": {"number": talent.au_strength * 100},
            "GitHub Profile": {"url": talent.github_url},
            "Twitter Profile": {"url": talent.twitter_url},
            "AI Focus": {
                "multi_select": [
                    {"name": focus} for focus in talent.ai_focus_areas
                ]
            },
            "Recent Activity": {
                "rich_text": [{"text": {"content": talent.activity_summary}}]
            },
            "Discovered Date": {"date": {"start": talent.discovered_date.isoformat()}},
            "Source Platforms": {
                "multi_select": [{"name": source} for source in talent.sources]
            }
        }
        
        return self.notion.pages.create(
            parent={"database_id": self.database_id},
            properties=properties
        )
```

## GitHub Integration

### Setup Requirements  
1. **GitHub Account**: Personal or organization account
2. **Personal Access Token**: For API authentication
3. **API Rate Limits**: 5,000 requests/hour for authenticated requests

### Step 1: Create GitHub Personal Access Token
```bash
# 1. Go to https://github.com/settings/personal-access-tokens/tokens
# 2. Click "Generate new token" → "Generate new token (classic)"
# 3. Note: "Talent-Seekr API Access"
# 4. Expiration: Custom (1 year recommended)
# 5. Scopes needed:
#    - public_repo (read public repositories)
#    - user (read user profile information)
#    - user:email (access user email addresses)
# 6. Generate token and copy immediately
```

### Step 2: GitHub API Configuration
```python
# config.yaml
github:
  token: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  rate_limit: 5000  # requests per hour
  search_queries:
    - "machine learning location:Australia"
    - "artificial intelligence location:Australia"
    - "tensorflow location:Australia"
    - "pytorch location:Australia"
    - "transformers location:Australia"
  min_repos: 2
  min_commits: 10
  ai_keywords: 
    - "machine learning"
    - "artificial intelligence"  
    - "deep learning"
    - "neural network"
    - "tensorflow"
    - "pytorch"
    - "transformers"
    - "llm"
    - "gpt"
```

### GitHub API Client Setup
```python
from github import Github
import time
from typing import List, Dict

class GitHubTalentScout:
    def __init__(self, token: str):
        self.github = Github(token)
        self.rate_limit_remaining = 5000
        
    def search_au_ai_developers(self) -> List[Dict]:
        """Search for Australian AI developers"""
        developers = []
        
        for query in self.config.search_queries:
            try:
                users = self.github.search_users(
                    query=query,
                    sort="repositories",
                    order="desc"
                )
                
                for user in users[:50]:  # Limit per query
                    if self._is_rate_limited():
                        self._wait_for_rate_limit()
                    
                    user_data = self._get_user_details(user)
                    if self._is_au_connected(user_data):
                        developers.append(user_data)
                        
            except Exception as e:
                print(f"GitHub search error: {e}")
                
        return developers
    
    def _get_user_details(self, user) -> Dict:
        """Get detailed user information"""
        try:
            return {
                'name': user.name,
                'login': user.login,
                'email': user.email,
                'location': user.location,
                'bio': user.bio,
                'company': user.company,
                'blog': user.blog,
                'public_repos': user.public_repos,
                'followers': user.followers,
                'following': user.following,
                'created_at': user.created_at,
                'html_url': user.html_url,
                'repos': self._get_ai_repos(user)
            }
        except Exception as e:
            print(f"Error getting user details: {e}")
            return {}
```

## Twitter/X Integration

### Setup Requirements
1. **Twitter Developer Account**: Applied and approved
2. **API Access**: Basic tier (free) or higher
3. **Bearer Token**: For API authentication

### Step 1: Twitter Developer Account Setup
```bash
# Due to Twitter API changes in 2023, we'll use web scraping approach
# Alternative: Apply for Twitter Developer Account
# 1. Go to https://developer.twitter.com/
# 2. Apply for developer account
# 3. Create new app: "Talent-Seekr"
# 4. Generate Bearer Token
```

### Step 2: Web Scraping Approach (Recommended)
```python
# config.yaml
twitter:
  enabled: true
  scraping_method: "web"  # or "api" if you have access
  search_keywords:
    - "machine learning Australia"
    - "AI startup Australia"  
    - "GPT finetuning"
    - "LLM training"
    - "ML engineer Australia"
  au_indicators:
    - "Australia"
    - "Sydney"
    - "Melbourne" 
    - "Brisbane"
    - "Perth"
    - ".com.au"
    - ".edu.au"
  max_tweets_per_search: 100
  delay_between_requests: 2  # seconds
```

### Twitter Scraping Client
```python
import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict

class TwitterTalentScout:
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_au_ai_talent(self) -> List[Dict]:
        """Search for AU AI talent on Twitter"""
        profiles = []
        
        for keyword in self.config.search_keywords:
            try:
                # Use Twitter advanced search
                search_url = f"https://twitter.com/search?q={keyword}&src=typed_query&f=user"
                
                response = self.session.get(search_url)
                if response.status_code == 200:
                    # Parse profiles from search results
                    soup = BeautifulSoup(response.content, 'html.parser')
                    user_profiles = self._extract_user_profiles(soup)
                    profiles.extend(user_profiles)
                
                # Respect rate limits
                time.sleep(self.config.delay_between_requests)
                
            except Exception as e:
                print(f"Twitter search error: {e}")
                
        return profiles
    
    def _extract_user_profiles(self, soup) -> List[Dict]:
        """Extract user profiles from Twitter search results"""
        # Implementation depends on Twitter's current HTML structure
        # This is a simplified example
        profiles = []
        
        # Look for user profile elements
        for profile_element in soup.find_all('div', {'data-testid': 'UserCell'}):
            try:
                profile_data = {
                    'username': profile_element.find('span').text,
                    'display_name': profile_element.find('div').text,
                    'bio': profile_element.find('div', {'data-testid': 'UserDescription'}).text,
                    'url': f"https://twitter.com/{profile_element.find('span').text}"
                }
                profiles.append(profile_data)
            except Exception as e:
                continue
                
        return profiles
```

### Alternative: Twitter API v2 Setup (If Available)
```python
# If you have Twitter API access
import tweepy

class TwitterAPIClient:
    def __init__(self, bearer_token: str):
        self.client = tweepy.Client(bearer_token=bearer_token)
    
    def search_tweets(self, query: str, max_results: int = 100):
        """Search tweets with Twitter API v2"""
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                expansions=['author_id'],
                user_fields=['name', 'username', 'location', 'description']
            )
            
            return tweets
        except Exception as e:
            print(f"Twitter API error: {e}")
            return None
```

## Future Integrations

### LinkedIn Integration (Future)
```python
# config.yaml
linkedin:
  enabled: false  # Enable when ready
  api_method: "scraping"  # LinkedIn API is restricted
  search_queries:
    - "machine learning engineer Australia"
    - "AI researcher Australia"
    - "data scientist Australia"
  profile_indicators:
    - "AI"
    - "Machine Learning" 
    - "Data Science"
    - "Artificial Intelligence"
```

### Product Hunt Integration (Future)
```python
# config.yaml
producthunt:
  enabled: false
  api_token: "xxx"  # Product Hunt API token
  search_categories: ["ai", "machine-learning", "developer-tools"]
  au_indicators: [".com.au", "Australia", "Sydney", "Melbourne"]
```

### Reddit/HackerNews Integration (Future)
```python
# config.yaml
reddit:
  enabled: false
  client_id: "xxx"
  client_secret: "xxx"
  user_agent: "talent-seekr:v1.0"
  subreddits: ["MachineLearning", "artificial", "AusFintech"]

hackernews:
  enabled: false
  api_base: "https://hacker-news.firebaseio.com/v0"
  keywords: ["Show HN", "AI", "ML", "machine learning"]
```

## Configuration Management

### Environment Variables Setup
```bash
# .env file (DO NOT COMMIT TO VERSION CONTROL)
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_BEARER_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Development vs Production
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### Configuration Loading
```python
# config/settings.py
import os
from dotenv import load_dotenv
import yaml

load_dotenv()

def load_config():
    """Load configuration from YAML and environment variables"""
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables
    config['notion']['token'] = os.getenv('NOTION_TOKEN')
    config['notion']['database_id'] = os.getenv('NOTION_DATABASE_ID')
    config['github']['token'] = os.getenv('GITHUB_TOKEN')
    
    # Validate required configurations
    required_env_vars = ['NOTION_TOKEN', 'NOTION_DATABASE_ID', 'GITHUB_TOKEN']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    return config
```

## Rate Limiting & Error Handling

### GitHub Rate Limiting
```python
class GitHubRateLimiter:
    def __init__(self, github_client):
        self.github = github_client
        
    def check_rate_limit(self):
        """Check current rate limit status"""
        rate_limit = self.github.get_rate_limit()
        return {
            'remaining': rate_limit.core.remaining,
            'reset_time': rate_limit.core.reset,
            'limit': rate_limit.core.limit
        }
    
    def wait_if_needed(self):
        """Wait if rate limit is low"""
        status = self.check_rate_limit()
        
        if status['remaining'] < 100:  # Safety buffer
            sleep_time = (status['reset_time'] - datetime.now()).total_seconds()
            if sleep_time > 0:
                print(f"Rate limit low, waiting {sleep_time} seconds")
                time.sleep(sleep_time + 60)  # Extra buffer
```

### Notion Rate Limiting
```python
class NotionRateLimiter:
    def __init__(self):
        self.request_times = []
        self.max_requests_per_second = 3
        
    def make_request(self, func, *args, **kwargs):
        """Make rate-limited request to Notion API"""
        now = time.time()
        
        # Remove old requests (older than 1 second)
        self.request_times = [t for t in self.request_times if now - t < 1]
        
        # Wait if we're at the limit
        if len(self.request_times) >= self.max_requests_per_second:
            sleep_time = 1 - (now - self.request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Make the request
        self.request_times.append(now)
        return func(*args, **kwargs)
```

## Error Handling & Retry Logic

### Exponential Backoff
```python
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    """Decorator for exponential backoff retry logic"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise e
                    
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
                    time.sleep(delay)
            
        return wrapper
    return decorator

# Usage example
@retry_with_backoff(max_retries=3, base_delay=2)
def create_notion_page(self, properties):
    return self.notion.pages.create(
        parent={"database_id": self.database_id},
        properties=properties
    )
```

## Monitoring & Logging

### Structured Logging Setup
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_pipeline_event(self, event_type: str, data: dict):
        """Log structured pipeline events"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }
        self.logger.info(json.dumps(log_entry))

# Usage examples
logger = StructuredLogger('talent-seekr')

# Log successful discovery
logger.log_pipeline_event('talent_discovered', {
    'talent_name': 'John Smith',
    'source': 'github',
    'score': 85,
    'au_strength': 0.8
})

# Log API errors
logger.log_pipeline_event('api_error', {
    'source': 'github',
    'error_type': 'rate_limit_exceeded',
    'retry_count': 2
})
```

## Testing Integration Setup

### Test Configuration
```yaml
# config_test.yaml
notion:
  token: "test_token"
  database_id: "test_database_id"
  
github:
  token: "test_github_token"
  rate_limit: 100  # Lower for testing
  
twitter:
  enabled: false  # Disable for testing
  
pipeline:
  score_threshold: 0  # Include all for testing
  max_talents_per_run: 10  # Limit for testing
```

### Integration Test Examples
```python
import pytest
from unittest.mock import Mock, patch

class TestNotionIntegration:
    @patch('notion_client.Client')
    def test_create_talent_record(self, mock_notion):
        """Test Notion record creation"""
        # Setup mock
        mock_client = Mock()
        mock_notion.return_value = mock_client
        
        # Test talent creation
        notion_db = NotionTalentDB("test_token", "test_db_id")
        talent = Talent(name="Test User", score=85)
        
        result = notion_db.create_talent_record(talent)
        
        # Verify API was called correctly
        mock_client.pages.create.assert_called_once()
        
class TestGitHubIntegration:
    @patch('github.Github')
    def test_search_au_developers(self, mock_github):
        """Test GitHub user search"""
        # Setup mock responses
        mock_client = Mock()
        mock_github.return_value = mock_client
        
        # Mock search results
        mock_user = Mock()
        mock_user.name = "Test Developer"
        mock_user.location = "Sydney, Australia"
        mock_client.search_users.return_value = [mock_user]
        
        # Test search
        scout = GitHubTalentScout("test_token")
        results = scout.search_au_ai_developers()
        
        assert len(results) > 0
        assert results[0]['name'] == "Test Developer"
```

This comprehensive integration guide provides all the necessary setup instructions, code examples, and configuration details needed to connect Talent-Seekr with external data sources and the Notion database.