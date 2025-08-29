#!/usr/bin/env python3
"""
Authentication and API Key Management Endpoints
(DISABLED FOR DEMO)
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Initialize router (disabled for demo)
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# Authentication disabled for demo application

@router.get("/demo-info")
async def get_demo_info():
    """Demo information endpoint"""
    return {
        "message": "Authentication disabled for demo",
        "demo_mode": True,
        "note": "All authentication endpoints have been disabled"
    }

# All authentication endpoints disabled for demo
# Original endpoints: /register, /api-key, /me, /api-keys, /validate, etc.

# Authentication endpoints removed for demo