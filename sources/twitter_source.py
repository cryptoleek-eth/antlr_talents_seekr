#!/usr/bin/env python3
"""
Twitter Source Module
Twitter talent discovery with intelligent contact extraction using twitterapi.io
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta, timezone
import requests
import time
import re

from config import settings
from core.talent import Talent
from services.contact_extractor import ContactExtractor

logger = logging.getLogger(__name__)

class TwitterSource:
    """
    Twitter talent discovery source with intelligent contact extraction

    Features:
    - twitterapi.io integration for user search
    - Australia connection scoring
    - AI/ML activity analysis
    - Intelligent contact extraction integration
    - Rate limiting and error handling
    - Comprehensive talent scoring
    """

    # Australia location indicators
    AU_LOCATION_KEYWORDS = [
        "australia", "sydney", "melbourne", "brisbane", "perth",
        "adelaide", "darwin", "canberra", "hobart", "nsw", "vic",
        "qld", "wa", "sa", "tas", "act", "nt", "australian"
    ]

    # AI/ML keywords for profile and tweet analysis
    AI_ML_KEYWORDS = [
        "machine learning", "deep learning", "neural network",
        "artificial intelligence", "tensorflow", "pytorch",
        "scikit-learn", "keras", "nlp", "computer vision",
        "data science", "ml", "ai", "chatgpt", "llm", "openai",
        "transformer", "gpt", "bert", "huggingface", "langchain",
        "vector database", "embedding", "rag", "fine-tuning"
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Twitter source with twitterapi.io

        Args:
            config: Optional configuration override
        """
        self.api_key = config.get("api_key") if config else settings.api.twitter_api_key
        
        if not self.api_key:
            logger.warning("Twitter API key not configured - Twitter source disabled")
            self.enabled = False
            return
        
        self.enabled = True
        self.base_url = "https://api.twitterapi.io"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Initialize contact extractor
        self.contact_extractor = ContactExtractor()
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests for 200 QPS limit
        
        logger.info("Twitter source initialized with twitterapi.io")

    def search(self, params: Dict[str, Any]) -> List[Talent]:
        """
        Search for AI/ML talents on Twitter using twitterapi.io

        Args:
            params: Search parameters including keywords, location, etc.

        Returns:
            List of discovered talents
        """
        if not self.enabled:
            logger.warning("Twitter source not enabled - skipping search")
            return []
            
        try:
            logger.info(f"Starting Twitter search with params: {params}")
            
            # Extract search parameters
            max_results = params.get('max_results', 20)
            keywords = params.get('keywords', self.AI_ML_KEYWORDS[:5])  # Use top 5 AI keywords
            
            talents = []
            
            # Search for users with AI/ML keywords
            for keyword in keywords:
                if len(talents) >= max_results:
                    break
                    
                logger.info(f"Searching Twitter users for keyword: {keyword}")
                users = self._search_users_by_keyword(keyword, limit=10)
                
                for user_data in users:
                    if len(talents) >= max_results:
                        break
                        
                    talent = self._convert_user_to_talent(user_data)
                    if talent and self._meets_quality_threshold(talent):
                        talents.append(talent)
                        
                # Rate limiting
                time.sleep(0.5)  # Be conservative with rate limits
            
            logger.info(f"Twitter search completed: {len(talents)} talents found")
            return talents
            
        except Exception as e:
            logger.error(f"Twitter search failed: {e}")
            return []

    def _search_users_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for users by keyword using twitterapi.io tweet search and extracting authors
        
        Args:
            keyword: Search keyword
            limit: Maximum number of users to return
            
        Returns:
            List of user data dictionaries
        """
        try:
            # Rate limiting
            self._enforce_rate_limit()
            
            url = f"{self.base_url}/twitter/tweet/advanced_search"
            params = {
                "query": keyword,
                "queryType": "Latest",
                "limit": limit * 3  # Get more tweets to find unique users
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # The advanced search endpoint returns tweets directly
            if "tweets" in data and data["tweets"]:
                tweets = data["tweets"]
                
                # Extract unique users from tweet authors
                seen_users = set()
                users = []
                
                for tweet in tweets:
                    author = tweet.get("author", {})
                    user_id = author.get("id")
                    
                    if user_id and user_id not in seen_users:
                        seen_users.add(user_id)
                        users.append(author)
                        
                        if len(users) >= limit:
                            break
                
                logger.info(f"Found {len(users)} unique users from {len(tweets)} tweets for keyword '{keyword}'")
                return users
            else:
                logger.warning(f"No tweets found for keyword '{keyword}'")
                return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for keyword '{keyword}': {e}")
            return []

    def _convert_user_to_talent(self, user_data: Dict[str, Any]) -> Optional[Talent]:
        """
        Convert Twitter user data to Talent object
        
        Args:
            user_data: User data from twitterapi.io
            
        Returns:
            Talent object or None if conversion fails
        """
        try:
            # Extract basic information
            name = user_data.get("name") or user_data.get("userName", "Unknown")
            username = user_data.get("userName", "")
            description = user_data.get("description", "")
            location = user_data.get("location", "")
            
            # Calculate Australia connection strength
            au_strength = self._calculate_au_strength(user_data)
            
            # Skip if no Australia connection
            if au_strength < 0.1:
                return None
            
            # Calculate Twitter score
            twitter_score = self._calculate_twitter_score(user_data)
            
            # Create talent object
            talent = Talent(
                name=name,
                twitter_url=user_data.get("url", f"https://twitter.com/{username}"),
                location=location,
                au_strength=au_strength,
                twitter_score=twitter_score,
                platform_data={
                    'twitter': {
                        'username': username,
                        'description': description,
                        'followers': user_data.get("followers", 0),
                        'following': user_data.get("following", 0),
                        'tweets_count': user_data.get("statusesCount", 0),
                        'verified': user_data.get("isBlueVerified", False),
                        'created_at': user_data.get("createdAt"),
                        'profile_picture': user_data.get("profilePicture")
                    }
                },
                sources=['twitter']
            )
            
            # Add AU signals
            au_signals = self._identify_au_signals(user_data)
            talent.add_au_signals(au_signals)
            
            # Extract contact information
            self._extract_contact_information(talent, user_data)
            
            return talent
            
        except Exception as e:
            logger.error(f"Failed to convert user to talent: {e}")
            return None

    def _calculate_au_strength(self, user_data: Dict[str, Any]) -> float:
        """
        Calculate Australia connection strength for a Twitter user
        
        Args:
            user_data: User data from twitterapi.io
            
        Returns:
            AU strength score (0-1)
        """
        score = 0.0
        
        # Check location field
        location = (user_data.get("location") or "").lower()
        for keyword in self.AU_LOCATION_KEYWORDS:
            if keyword in location:
                score += 0.8  # Strong signal from location
                break
        
        # Check description/bio
        description = (user_data.get("description") or "").lower()
        for keyword in self.AU_LOCATION_KEYWORDS:
            if keyword in description:
                score += 0.4  # Medium signal from bio
                break
        
        # Check profile bio entities for URLs
        profile_bio = user_data.get("profile_bio", {})
        entities = profile_bio.get("entities", {})
        
        # Check bio URLs
        bio_urls = entities.get("description", {}).get("urls", [])
        for url_info in bio_urls:
            expanded_url = (url_info.get("expanded_url") or "").lower()
            if any(keyword in expanded_url for keyword in self.AU_LOCATION_KEYWORDS):
                score += 0.3
                break
        
        # Check profile URL
        profile_urls = entities.get("url", {}).get("urls", [])
        for url_info in profile_urls:
            expanded_url = (url_info.get("expanded_url") or "").lower()
            if any(keyword in expanded_url for keyword in self.AU_LOCATION_KEYWORDS):
                score += 0.3
                break
        
        return min(score, 1.0)

    def _calculate_twitter_score(self, user_data: Dict[str, Any]) -> float:
        """
        Calculate Twitter-specific quality score
        
        Args:
            user_data: User data from twitterapi.io
            
        Returns:
            Twitter score (0-100)
        """
        score = 0.0
        
        # Follower count (0-30 points)
        followers = user_data.get("followers", 0)
        if followers > 10000:
            score += 30
        elif followers > 1000:
            score += 20
        elif followers > 100:
            score += 10
        elif followers > 10:
            score += 5
        
        # Tweet count and activity (0-20 points)
        tweets_count = user_data.get("statusesCount", 0)
        if tweets_count > 1000:
            score += 20
        elif tweets_count > 100:
            score += 15
        elif tweets_count > 50:
            score += 10
        elif tweets_count > 10:
            score += 5
        
        # AI/ML content in description (0-30 points)
        description = (user_data.get("description") or "").lower()
        ai_keywords_found = sum(1 for keyword in self.AI_ML_KEYWORDS if keyword in description)
        score += min(ai_keywords_found * 5, 30)
        
        # Verification status (0-10 points)
        if user_data.get("isBlueVerified"):
            score += 10
        
        # Account age (0-10 points)
        created_at = user_data.get("createdAt")
        if created_at:
            try:
                # Assume older accounts are more established
                account_age_years = (datetime.now() - datetime.fromisoformat(created_at.replace('Z', '+00:00'))).days / 365
                if account_age_years > 5:
                    score += 10
                elif account_age_years > 2:
                    score += 5
                elif account_age_years > 1:
                    score += 2
            except:
                pass
        
        return min(score, 100.0)

    def _identify_au_signals(self, user_data: Dict[str, Any]) -> List[str]:
        """
        Identify specific Australia connection signals
        
        Args:
            user_data: User data from twitterapi.io
            
        Returns:
            List of AU signal descriptions
        """
        signals = []
        
        location = (user_data.get("location") or "").lower()
        description = (user_data.get("description") or "").lower()
        
        # Location signals
        for keyword in self.AU_LOCATION_KEYWORDS:
            if keyword in location:
                signals.append(f"Location mentions '{keyword}'")
                break
        
        # Bio signals
        for keyword in self.AU_LOCATION_KEYWORDS:
            if keyword in description:
                signals.append(f"Bio mentions '{keyword}'")
                break
        
        # URL signals
        profile_bio = user_data.get("profile_bio", {})
        entities = profile_bio.get("entities", {})
        
        all_urls = []
        all_urls.extend(entities.get("description", {}).get("urls", []))
        all_urls.extend(entities.get("url", {}).get("urls", []))
        
        for url_info in all_urls:
            expanded_url = (url_info.get("expanded_url") or "").lower()
            if ".au" in expanded_url or "australia" in expanded_url:
                signals.append(f"Profile links to Australian domain")
                break
        
        return signals

    def _extract_contact_information(self, talent: Talent, user_data: Dict[str, Any]) -> None:
        """
        Extract contact information from Twitter profile
        
        Args:
            talent: Talent object to update
            user_data: User data from twitterapi.io
        """
        try:
            # Prepare profile data for contact extractor
            profile_data = {
                'name': talent.name,
                'bio': user_data.get("description", ""),
                'location': user_data.get("location", ""),
                'twitter_url': talent.twitter_url
            }
            
            # Extract URLs from bio entities
            profile_bio = user_data.get("profile_bio", {})
            entities = profile_bio.get("entities", {})
            
            urls = []
            # Bio URLs
            for url_info in entities.get("description", {}).get("urls", []):
                if url_info.get("expanded_url"):
                    urls.append(url_info["expanded_url"])
            
            # Profile URL
            for url_info in entities.get("url", {}).get("urls", []):
                if url_info.get("expanded_url"):
                    urls.append(url_info["expanded_url"])
            
            profile_data['urls'] = urls
            
            # Use contact extractor
            contact_info = self.contact_extractor.extract_from_profile(
                profile_data, 'twitter', user_data
            )
            
            # Update talent with contact information
            talent.add_contact_info(contact_info)
            
        except Exception as e:
            logger.error(f"Failed to extract contact info for {talent.name}: {e}")

    def _meets_quality_threshold(self, talent: Talent) -> bool:
        """
        Check if talent meets minimum quality thresholds
        
        Args:
            talent: Talent object to evaluate
            
        Returns:
            True if talent meets thresholds
        """
        # Minimum AU connection
        if talent.au_strength < 0.3:
            return False
        
        # Minimum Twitter score
        if talent.twitter_score < 15:
            return False
        
        # Must have some AI/ML indicators
        description = talent.platform_data.get('twitter', {}).get('description', '').lower()
        if not any(keyword in description for keyword in self.AI_ML_KEYWORDS):
            return False
        
        return True

    def _enforce_rate_limit(self) -> None:
        """
        Enforce rate limiting between API requests
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current Twitter API rate limit status
        Note: twitterapi.io doesn't provide rate limit headers, so we return estimated values
        """
        if not self.enabled:
            return {"status": "disabled", "reason": "API key not configured"}
        
        return {
            "service": "twitterapi.io",
            "max_qps": 200,
            "current_interval": self.min_request_interval,
            "status": "active"
        }
