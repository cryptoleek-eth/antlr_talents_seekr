#!/usr/bin/env python3
"""
Pydantic models for API request/response schemas
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class SourceType(str, Enum):
    """Available talent sources"""
    GITHUB = "github"
    TWITTER = "twitter"

class OutreachType(str, Enum):
    """Available outreach methods"""
    EMAIL = "email"
    TWITTER_DM = "twitter_dm"
    LINKEDIN = "linkedin"

class CampaignStatus(str, Enum):
    """Campaign status options"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ContactStatus(str, Enum):
    """Contact attempt status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"

# Talent Search Models
class TalentSearchRequest(BaseModel):
    """Request model for talent search"""
    keywords: List[str] = Field(
        default=["machine learning", "artificial intelligence", "python"],
        description="Keywords to search for",
        min_items=1,
        max_items=10
    )
    locations: Optional[List[str]] = Field(
        default=["Australia", "Sydney", "Melbourne"],
        description="Geographic locations to focus on",
        max_items=5
    )
    sources: List[SourceType] = Field(
        default=[SourceType.GITHUB, SourceType.TWITTER],
        description="Sources to search",
        min_items=1
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of talents to return",
        ge=1,
        le=100
    )
    save_to_notion: bool = Field(
        default=True,
        description="Whether to save results to Notion database"
    )
    min_au_strength: Optional[float] = Field(
        default=0.3,
        description="Minimum Australia connection strength (0-1)",
        ge=0.0,
        le=1.0
    )
    min_score: Optional[float] = Field(
        default=0.5,
        description="Minimum overall talent score (0-1)",
        ge=0.0,
        le=1.0
    )

    @validator('keywords')
    def validate_keywords(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one keyword is required')
        return [keyword.strip() for keyword in v if keyword.strip()]

class TalentData(BaseModel):
    """Talent data model"""
    name: str
    location: Optional[str] = None
    email: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
    au_strength: float = Field(ge=0.0, le=1.0)
    total_score: float = Field(ge=0.0, le=1.0)
    platform_data: Dict[str, Any] = Field(default_factory=dict)
    contact_methods: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    bio: Optional[str] = None
    discovered_at: datetime = Field(default_factory=datetime.now)

class QualityMetrics(BaseModel):
    """Quality metrics for search results"""
    avg_score: float = Field(ge=0.0, le=1.0)
    avg_au_strength: float = Field(ge=0.0, le=1.0)
    contact_coverage: float = Field(ge=0.0, le=1.0, description="Percentage with contact info")

class TalentSearchResponse(BaseModel):
    """Response model for talent search"""
    success: bool
    search_id: str
    talents_found: int
    talents: List[TalentData]
    discovery_time: float = Field(description="Discovery time in seconds")
    quality_metrics: QualityMetrics
    timestamp: datetime = Field(default_factory=datetime.now)
    message: Optional[str] = None

# Outreach Campaign Models
class EmailTemplate(BaseModel):
    """Email template model"""
    subject: str = Field(max_length=200)
    body: str = Field(max_length=5000)
    sender_name: str = Field(max_length=100)
    sender_email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    reply_to: Optional[str] = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

class TwitterDMTemplate(BaseModel):
    """Twitter DM template model"""
    message: str = Field(max_length=1000, description="DM message content")
    sender_handle: str = Field(pattern=r'^@?[A-Za-z0-9_]{1,15}$')

class OutreachCampaignRequest(BaseModel):
    """Request model for creating outreach campaign"""
    name: str = Field(max_length=200, description="Campaign name")
    description: Optional[str] = Field(max_length=1000)
    outreach_type: OutreachType
    target_talent_ids: List[str] = Field(
        min_items=1,
        max_items=1000,
        description="List of talent IDs to contact"
    )
    email_template: Optional[EmailTemplate] = None
    twitter_dm_template: Optional[TwitterDMTemplate] = None
    schedule_send: Optional[datetime] = None
    send_immediately: bool = Field(default=False)
    max_contacts_per_day: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Rate limiting for outreach"
    )
    track_opens: bool = Field(default=True)
    track_clicks: bool = Field(default=True)

    @validator('email_template')
    def validate_email_template(cls, v, values):
        if values.get('outreach_type') == OutreachType.EMAIL and not v:
            raise ValueError('Email template is required for email campaigns')
        return v

    @validator('twitter_dm_template')
    def validate_twitter_template(cls, v, values):
        if values.get('outreach_type') == OutreachType.TWITTER_DM and not v:
            raise ValueError('Twitter DM template is required for Twitter campaigns')
        return v

class OutreachCampaignResponse(BaseModel):
    """Response model for outreach campaign creation"""
    success: bool
    campaign_id: str
    name: str
    status: CampaignStatus
    total_targets: int
    estimated_completion: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    message: Optional[str] = None

# Contact Management Models
class ContactRequest(BaseModel):
    """Request model for individual contact"""
    talent_id: str
    outreach_type: OutreachType
    message: str = Field(max_length=5000)
    subject: Optional[str] = Field(max_length=200)  # For emails
    sender_info: Dict[str, str] = Field(
        description="Sender information (name, email, handle, etc.)"
    )
    track_engagement: bool = Field(default=True)
    custom_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ContactResponse(BaseModel):
    """Response model for contact attempt"""
    success: bool
    contact_id: str
    talent_id: str
    status: ContactStatus
    outreach_type: OutreachType
    sent_at: Optional[datetime] = None
    tracking_id: Optional[str] = None
    message: Optional[str] = None
    error_details: Optional[str] = None

# Analytics Models
class CampaignAnalytics(BaseModel):
    """Campaign analytics model"""
    campaign_id: str
    total_sent: int
    total_delivered: int
    total_opened: int
    total_replied: int
    total_bounced: int
    total_failed: int
    open_rate: float = Field(ge=0.0, le=1.0)
    reply_rate: float = Field(ge=0.0, le=1.0)
    bounce_rate: float = Field(ge=0.0, le=1.0)
    last_updated: datetime = Field(default_factory=datetime.now)

class APIUsageStats(BaseModel):
    """API usage statistics"""
    user_id: str
    total_searches: int
    total_talents_found: int
    total_campaigns: int
    total_contacts_sent: int
    current_month_usage: int
    rate_limit_remaining: int
    last_activity: datetime

# Error Models
class APIError(BaseModel):
    """Standard API error response"""
    error: bool = True
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None