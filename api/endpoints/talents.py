#!/usr/bin/env python3
"""
Talent Discovery API Endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from api.models import (
    TalentSearchRequest, TalentSearchResponse, TalentData,
    SourceType, APIError
)
from api.services.rate_limiter import RateLimiter
from talent_discovery import TalentDiscoveryApp
from config.settings import APIConfig

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/talents", tags=["talents"])

# Dependencies will be injected by main.py
rate_limiter: RateLimiter = None
talent_app: TalentDiscoveryApp = None

# Authentication removed for demo application

@router.post("/search", response_model=TalentSearchResponse)
async def search_talents(
    request: TalentSearchRequest,
    background_tasks: BackgroundTasks
):
    """Search for talents using specified sources and criteria"""
    try:
        if not talent_app:
            raise HTTPException(
                status_code=500,
                detail="Talent discovery service not available"
            )
        
        logger.info(f"Talent search request: {request.keywords}")
        
        # Convert request to internal format
        search_sources = [source.value for source in request.sources]
        
        # Perform talent discovery
        results = await talent_app.discover_talents(
            keywords=request.keywords,
            sources=search_sources,
            location=request.location,
            max_results=min(request.max_results, 100),  # Cap at 100
            quality_threshold=request.quality_threshold,
            save_to_notion=request.save_to_notion
        )
        
        # Convert results to API format
        talents = []
        for result in results[:request.max_results]:
            talent_data = TalentData(
                id=result.get('id', ''),
                name=result.get('name', ''),
                location=result.get('location', ''),
                bio=result.get('bio', ''),
                skills=result.get('skills', []),
                experience_years=result.get('experience_years'),
                github_url=result.get('github_url'),
                twitter_url=result.get('twitter_url'),
                linkedin_url=result.get('linkedin_url'),
                email=result.get('email'),
                phone=result.get('phone'),
                website=result.get('website'),
                quality_score=result.get('quality_score', 0.0),
                au_strength=result.get('au_strength', 0.0),
                source=SourceType(result.get('source', 'github')),
                discovered_at=result.get('discovered_at'),
                custom_data=result.get('custom_data', {})
            )
            talents.append(talent_data)
        
        # Update user stats in background
        background_tasks.add_task(
            update_user_stats,
            user.id,
            "talents_discovered",
            len(talents)
        )
        
        response = TalentSearchResponse(
            success=True,
            talents=talents,
            total_found=len(results),
            sources_used=request.sources,
            search_metadata={
                "keywords": request.keywords,
                "location": request.location,
                "quality_threshold": request.quality_threshold,
                "execution_time": results[0].get('execution_time', 0) if results else 0,
                "user_id": user.id,
                "api_key_id": api_key_obj.id
            }
        )
        
        logger.info(f"Talent search completed: {len(talents)} talents found")
        return response
        
    except ValueError as e:
        logger.error(f"Talent search validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Talent search error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during talent search"
        )

@router.get("/sources", response_model=List[dict])
async def get_available_sources():
    """Get list of available talent sources and their configuration status"""
    try:
        if not talent_app:
            raise HTTPException(
                status_code=500,
                detail="Talent discovery service not available"
            )
        
        # Get source configuration status
        config = APIConfig()
        
        sources = [
            {
                "name": "github",
                "display_name": "GitHub",
                "description": "Search GitHub users by location and programming language",
                "configured": config.is_github_configured(),
                "capabilities": [
                    "Location-based search",
                    "Programming language filtering",
                    "Repository analysis",
                    "Contact extraction"
                ]
            },
            {
                "name": "twitter",
                "display_name": "Twitter/X",
                "description": "Search Twitter users by keywords and location",
                "configured": config.is_twitter_configured(),
                "capabilities": [
                    "Keyword-based search",
                    "Bio analysis",
                    "Engagement metrics",
                    "Contact extraction"
                ]
            }
        ]
        
        return sources
        
    except Exception as e:
        logger.error(f"Error getting available sources: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving available sources"
        )

@router.get("/stats", response_model=dict)
async def get_talent_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in stats")
):
    """Get talent discovery statistics for the authenticated user"""
    try:
        user = auth_data["user"]
        
        # Get user stats from auth service
        user_stats = auth_service.get_user_stats(user.id)
        if not user_stats:
            raise HTTPException(status_code=404, detail="User stats not found")
        
        # Get rate limit info
        api_key_obj = auth_data["api_key"]
        rate_limit_key = f"api_key:{api_key_obj.id}"
        
        current_limits = []
        usage_stats = {}
        
        if rate_limiter:
            current_limits = rate_limiter.get_current_limits(
                key=rate_limit_key,
                endpoint="/api/v1/talents/search",
                user_role=user.role.value
            )
            usage_stats = rate_limiter.get_usage_stats(rate_limit_key)
        
        return {
            "user_info": user_stats["user_info"],
            "api_usage": {
                "total_requests": user_stats["usage"]["total_requests"],
                "talents_discovered": user_stats["usage"].get("total_talents_discovered", 0),
                "outreach_sent": user_stats["usage"].get("total_outreach_sent", 0)
            },
            "rate_limits": current_limits,
            "recent_activity": usage_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting talent stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving talent statistics"
        )

@router.get("/export", response_model=dict)
async def export_talents(
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of records")
):
    """Export discovered talents for the authenticated user"""
    try:
        user = auth_data["user"]
        
        # This would typically query the Notion database or local storage
        # For now, return a placeholder response
        
        logger.info(f"Talent export request from user {user.id} (format: {format}, limit: {limit})")
        
        return {
            "success": True,
            "message": "Export functionality will be implemented with database integration",
            "format": format,
            "limit": limit,
            "user_id": user.id,
            "export_url": f"/api/v1/talents/download/{user.id}?format={format}"
        }
        
    except Exception as e:
        logger.error(f"Error exporting talents: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error exporting talents"
        )

async def update_user_stats(user_id: str, stat_name: str, increment: int):
    """Background task to update user statistics"""
    try:
        if auth_service and user_id in auth_service.users:
            user = auth_service.users[user_id]
            if stat_name in user.usage_stats:
                user.usage_stats[stat_name] += increment
            else:
                user.usage_stats[stat_name] = increment
            
            # Save updated stats
            auth_service._save_data()
            
    except Exception as e:
        logger.error(f"Failed to update user stats: {e}")

# Dependency injection functions (called by main.py)
def set_rate_limiter(limiter: RateLimiter):
    global rate_limiter
    rate_limiter = limiter

def set_talent_app(app: TalentDiscoveryApp):
    global talent_app
    talent_app = app