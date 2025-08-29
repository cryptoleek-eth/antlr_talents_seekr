#!/usr/bin/env python3
"""
API Documentation and Testing Endpoints
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from api.models import APIUsageStats, APIError
from api.services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/docs", tags=["documentation"])

# Dependencies will be injected by main.py
rate_limiter: RateLimiter = None

# Authentication removed for demo application

@router.get("/api-info", response_model=Dict[str, Any])
async def get_api_info():
    """Get general API information and capabilities"""
    return {
        "name": "Talent Discovery & Outreach API",
        "version": "1.0.0",
        "description": "API for discovering talents and managing outreach campaigns",
        "features": [
            "Multi-source talent discovery (GitHub, Twitter)",
            "Automated outreach campaigns",
            "Email and Twitter DM integration",
            "Campaign analytics and tracking",
            "Rate limiting and authentication",
            "Quality scoring and filtering"
        ],
        "endpoints": {
            "talents": "/api/v1/talents",
            "outreach": "/api/v1/outreach",
            "auth": "/api/v1/auth",
            "docs": "/api/v1/docs"
        },
        "authentication": {
            "type": "None (Demo Mode)",
            "note": "Authentication disabled for demo"
        },
        "rate_limits": {
            "basic": "100 requests/hour",
            "premium": "1000 requests/hour",
            "enterprise": "10000 requests/hour"
        }
    }

@router.get("/usage", response_model=APIUsageStats)
async def get_usage_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to include")
):
    """Get API usage statistics for the authenticated user"""
    try:
        # Get usage stats from rate limiter
        usage_data = {}
        if rate_limiter:
            rate_limit_key = "demo_user"
            usage_data = rate_limiter.get_usage_stats(rate_limit_key, days)
        
        # Demo user stats
        user_stats = {}
        
        stats = APIUsageStats(
            user_id="demo_user",
            api_key_id="demo_key",
            total_requests=usage_data.get('total_requests', 0),
            successful_requests=usage_data.get('successful_requests', 0),
            failed_requests=usage_data.get('failed_requests', 0),
            rate_limited_requests=usage_data.get('rate_limited_requests', 0),
            talents_discovered=user_stats.get('talents_discovered', 0),
            campaigns_created=user_stats.get('campaigns_created', 0),
            contacts_sent=user_stats.get('contacts_sent', 0),
            period_days=days,
            current_rate_limit=usage_data.get('current_limit', 100),
            remaining_requests=usage_data.get('remaining_requests', 100)
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving usage statistics"
        )

@router.get("/examples", response_model=Dict[str, Any])
async def get_api_examples():
    """Get API usage examples and sample requests"""
    return {
        "talent_search": {
            "endpoint": "POST /api/v1/talents/search",
            "description": "Search for talents across multiple sources",
            "example_request": {
                "keywords": ["python", "machine learning"],
                "sources": ["github", "twitter"],
                "location": "Sydney",
                "min_quality_score": 0.7,
                "limit": 10
            },
            "example_response": {
                "success": True,
                "talents": [
                    {
                        "id": "talent_123",
                        "name": "John Doe",
                        "source": "github",
                        "profile_url": "https://github.com/johndoe",
                        "skills": ["Python", "Machine Learning"],
                        "location": "Sydney, Australia",
                        "quality_metrics": {
                            "overall_score": 0.85,
                            "technical_score": 0.9,
                            "activity_score": 0.8
                        }
                    }
                ],
                "total_found": 1,
                "search_time_seconds": 2.5
            }
        },
        "create_campaign": {
            "endpoint": "POST /api/v1/outreach/campaign",
            "description": "Create an outreach campaign",
            "example_request": {
                "name": "Python Developers Outreach",
                "description": "Recruiting Python developers for our startup",
                "outreach_type": "email",
                "target_talent_ids": ["talent_123", "talent_456"],
                "email_template": {
                    "subject": "Exciting Python Developer Opportunity",
                    "body": "Hi {name}, we have an exciting opportunity...",
                    "sender_name": "Jane Smith",
                    "sender_email": "jane@company.com"
                }
            },
            "example_response": {
                "success": True,
                "campaign_id": "campaign_789",
                "message": "Campaign created successfully",
                "targets_count": 2,
                "estimated_send_time": "2024-01-15T10:30:00Z"
            }
        },
        "send_individual_contact": {
            "endpoint": "POST /api/v1/outreach/contact",
            "description": "Send individual contact to a talent",
            "example_request": {
                "talent_id": "talent_123",
                "outreach_type": "twitter_dm",
                "twitter_dm_template": {
                    "message": "Hi {name}! Love your work on {skills}. Interested in a new opportunity? 🚀"
                }
            },
            "example_response": {
                "success": True,
                "contact_id": "contact_456",
                "message": "Contact sent successfully",
                "sent_at": "2024-01-15T10:30:00Z",
                "status": "sent"
            }
        }
    }

@router.get("/schemas", response_model=Dict[str, Any])
async def get_api_schemas():
    """Get API request/response schemas"""
    return {
        "TalentSearchRequest": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords to search for"
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["github", "twitter"]},
                    "description": "Sources to search"
                },
                "location": {
                    "type": "string",
                    "description": "Location filter (optional)"
                },
                "min_quality_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Minimum quality score filter"
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Maximum number of results"
                }
            },
            "required": ["keywords", "sources"]
        },
        "OutreachCampaignRequest": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Campaign name"
                },
                "description": {
                    "type": "string",
                    "description": "Campaign description"
                },
                "outreach_type": {
                    "type": "string",
                    "enum": ["email", "twitter_dm"],
                    "description": "Type of outreach"
                },
                "target_talent_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of talent IDs to contact"
                },
                "email_template": {
                    "type": "object",
                    "description": "Email template (required for email campaigns)"
                },
                "twitter_dm_template": {
                    "type": "object",
                    "description": "Twitter DM template (required for Twitter campaigns)"
                }
            },
            "required": ["name", "outreach_type", "target_talent_ids"]
        },
        "ContactRequest": {
            "type": "object",
            "properties": {
                "talent_id": {
                    "type": "string",
                    "description": "ID of the talent to contact"
                },
                "outreach_type": {
                    "type": "string",
                    "enum": ["email", "twitter_dm"],
                    "description": "Type of outreach"
                },
                "email_template": {
                    "type": "object",
                    "description": "Email template (required for email)"
                },
                "twitter_dm_template": {
                    "type": "object",
                    "description": "Twitter DM template (required for Twitter DM)"
                }
            },
            "required": ["talent_id", "outreach_type"]
        }
    }

@router.get("/errors", response_model=Dict[str, Any])
async def get_error_codes():
    """Get API error codes and descriptions"""
    return {
        "400": {
            "name": "Bad Request",
            "description": "Invalid request parameters or malformed request",
            "examples": [
                "Missing required fields",
                "Invalid enum values",
                "Malformed JSON"
            ]
        },
        "401": {
            "name": "Unauthorized",
            "description": "Invalid or missing API key",
            "examples": [
                "Missing Authorization header",
                "Invalid API key",
                "Expired API key"
            ]
        },
        "403": {
            "name": "Forbidden",
            "description": "Access denied to the requested resource",
            "examples": [
                "Insufficient permissions",
                "Resource belongs to another user"
            ]
        },
        "404": {
            "name": "Not Found",
            "description": "Requested resource not found",
            "examples": [
                "Talent not found",
                "Campaign not found",
                "Contact not found"
            ]
        },
        "429": {
            "name": "Too Many Requests",
            "description": "Rate limit exceeded",
            "examples": [
                "Hourly rate limit exceeded",
                "Daily rate limit exceeded"
            ],
            "headers": {
                "X-RateLimit-Limit": "Current rate limit",
                "X-RateLimit-Remaining": "Remaining requests",
                "X-RateLimit-Reset": "Reset time (Unix timestamp)",
                "Retry-After": "Seconds to wait before retry"
            }
        },
        "500": {
            "name": "Internal Server Error",
            "description": "Server error occurred",
            "examples": [
                "Database connection error",
                "External service unavailable",
                "Unexpected server error"
            ]
        }
    }

@router.get("/test-connection")
async def test_connection():
    """Test API connection and authentication"""
    try:
        return {
            "success": True,
            "message": "Connection successful",
            "user_id": "demo_user",
            "user_role": "basic",
            "api_key_id": "demo_key",
            "api_key_status": "active",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Connection test error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Connection test failed"
        )

@router.get("/rate-limits")
async def get_rate_limits():
    """Get current rate limit information"""
    try:
        # Get rate limit info from rate limiter
        rate_info = {}
        if rate_limiter:
            rate_limit_key = "demo_user"
            
            # Get limits for different endpoints
            endpoints = [
                "/api/v1/talents/search",
                "/api/v1/outreach/campaign",
                "/api/v1/outreach/contact"
            ]
            
            for endpoint in endpoints:
                status = rate_limiter.check_rate_limit(
                    key=rate_limit_key,
                    endpoint=endpoint,
                    user_role="basic",
                    dry_run=True  # Don't actually consume a request
                )
                
                rate_info[endpoint] = {
                    "limit": status.limit,
                    "remaining": status.remaining,
                    "reset_time": status.reset_time.isoformat() if status.reset_time else None,
                    "window_seconds": status.window_seconds
                }
        
        return {
            "success": True,
            "user_role": "basic",
            "rate_limits": rate_info,
            "global_limits": {
                "basic": "100 requests/hour",
                "premium": "1000 requests/hour",
                "enterprise": "10000 requests/hour"
            }
        }
        
    except Exception as e:
        logger.error(f"Rate limit info error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving rate limit information"
        )

# Dependency injection functions (called by main.py)
def set_rate_limiter(limiter: RateLimiter):
    global rate_limiter
    rate_limiter = limiter