#!/usr/bin/env python3
"""
Talent Discovery API
RESTful API for talent discovery and outreach management
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
# Removed HTTPBearer and HTTPAuthorizationCredentials imports
from pydantic import BaseModel, Field
import uvicorn

# Import our existing talent discovery system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from talent_discovery import TalentDiscoveryApp
from core.talent import Talent
from api.models import (
    TalentSearchRequest, TalentSearchResponse,
    OutreachCampaignRequest, OutreachCampaignResponse,
    ContactRequest, ContactResponse
)
from api.endpoints import talents, outreach, docs
from api.services.outreach_manager import OutreachManager
from api.services.email_service import EmailService
from api.services.twitter_dm_service import TwitterDMService
from api.services.rate_limiter import RateLimiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Talent Discovery API",
    description="API for discovering Australian AI/ML talent and managing outreach campaigns",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
talent_discovery_app = None
outreach_manager = None
rate_limiter = None

# Include routers
app.include_router(talents.router)
app.include_router(outreach.router)
app.include_router(docs.router)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global talent_discovery_app, outreach_manager, rate_limiter
    
    logger.info("Starting Talent Discovery API...")
    
    try:
        # Initialize core services
        talent_discovery_app = TalentDiscoveryApp()
        rate_limiter = RateLimiter()
        
        # Initialize outreach services
        email_service = EmailService()
        twitter_dm_service = TwitterDMService()
        outreach_manager = OutreachManager()
        
        # Inject dependencies into endpoint modules
        talents.set_talent_app(talent_discovery_app)
        talents.set_rate_limiter(rate_limiter)
        
        outreach.set_rate_limiter(rate_limiter)
        outreach.set_outreach_manager(outreach_manager)
        
        docs.set_rate_limiter(rate_limiter)
        
        logger.info("Talent Discovery API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
        raise

# Authentication removed for demo application

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Talent Discovery API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not talent_discovery_app:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Talent discovery service not available"
        )
    
    status_info = talent_discovery_app.get_status()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "talent_discovery": "operational",
            "github_source": "operational" if status_info["github_source_ready"] else "unavailable",
            "twitter_source": "operational" if status_info["twitter_source_ready"] else "unavailable",
            "notion_db": "operational" if status_info["notion_db_ready"] else "unavailable",
            "outreach_manager": "operational" if outreach_manager else "unavailable"
        }
    }

# Talent search endpoint moved to api/endpoints/talents.py

async def log_search_analytics(user_id: str, search_params: dict, talents_found: int):
    """Log search analytics for monitoring"""
    logger.info(f"Search analytics - User: {user_id}, Params: {search_params}, Found: {talents_found}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )