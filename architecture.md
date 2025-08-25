# System Architecture

## Overview

Talent-Seekr is built as a **modular data pipeline** with a **plugin-based architecture** that enables easy extension to new data sources. The system follows a **batch processing model** with **weekly discovery cycles**, outputting results to a **Notion database** for team collaboration.

## High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Data Sources  │───▶│  Plugin System   │───▶│ Scoring Engine  │───▶│ Notion Database  │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └──────────────────┘
       │                        │                       │                       │
   ┌───┴───┐              ┌─────┴─────┐           ┌─────┴─────┐           ┌─────┴─────┐
   │GitHub │              │ Talent    │           │AU Filter  │           │Team Views │
   │Twitter│              │Normalizer │           │ML Scoring │           │Workflow   │
   │Future │              │Dedup Logic│           │Quality    │           │Mobile App │
   └───────┘              └───────────┘           └───────────┘           └───────────┘
```

## Core Components

### 1. Plugin System
**Purpose**: Extensible architecture for adding new data sources
**Location**: `/plugins/`

#### Base Plugin Interface
```python
class SourcePlugin(ABC):
    def search(self, query_params: dict) -> List[Talent]
    def is_au_connected(self, raw_data: dict) -> float  
    def get_platform_score(self, talent: Talent) -> float
```

#### Plugin Implementations
- **GitHubPlugin**: GitHub API integration with repository analysis
- **TwitterPlugin**: Twitter/X scraping with AI keyword detection
- **Future Plugins**: LinkedIn, HackerNews, ProductHunt, etc.

#### Plugin Registration
```python
# Automatic plugin discovery and registration
AVAILABLE_PLUGINS = {
    'github': GitHubPlugin,
    'twitter': TwitterPlugin,
    'linkedin': LinkedInPlugin,  # Future
}
```

### 2. Data Pipeline Core
**Purpose**: Orchestrates data collection, processing, and output
**Location**: `/core/pipeline.py`

#### Pipeline Phases
```python
def run_discovery():
    # Phase 1: Data Collection
    raw_talents = []
    for plugin in enabled_plugins:
        raw_talents.extend(plugin.search(query_params))
    
    # Phase 2: Normalization  
    normalized_talents = [Talent.from_raw(data) for data in raw_talents]
    
    # Phase 3: Deduplication
    unique_talents = deduplicate_talents(normalized_talents)
    
    # Phase 4: Scoring
    for talent in unique_talents:
        talent.score = scoring_engine.calculate_score(talent)
    
    # Phase 5: Quality Filtering
    qualified_talents = filter_by_quality(unique_talents)
    
    # Phase 6: Database Sync
    notion_client.batch_create_talents(qualified_talents)
```

### 3. Data Models
**Purpose**: Standardized data structures across all plugins
**Location**: `/core/talent.py`

#### Core Talent Model
```python
@dataclass
class Talent:
    # Identity
    name: str
    email: Optional[str] = None
    
    # Platform Links
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    # AU Connection
    au_strength: float = 0.0  # 0-1 score
    location: Optional[str] = None
    au_signals: List[str] = field(default_factory=list)
    
    # Scoring
    github_score: float = 0.0
    twitter_score: float = 0.0
    total_score: float = 0.0
    
    # Metadata
    platform_data: Dict = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    discovered_date: datetime = field(default_factory=datetime.now)
    
    # Status (managed in Notion)
    status: str = "new"
    notes: str = ""
```

### 4. Scoring Engine
**Purpose**: Multi-factor scoring algorithm with ML capabilities
**Location**: `/core/scoring.py`

#### Scoring Algorithm
```python
def calculate_talent_score(talent: Talent) -> float:
    """
    Weighted scoring across multiple dimensions:
    - Technical Depth (30%): GitHub activity, repo quality, AI focus
    - Founder Intent (40%): Building signals, launches, community engagement  
    - Commercial Awareness (20%): GTM experiments, user feedback
    - AU Connection (10%): Geographic ties, ecosystem involvement
    """
    
    technical_score = calculate_technical_score(talent)      # 0-30
    founder_score = calculate_founder_intent_score(talent)   # 0-40  
    commercial_score = calculate_commercial_score(talent)    # 0-20
    au_score = talent.au_strength * 10                       # 0-10
    
    total = technical_score + founder_score + commercial_score + au_score
    return min(total, 100)
```

#### Platform-Specific Scoring
```python
# GitHub Technical Scoring
def score_github_activity(github_data):
    score = 0
    score += min(github_data.commits_last_month * 2, 20)  # Recent activity
    score += min(github_data.ai_repos_count * 3, 15)     # AI focus
    score += min(github_data.stars_received / 50, 10)    # Code quality
    score += 5 if github_data.has_readme else 0          # Documentation
    return score

# Twitter Founder Intent Scoring  
def score_twitter_engagement(twitter_data):
    score = 0
    score += min(twitter_data.ai_posts_count * 2, 15)     # AI content
    score += min(twitter_data.engagement_rate * 20, 10)   # Influence
    score += 10 if twitter_data.has_building_keywords else 0  # Building signals
    score += 5 if twitter_data.mentions_launches else 0  # Product launches
    return score
```

### 5. Australia Detection System
**Purpose**: Identify and score Australian connections
**Location**: `/utils/au_detection.py`

#### Multi-Signal AU Detection
```python
def calculate_au_strength(profile_data) -> float:
    """Returns 0-1 AU connection strength"""
    signals = []
    
    # Email domains (0.5 weight)
    if any(domain in profile_data.get('email', '') for domain in ['.edu.au', '.com.au']):
        signals.append(0.5)
    
    # Location metadata (0.4 weight)  
    location = str(profile_data.get('location', '')).lower()
    if any(city in location for city in AU_CITIES):
        signals.append(0.4)
    
    # Organization affiliations (0.3 weight)
    bio = str(profile_data.get('bio', '')).lower()  
    if any(org in bio for org in AU_ORGANIZATIONS):
        signals.append(0.3)
    
    # Timezone activity patterns (0.2 weight)
    if has_au_timezone_pattern(profile_data.get('activity_times', [])):
        signals.append(0.2)
    
    return min(sum(signals), 1.0)
```

### 6. Notion Integration
**Purpose**: Database operations and team workflow interface
**Location**: `/core/notion_client.py`

#### Notion Database Schema
```python
NOTION_PROPERTIES = {
    "Name": {"title": {}},
    "Talent Score": {"number": {"format": "number"}},
    "Status": {"select": {"options": [
        {"name": "New", "color": "blue"},
        {"name": "Contacted", "color": "yellow"}, 
        {"name": "Follow-up", "color": "orange"},
        {"name": "Potential", "color": "green"},
        {"name": "Reject", "color": "red"},
        {"name": "Later", "color": "gray"}
    ]}},
    "AU Connection": {"number": {"format": "percent"}},
    "GitHub Profile": {"url": {}},
    "Twitter Profile": {"url": {}},
    "AI Focus": {"multi_select": {"options": [
        {"name": "Infrastructure", "color": "blue"},
        {"name": "Model Development", "color": "green"},
        {"name": "Applied AI", "color": "purple"}
    ]}},
    "Recent Activity": {"rich_text": {}},
    "Discovered Date": {"date": {}},
    "Last Contact": {"date": {}},
    "Assigned To": {"people": {}},
    "Notes": {"rich_text": {}},
    "Source Platforms": {"multi_select": {}}
}
```

## System Flow

### Weekly Discovery Pipeline
```
Sunday 2:00 AM (AEST)
├─ 1. Configuration Load
│  ├─ Load enabled plugins
│  ├─ Set query parameters  
│  └─ Initialize API clients
├─ 2. Data Collection (2-4 hours)
│  ├─ GitHub: Search AU AI developers
│  ├─ Twitter: Scrape AI-related content
│  └─ Future: LinkedIn, HN, etc.
├─ 3. Data Processing (30 minutes)
│  ├─ Normalize to Talent objects
│  ├─ Deduplicate across platforms
│  └─ Calculate AU strength scores
├─ 4. Scoring Phase (15 minutes)
│  ├─ Platform-specific scoring
│  ├─ Combined multi-factor scoring
│  └─ Quality threshold filtering
├─ 5. Database Operations (15 minutes)
│  ├─ Check existing Notion entries
│  ├─ Create new talent records
│  └─ Update changed scores
└─ 6. Reporting
   ├─ Pipeline success metrics
   ├─ New talent summary
   └─ Error logs and alerts
```

### Real-Time Operations
```
Continuous Monitoring
├─ API Health Checks
├─ Rate Limit Monitoring  
├─ Error Rate Tracking
└─ Manual Pipeline Triggers

Notion Sync
├─ Status Change Detection
├─ Note Updates
├─ Team Assignment Changes
└─ Follow-up Date Tracking
```

## Technology Stack

### Backend Infrastructure
- **Language**: Python 3.9+
- **Framework**: FastAPI (for future API endpoints)
- **Database**: Notion (primary), SQLite (local caching)
- **Task Queue**: Python schedule (batch processing)
- **Configuration**: YAML + python-dotenv

### External Integrations
- **Notion API**: `notion-client` library
- **GitHub API**: `PyGithub` library  
- **Twitter Scraping**: `requests` + `beautifulsoup4`
- **HTTP Client**: `httpx` (async capabilities)
- **Data Processing**: `pandas` (optional, for complex analysis)

### Development Tools
- **Testing**: `pytest` + `pytest-mock`
- **Code Quality**: `black` + `flake8` + `mypy`
- **Dependency Management**: `pip` + `requirements.txt`
- **Environment**: `python-dotenv` for configuration
- **Logging**: Python `logging` module with structured output

## Security Architecture

### API Key Management
```python
# Environment Variables (.env file)
NOTION_TOKEN=secret_xxx
GITHUB_TOKEN=ghp_xxx  
TWITTER_BEARER_TOKEN=xxx

# Secure Loading
from dotenv import load_dotenv
load_dotenv()

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
if not NOTION_TOKEN:
    raise ValueError("NOTION_TOKEN required")
```

### Rate Limit Management
```python
class RateLimitedClient:
    def __init__(self, requests_per_hour: int):
        self.requests_per_hour = requests_per_hour
        self.request_times = []
    
    def make_request(self, func, *args, **kwargs):
        # Rate limiting logic
        self._wait_if_necessary()
        self.request_times.append(time.time())
        
        # Exponential backoff retry
        return self._retry_with_backoff(func, *args, **kwargs)
```

### Data Privacy
- **Public Data Only**: No private repositories or protected tweets
- **No PII Storage**: Names and public profiles only
- **AU Focus**: Geographic filtering reduces data scope
- **Retention Policy**: Indefinite storage for relationship building

## Scalability Considerations

### Current Scale (MVP)
- **Weekly Processing**: ~100-500 profiles per source
- **Database Size**: ~1000-5000 talent records per year
- **API Usage**: Well within GitHub/Twitter limits
- **Processing Time**: <4 hours per weekly batch

### Future Scale (Production)
- **Multi-Region**: Expand beyond Australia
- **More Sources**: 10+ platforms integrated
- **Real-Time Processing**: Daily or hourly updates
- **ML Enhancement**: Feedback-driven scoring improvements

### Performance Optimizations
```python
# Async Processing
async def process_talents_async(talents):
    tasks = []
    async with httpx.AsyncClient() as client:
        for talent in talents:
            task = asyncio.create_task(
                score_talent_async(client, talent)
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks)

# Caching Strategy
@lru_cache(maxsize=1000)
def get_github_user_data(username: str):
    # Cache expensive API calls
    return github_api.get_user(username)
```

## Error Handling & Monitoring

### Exception Handling
```python
class PipelineError(Exception):
    """Base exception for pipeline errors"""
    pass

class PluginError(PipelineError):
    """Plugin-specific errors"""
    def __init__(self, plugin_name: str, message: str):
        self.plugin_name = plugin_name
        super().__init__(f"{plugin_name}: {message}")

# Graceful degradation
def run_plugin_safely(plugin):
    try:
        return plugin.search(query_params)
    except Exception as e:
        logger.error(f"Plugin {plugin.name} failed: {e}")
        # Continue with other plugins
        return []
```

### Health Monitoring
```python
def generate_pipeline_report():
    return {
        'timestamp': datetime.now(),
        'plugins_enabled': len(enabled_plugins),
        'talents_discovered': total_discovered,
        'talents_qualified': total_qualified, 
        'api_errors': error_count,
        'processing_time': execution_time,
        'success_rate': success_rate
    }
```

## Deployment Architecture

### Local Development
```bash
# Single machine deployment
python -m venv talent-seekr-env
source talent-seekr-env/bin/activate
pip install -r requirements.txt
python main.py --config config.yaml
```

### Production Deployment Options

#### Option 1: Cloud VM (Recommended)
- **Platform**: AWS EC2, Google Cloud, or DigitalOcean
- **Schedule**: Cron job for weekly execution
- **Monitoring**: CloudWatch or similar logging
- **Benefits**: Simple, cost-effective, easy debugging

#### Option 2: Serverless Functions
- **Platform**: AWS Lambda, Google Cloud Functions
- **Triggers**: CloudWatch Events (scheduled)
- **Storage**: External database for state management
- **Benefits**: Zero maintenance, pay-per-execution

#### Option 3: Container Deployment
- **Platform**: Docker + Kubernetes
- **Scheduling**: CronJob resources
- **Scaling**: Horizontal pod autoscaling
- **Benefits**: Consistent environments, easy scaling

### Configuration Management
```yaml
# config.yaml
environment: production
pipeline:
  schedule: "0 2 * * 0"  # Weekly Sunday 2 AM
  timeout_hours: 6
  max_retries: 3

sources:
  github:
    enabled: true
    search_queries:
      - "machine learning location:Australia"
      - "artificial intelligence location:Australia"
    rate_limit: 5000  # requests per hour
  
  twitter:
    enabled: true
    keywords: ["GPT", "LLM", "machine learning", "AI startup"]
    au_filters: ["Australia", ".com.au", "Sydney", "Melbourne"]
    rate_limit: 300   # requests per 15 minutes
```

This architecture provides a **solid foundation** for the 3-day MVP while being **extensible** for future enhancements and **scalable** for production use.