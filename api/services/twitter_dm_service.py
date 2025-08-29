#!/usr/bin/env python3
"""
Twitter DM Service
Handles Twitter direct message sending for talent outreach
"""

import logging
import os
import re
from typing import Dict, Optional, List
import asyncio
from datetime import datetime
import uuid

# Twitter API v2 client (would need tweepy or similar)
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    logging.warning("Tweepy not installed - Twitter DM functionality will be limited")

logger = logging.getLogger(__name__)

class TwitterDMService:
    """Service for sending Twitter direct messages"""
    
    def __init__(self):
        # Twitter API credentials
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Rate limiting
        self.daily_dm_limit = int(os.getenv('TWITTER_DAILY_DM_LIMIT', '1000'))
        self.hourly_dm_limit = int(os.getenv('TWITTER_HOURLY_DM_LIMIT', '100'))
        
        # Tracking
        self.sent_today = 0
        self.sent_this_hour = 0
        self.last_reset_date = datetime.now().date()
        self.last_reset_hour = datetime.now().hour
        
        self.is_configured = bool(
            self.api_key and 
            self.api_secret and 
            self.access_token and 
            self.access_token_secret
        )
        
        # Initialize Twitter client
        self.client = None
        if self.is_configured and TWEEPY_AVAILABLE:
            try:
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True
                )
                logger.info("Twitter DM service configured successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")
                self.is_configured = False
        else:
            logger.warning("Twitter DM service not configured - missing credentials or tweepy")
    
    async def send_dm(
        self,
        twitter_url: str,
        message: str,
        sender_handle: Optional[str] = None,
        tracking_id: Optional[str] = None
    ) -> bool:
        """Send a direct message to a Twitter user"""
        if not self.is_configured:
            logger.error("Twitter DM service not configured")
            return False
        
        if not self.client:
            logger.error("Twitter client not available")
            return False
        
        # Check rate limits
        if not self._check_rate_limits():
            logger.error("Twitter DM rate limit exceeded")
            return False
        
        try:
            # Extract username from Twitter URL
            username = self._extract_username_from_url(twitter_url)
            if not username:
                logger.error(f"Could not extract username from URL: {twitter_url}")
                return False
            
            # Get user ID from username
            user_id = await self._get_user_id(username)
            if not user_id:
                logger.error(f"Could not find user ID for username: {username}")
                return False
            
            # Prepare message with tracking if enabled
            final_message = message
            if tracking_id:
                # Add tracking info to message (subtle)
                final_message += f"\n\n[Ref: {tracking_id[:8]}]"
            
            # Send DM
            response = self.client.create_direct_message(
                dm_conversation_id=user_id,
                text=final_message
            )
            
            if response.data:
                self._update_rate_limit_counters()
                logger.info(f"DM sent successfully to @{username} (tracking: {tracking_id})")
                return True
            else:
                logger.error(f"Failed to send DM to @{username}: No response data")
                return False
                
        except tweepy.Forbidden as e:
            logger.error(f"Twitter API forbidden error (user may not accept DMs): {e}")
            return False
        except tweepy.TooManyRequests as e:
            logger.error(f"Twitter API rate limit exceeded: {e}")
            return False
        except tweepy.Unauthorized as e:
            logger.error(f"Twitter API unauthorized: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send DM to {twitter_url}: {e}")
            return False
    
    async def send_bulk_dms(
        self,
        recipients: List[Dict[str, str]],
        message_template: str,
        sender_handle: Optional[str] = None,
        delay_between_sends: float = 5.0
    ) -> Dict[str, bool]:
        """Send bulk DMs with personalization"""
        results = {}
        
        for recipient in recipients:
            twitter_url = recipient.get('twitter_url')
            if not twitter_url:
                continue
            
            # Check rate limits before each send
            if not self._check_rate_limits():
                logger.warning("Rate limit reached, stopping bulk DM send")
                break
            
            # Personalize message
            personalized_message = message_template.format(**recipient)
            
            # Generate tracking ID
            tracking_id = str(uuid.uuid4())
            
            # Send DM
            success = await self.send_dm(
                twitter_url=twitter_url,
                message=personalized_message,
                sender_handle=sender_handle,
                tracking_id=tracking_id
            )
            
            results[twitter_url] = success
            
            # Delay between sends to be respectful
            if delay_between_sends > 0:
                await asyncio.sleep(delay_between_sends)
        
        return results
    
    async def _get_user_id(self, username: str) -> Optional[str]:
        """Get Twitter user ID from username"""
        try:
            user = self.client.get_user(username=username)
            if user.data:
                return user.data.id
            return None
        except Exception as e:
            logger.error(f"Failed to get user ID for @{username}: {e}")
            return None
    
    def _extract_username_from_url(self, twitter_url: str) -> Optional[str]:
        """Extract username from Twitter URL"""
        # Handle various Twitter URL formats
        patterns = [
            r'twitter\.com/([^/\?]+)',
            r'x\.com/([^/\?]+)',
            r'@([a-zA-Z0-9_]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, twitter_url, re.IGNORECASE)
            if match:
                username = match.group(1)
                # Remove @ if present
                username = username.lstrip('@')
                # Validate username format
                if re.match(r'^[a-zA-Z0-9_]{1,15}$', username):
                    return username
        
        return None
    
    def _check_rate_limits(self) -> bool:
        """Check if we're within rate limits"""
        current_date = datetime.now().date()
        current_hour = datetime.now().hour
        
        # Reset daily counter
        if current_date != self.last_reset_date:
            self.sent_today = 0
            self.last_reset_date = current_date
        
        # Reset hourly counter
        if current_hour != self.last_reset_hour:
            self.sent_this_hour = 0
            self.last_reset_hour = current_hour
        
        # Check limits
        if self.sent_today >= self.daily_dm_limit:
            return False
        
        if self.sent_this_hour >= self.hourly_dm_limit:
            return False
        
        return True
    
    def _update_rate_limit_counters(self):
        """Update rate limit counters after successful send"""
        self.sent_today += 1
        self.sent_this_hour += 1
    
    def validate_twitter_url(self, twitter_url: str) -> bool:
        """Validate Twitter URL format"""
        patterns = [
            r'^https?://(www\.)?(twitter|x)\.com/[a-zA-Z0-9_]+/?$',
            r'^@[a-zA-Z0-9_]{1,15}$'
        ]
        
        for pattern in patterns:
            if re.match(pattern, twitter_url, re.IGNORECASE):
                return True
        
        return False
    
    def create_professional_dm_template(
        self,
        content: str,
        sender_name: str = None,
        company_name: str = None,
        include_unsubscribe: bool = True
    ) -> str:
        """Create a professional DM template"""
        sender_name = sender_name or "TalentSeeker Team"
        company_name = company_name or "TalentSeeker"
        
        template = f"""Hi {{name}},

{content}

Best regards,
{sender_name}
{company_name}"""
        
        if include_unsubscribe:
            template += "\n\nReply STOP to opt out of future messages."
        
        return template
    
    def get_rate_limit_status(self) -> Dict[str, any]:
        """Get current rate limit status"""
        return {
            "daily_limit": self.daily_dm_limit,
            "hourly_limit": self.hourly_dm_limit,
            "sent_today": self.sent_today,
            "sent_this_hour": self.sent_this_hour,
            "daily_remaining": max(0, self.daily_dm_limit - self.sent_today),
            "hourly_remaining": max(0, self.hourly_dm_limit - self.sent_this_hour),
            "can_send": self._check_rate_limits()
        }
    
    def get_configuration_status(self) -> Dict[str, any]:
        """Get Twitter DM service configuration status"""
        return {
            "configured": self.is_configured,
            "tweepy_available": TWEEPY_AVAILABLE,
            "api_key_configured": bool(self.api_key),
            "api_secret_configured": bool(self.api_secret),
            "access_token_configured": bool(self.access_token),
            "access_token_secret_configured": bool(self.access_token_secret),
            "bearer_token_configured": bool(self.bearer_token),
            "client_initialized": bool(self.client),
            "rate_limits": self.get_rate_limit_status()
        }
    
    async def test_connection(self) -> bool:
        """Test Twitter API connection"""
        if not self.client:
            return False
        
        try:
            # Try to get authenticated user info
            me = self.client.get_me()
            if me.data:
                logger.info(f"Twitter connection test successful - authenticated as @{me.data.username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Twitter connection test failed: {e}")
            return False