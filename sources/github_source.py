"""
GitHub Source Module
Clean, well-organized GitHub talent discovery with intelligent contact extraction
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta, timezone
import github
from github import Github
from github.GithubException import GithubException, RateLimitExceededException

from config import settings
from core.talent import Talent
from services.contact_extractor import ContactExtractor

logger = logging.getLogger(__name__)

class GitHubSource:
    """
    GitHub talent discovery source with intelligent contact extraction
    
    Features:
    - Advanced GitHub API search
    - Australia connection scoring
    - Intelligent contact extraction integration
    - Rate limiting and error handling
    - Comprehensive talent scoring
    """
    
    # Australia location indicators
    AU_LOCATION_KEYWORDS = [
        'australia', 'sydney', 'melbourne', 'brisbane', 'perth', 
        'adelaide', 'darwin', 'canberra', 'hobart', 'nsw', 'vic', 
        'qld', 'wa', 'sa', 'tas', 'act', 'nt', 'australian'
    ]
    
    # AI/ML keywords for repository analysis
    AI_ML_KEYWORDS = [
        'machine learning', 'deep learning', 'neural network', 
        'artificial intelligence', 'tensorflow', 'pytorch', 
        'scikit-learn', 'keras', 'nlp', 'computer vision',
        'data science', 'ml', 'ai'
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize GitHub source
        
        Args:
            config: Optional configuration dict with GitHub token and search params
        """
        self.config = config or {}
        
        # Initialize GitHub client
        github_token = self.config.get('github_token') or settings.api.github_token
        if not github_token:
            raise ValueError("GitHub token is required")
        
        try:
            self.github = Github(github_token)
            # Test the connection with a simple API call
            user = self.github.get_user()
            logger.info(f"GitHub client initialized successfully for user: {user.login}")
        except Exception as e:
            raise ValueError(f"Failed to initialize GitHub client: {e}")
        
        # Initialize contact extractor
        self.contact_extractor = ContactExtractor()
        
        # Search configuration
        self.max_results = self.config.get('max_results', settings.search.max_results)
        self.min_followers = self.config.get('min_followers', settings.search.min_followers)
        self.min_repos = self.config.get('min_repos', settings.search.min_repos)
    
    def search(self, search_params: Dict[str, Any]) -> List[Talent]:
        """
        Search for talents on GitHub
        
        Args:
            search_params: Search configuration including keywords, locations, etc.
            
        Returns:
            List of Talent objects with contact information extracted
        """
        logger.info("Starting GitHub talent search")
        
        try:
            # Build search query
            query = self._build_search_query(search_params)
            logger.info(f"Search query: {query}")
            
            # Execute search with much higher limit for Australian filtering
            original_max = search_params.get('max_results', 10)
            search_params['max_results'] = min(original_max * 10, 100)  # Search 10x more for strict filtering
            
            users = self._execute_search(query, search_params)
            logger.info(f"Found {len(users)} users from GitHub search")
            
            # Filter ONLY for Australian users - strict filtering
            australian_users = []
            
            for user in users:
                au_strength = self._calculate_au_strength(user)
                if au_strength > 0:  # Has some Australian connection
                    australian_users.append((user, au_strength))
            
            # Sort by AU strength (highest first) and take the top ones
            australian_users.sort(key=lambda x: x[1], reverse=True)
            final_users = [user for user, _ in australian_users[:original_max]]
            
            logger.info(f"Found {len(australian_users)} Australian users, selecting top {len(final_users)}")
            
            if len(australian_users) > 0:
                logger.info("Top Australian users found:")
                for i, (user, strength) in enumerate(australian_users[:5], 1):
                    logger.info(f"  {i}. {user.login} (AU={strength:.2f}, Location: {user.location})")
            
            # Convert to talents and extract contact info
            talents = []
            for i, user in enumerate(final_users, 1):
                logger.info(f"Processing Australian user {i}/{len(final_users)}: {user.login}")
                
                try:
                    talent = self._convert_user_to_talent(user, search_params)
                    if talent:
                        talents.append(talent)
                except Exception as e:
                    logger.warning(f"Failed to process user {user.login}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(talents)} Australian talents")
            return talents
            
        except RateLimitExceededException:
            logger.error("GitHub rate limit exceeded")
            raise
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            raise
    
    def _build_search_query(self, params: Dict[str, Any]) -> str:
        """Build GitHub search query from parameters"""
        
        query_parts = []
        
        # Use simple location search - just use Australia for maximum results
        locations = params.get('location', settings.search.locations)
        if locations:
            # Use just "Australia" for simplicity - GitHub will find users from all Australian cities
            query_parts.append('location:"Australia"')
        
        # Use minimal thresholds to find more users
        min_followers = max(1, params.get('min_followers', 1))
        query_parts.append(f'followers:>={min_followers}')
        
        min_repos = max(1, params.get('min_repos', 1))
        query_parts.append(f'repos:>={min_repos}')
        
        # Add language filter
        language = params.get('language', settings.search.default_language)
        if language:
            query_parts.append(f'language:{language}')
        
        # Add user type
        query_parts.append('type:user')
        
        query = ' '.join(query_parts)
        logger.info(f"Search query: {query}")
        return query
    
    def _execute_search(self, query: str, params: Dict[str, Any]) -> List:
        """Execute GitHub search and return users"""
        max_results = params.get('max_results', self.max_results)
        sort_by = params.get('sort', 'followers')
        
        try:
            # Search users
            result = self.github.search_users(
                query=query,
                sort=sort_by,
                order='desc'
            )
            
            # Get users (limited by max_results)
            users = []
            for i, user in enumerate(result):
                if i >= max_results:
                    break
                users.append(user)
            
            return users
            
        except GithubException as e:
            logger.error(f"GitHub search API error: {e}")
            raise
    
    def _convert_user_to_talent(self, user, search_params: Dict[str, Any]) -> Optional[Talent]:
        """Convert GitHub user to Talent object with contact extraction"""
        try:
            # Calculate AU strength
            au_strength = self._calculate_au_strength(user)
            
            # Create base talent from GitHub user
            talent = Talent.from_github_user(user, au_strength)
            
            # Calculate GitHub score
            talent.github_score = self._calculate_github_score(user, search_params)
            
            # Extract contact information
            contact_info = self._extract_contact_information(user)
            if contact_info:
                talent.add_contact_info(contact_info)
            
            # Add AU signals
            au_signals = self._identify_au_signals(user)
            talent.add_au_signals(au_signals)
            
            # Calculate final total score
            talent._calculate_total_score()
            
            return talent
            
        except Exception as e:
            logger.warning(f"Failed to convert user {user.login}: {e}")
            return None
    
    def _extract_contact_information(self, user) -> Optional:
        """Extract contact information using the contact extractor service"""
        try:
            # Prepare profile data
            profile_data = {
                'name': user.name,
                'login': user.login,
                'html_url': user.html_url,
                'bio': user.bio,
                'email': user.email,
                'blog': user.blog,
                'company': user.company,
                'location': user.location,
                'twitter_username': user.twitter_username
            }
            
            # Extract contact information
            contact_info = self.contact_extractor.extract_from_profile(
                profile_data, 'github', user
            )
            
            return contact_info
            
        except Exception as e:
            logger.warning(f"Contact extraction failed for {user.login}: {e}")
            return None
    
    def _calculate_au_strength(self, user) -> float:
        """Calculate Australia connection strength (0-1)"""
        score = 0.0
        
        # Location analysis (50% weight)
        if user.location:
            location_lower = user.location.lower()
            # Use more precise matching to avoid false positives
            for keyword in self.AU_LOCATION_KEYWORDS:
                if keyword in ['sa', 'nt', 'wa', 'nsw', 'vic', 'qld', 'tas', 'act']:
                    # For state abbreviations, require word boundaries or specific patterns
                    import re
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, location_lower):
                        score += 0.5
                        break
                else:
                    # For full words, use substring matching
                    if keyword in location_lower:
                        score += 0.5
                        break
        
        # Company analysis (20% weight)
        if user.company:
            company_lower = user.company.lower()
            au_company_indicators = ['australia', 'sydney', 'melbourne', '.au', 'aussie']
            for indicator in au_company_indicators:
                if indicator in company_lower:
                    score += 0.2
                    break
        
        # Blog/website analysis (15% weight)
        if user.blog:
            blog_lower = user.blog.lower()
            if '.au' in blog_lower or 'australia' in blog_lower:
                score += 0.15
        
        # Bio analysis (15% weight)
        if user.bio:
            bio_lower = user.bio.lower()
            for keyword in self.AU_LOCATION_KEYWORDS:
                if keyword in ['sa', 'nt', 'wa', 'nsw', 'vic', 'qld', 'tas', 'act']:
                    # For state abbreviations, require word boundaries
                    import re
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, bio_lower):
                        score += 0.15
                        break
                else:
                    # For full words, use substring matching
                    if keyword in bio_lower:
                        score += 0.15
                        break
        
        return min(score, 1.0)
    
    def _calculate_github_score(self, user, search_params: Dict[str, Any]) -> float:
        """Calculate GitHub activity and quality score"""
        score = 0.0
        
        # Follower score (30% weight) - normalize to reasonable scale
        if user.followers > 0:
            # Log scale for followers (1 follower = 0.1, 100 followers = 0.3)
            follower_score = min(0.3, (user.followers / 100) * 0.3)
            score += follower_score
        
        # Repository count (25% weight)
        if user.public_repos > 0:
            # Reasonable repository count scoring
            repo_score = min(0.25, (user.public_repos / 50) * 0.25)
            score += repo_score
        
        # Account age (20% weight)
        if user.created_at:
            account_age = datetime.now(timezone.utc) - user.created_at
            age_years = account_age.days / 365.25
            age_score = min(0.2, (age_years / 5) * 0.2)  # Max score at 5+ years
            score += age_score
        
        # Bio completeness (15% weight)
        if user.bio and len(user.bio) > 20:
            score += 0.15
        
        # Additional profile completeness (10% weight)
        profile_bonus = 0
        if user.name:
            profile_bonus += 0.03
        if user.company:
            profile_bonus += 0.03
        if user.blog:
            profile_bonus += 0.04
        score += profile_bonus
        
        return min(score, 1.0)
    
    def _identify_au_signals(self, user) -> List[str]:
        """Identify signals indicating Australia connection"""
        signals = []
        
        # Location signals
        if user.location:
            location_lower = user.location.lower()
            for keyword in self.AU_LOCATION_KEYWORDS:
                if keyword in location_lower:
                    signals.append(f"Location: {user.location}")
                    break
        
        # Company signals
        if user.company:
            company_lower = user.company.lower()
            au_indicators = ['australia', '.au', 'sydney', 'melbourne']
            for indicator in au_indicators:
                if indicator in company_lower:
                    signals.append(f"Company: {user.company}")
                    break
        
        # Website signals
        if user.blog and '.au' in user.blog.lower():
            signals.append(f"Australian domain: {user.blog}")
        
        # Bio signals
        if user.bio:
            bio_lower = user.bio.lower()
            if any(keyword in bio_lower for keyword in self.AU_LOCATION_KEYWORDS):
                signals.append("Bio mentions Australia")
        
        # GitHub activity signals
        if user.followers >= 50:
            signals.append("High follower count")
        if user.public_repos >= 20:
            signals.append("Active repository contributor")
        
        # Account quality signals
        if user.created_at and (datetime.now(timezone.utc) - user.created_at).days >= 365:
            signals.append("Established account (1+ years)")
        
        return signals
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current GitHub API rate limit status"""
        try:
            rate_limit = self.github.get_rate_limit()
            return {
                'core': {
                    'remaining': rate_limit.core.remaining,
                    'limit': rate_limit.core.limit,
                    'reset_time': rate_limit.core.reset
                },
                'search': {
                    'remaining': rate_limit.search.remaining,
                    'limit': rate_limit.search.limit,
                    'reset_time': rate_limit.search.reset
                }
            }
        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            return {}