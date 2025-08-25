"""
Contact Extraction Service
Intelligent multi-level contact information extraction with LLM decision-making
"""

import os
import re
import requests
import logging
from typing import Set, Dict, List, Optional, Union
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

from config import settings

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ContactInfo:
    """Container for extracted contact information"""
    emails: Set[str] = field(default_factory=set)
    social_links: Dict[str, str] = field(default_factory=dict)  # platform -> url
    website: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    personal_site: Optional[str] = None
    contact_score: float = 0.0  # 0-1, based on information richness

class ContactExtractor:
    """
    Intelligent contact extraction service with multi-level drilling
    
    Features:
    - Multi-level link drilling (up to 3 levels)
    - LLM-powered intelligent link selection
    - Fake email filtering
    - Source-agnostic extraction
    """
    
    # Fake email patterns to filter out
    FAKE_EMAIL_PATTERNS = [
        'git@github.com', 'noreply@github.com', 'example@', 'test@', 'demo@',
        'user@example', 'your-email@', 'email@example.com', 'sample@',
        'no-reply@', 'donotreply@', 'support@github.com'
    ]
    
    # Social platform patterns
    SOCIAL_PATTERNS = {
        'linkedin': re.compile(r'linkedin\.com/in/([a-zA-Z0-9-]+)', re.IGNORECASE),
        'twitter': re.compile(r'(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)', re.IGNORECASE),
        'github': re.compile(r'github\.com/([a-zA-Z0-9-]+)', re.IGNORECASE),
    }
    
    def __init__(self):
        """Initialize contact extractor with API configurations"""
        self.jina_token = settings.api.jina_token
        self.jina_base_url = "https://r.jina.ai"
        self.openai_client = None
        self.config = settings.contact_extraction
        
        # Initialize OpenAI client if available
        if settings.api.is_openai_configured():
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.api.openai_api_key)
                logger.info("OpenAI client initialized for intelligent extraction")
            except ImportError:
                logger.warning("OpenAI package not installed - using regex fallback")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e} - using regex fallback")
        else:
            logger.info("OpenAI API key not configured - using regex fallback")
    
    def extract_from_profile(self, profile_data: Dict, source_type: str, extra_data=None) -> ContactInfo:
        """
        Extract contact information from profile data
        
        Args:
            profile_data: Dict containing profile information
            source_type: Type of source ('github', 'linkedin', etc.)
            extra_data: Additional data specific to source type
            
        Returns:
            ContactInfo object with extracted information
        """
        logger.info(f"Starting contact extraction for {profile_data.get('name', 'Unknown')} from {source_type}")
        
        # Initialize contact info
        contact_info = ContactInfo()
        
        # Extract basic information from profile
        self._extract_basic_info(profile_data, contact_info)
        
        # Source-specific extraction
        if source_type == 'github' and extra_data:
            self._extract_github_specific(extra_data, contact_info)
        
        # Deep web extraction if URLs are available
        urls_to_scrape = self._identify_scraping_targets(profile_data, contact_info)
        if urls_to_scrape:
            self._perform_multi_level_extraction(urls_to_scrape, contact_info)
        
        # Calculate contact score
        contact_info.contact_score = self._calculate_contact_score(contact_info)
        
        logger.info(f"Contact extraction completed: {len(contact_info.emails)} emails, "
                   f"{len(contact_info.social_links)} social links, score: {contact_info.contact_score:.2f}")
        
        return contact_info
    
    def _extract_basic_info(self, profile_data: Dict, contact_info: ContactInfo) -> None:
        """Extract basic contact info from profile data"""
        # Extract email
        if profile_data.get('email'):
            if self._is_valid_email(profile_data['email']):
                contact_info.emails.add(profile_data['email'])
        
        # Extract website/blog
        blog_url = profile_data.get('blog') or profile_data.get('website')
        if blog_url and self._is_valid_url(blog_url):
            contact_info.website = blog_url
            if self._is_personal_site(blog_url):
                contact_info.personal_site = blog_url
        
        # Extract social profiles
        if profile_data.get('twitter_username'):
            contact_info.twitter = f"https://twitter.com/{profile_data['twitter_username']}"
            contact_info.social_links['twitter'] = contact_info.twitter
    
    def _extract_github_specific(self, github_user, contact_info: ContactInfo) -> None:
        """Extract GitHub-specific contact information"""
        # Add GitHub profile to social links
        if hasattr(github_user, 'html_url'):
            contact_info.social_links['github'] = github_user.html_url
        
        # Extract from bio
        if hasattr(github_user, 'bio') and github_user.bio:
            self._extract_from_text(github_user.bio, contact_info)
    
    def _identify_scraping_targets(self, profile_data: Dict, contact_info: ContactInfo) -> List[str]:
        """Identify URLs that should be scraped for contact information"""
        urls = []
        
        # Personal website/blog (highest priority)
        if contact_info.personal_site:
            urls.append(contact_info.personal_site)
        elif contact_info.website:
            urls.append(contact_info.website)
        
        # GitHub profile page for repository analysis
        if profile_data.get('html_url'):
            urls.append(profile_data['html_url'])
        
        return urls
    
    def _perform_multi_level_extraction(self, urls: List[str], contact_info: ContactInfo) -> None:
        """Perform multi-level intelligent extraction"""
        visited_urls = set()
        
        for url in urls:
            if url not in visited_urls:
                self._scrape_and_extract(url, contact_info, 0, visited_urls)
    
    def _scrape_and_extract(self, url: str, contact_info: ContactInfo, depth: int, visited_urls: set) -> None:
        """Scrape URL and extract contact information with depth control"""
        # Depth and loop protection
        if depth >= self.config.max_drilling_depth or url in visited_urls:
            return
        
        visited_urls.add(url)
        logger.debug(f"Scraping URL (depth {depth}): {url}")
        
        try:
            # Scrape content using Jina.ai
            content = self._scrape_url(url)
            if not content:
                return
            
            # Extract contact info from content
            self._extract_from_content(content, url, contact_info, depth, visited_urls)
            
        except Exception as e:
            logger.debug(f"Error scraping {url}: {e}")
    
    def _scrape_url(self, url: str) -> Optional[str]:
        """Scrape URL content using Jina.ai"""
        if not self.jina_token:
            logger.warning("Jina token not configured - skipping web scraping")
            return None
        
        try:
            response = requests.get(
                f"{self.jina_base_url}/{url}",
                headers={'Authorization': f'Bearer {self.jina_token}'},
                timeout=self.config.request_timeout
            )
            
            if response.status_code == 200:
                return response.text
            else:
                logger.debug(f"Jina.ai request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.debug(f"Error scraping {url}: {e}")
            return None
    
    def _extract_from_content(self, content: str, source_url: str, contact_info: ContactInfo, 
                            depth: int, visited_urls: set) -> None:
        """Extract contact information from scraped content"""
        # Try intelligent extraction first
        if self.openai_client and len(content) > 100:
            try:
                self._intelligent_extract(content, source_url, contact_info, depth, visited_urls)
                return
            except Exception as e:
                logger.debug(f"OpenAI extraction failed, falling back to regex: {e}")
        
        # Fallback to regex extraction
        self._regex_extract(content, contact_info)
    
    def _intelligent_extract(self, content: str, source_url: str, contact_info: ContactInfo,
                           depth: int, visited_urls: set) -> None:
        """Use OpenAI for intelligent contact extraction and link discovery"""
        # Truncate content if too long
        if len(content) > 4000:
            content = content[:4000] + "..."
        
        # Create prompt based on depth
        if depth == 0:
            prompt = self._create_level_0_prompt(content, source_url)
        elif depth == 1:
            prompt = self._create_level_1_prompt(content, source_url)
        else:
            prompt = self._create_level_2_prompt(content, source_url)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            self._parse_llm_response(result, contact_info, depth, source_url, visited_urls)
            
        except Exception as e:
            logger.debug(f"OpenAI API call failed: {e}")
            self._regex_extract(content, contact_info)
    
    def _create_level_0_prompt(self, content: str, source_url: str) -> str:
        """Create prompt for level 0 analysis (initial contact extraction + link discovery)"""
        return f"""Analyze this web content for contact information AND identify promising links for deeper analysis.

Source URL: {source_url}
Content: {content}

Please extract:
1. Email addresses (ignore fake/example emails)
2. Social media profiles (LinkedIn, Twitter, etc.)
3. Phone numbers
4. Personal websites

Also identify up to 4 most promising links for further exploration:
- Contact/About pages
- Personal portfolio sites  
- CV/Resume pages
- Professional profiles

Respond in this format:
EMAILS: email1@example.com, email2@example.com
LINKEDIN: https://linkedin.com/in/profile
TWITTER: https://twitter.com/username
PHONE: +1234567890
WEBSITE: https://personal-site.com
NEXT_LINKS: https://site.com/contact, https://site.com/about"""
    
    def _create_level_1_prompt(self, content: str, source_url: str) -> str:
        """Create prompt for level 1 analysis (focused contact extraction)"""
        return f"""Analyze this contact-focused page for direct contact information.

Source URL: {source_url}
Content: {content}

Focus on extracting:
1. Direct contact emails
2. Professional social profiles
3. Contact forms or methods
4. Up to 3 additional contact-relevant links

EMAILS: 
LINKEDIN: 
TWITTER: 
PHONE: 
NEXT_LINKS: """
    
    def _create_level_2_prompt(self, content: str, source_url: str) -> str:
        """Create prompt for level 2 analysis (final extraction, no more drilling)"""
        return f"""Extract final contact information from this page. No need to identify more links.

Source URL: {source_url}
Content: {content}

Extract:
EMAILS: 
LINKEDIN: 
TWITTER: 
PHONE: """
    
    def _parse_llm_response(self, response: str, contact_info: ContactInfo, depth: int, 
                          source_url: str, visited_urls: set) -> None:
        """Parse LLM response and update contact info"""
        lines = response.split('\n')
        next_links = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('EMAILS:'):
                emails = line.replace('EMAILS:', '').strip()
                if emails and emails != 'None':
                    for email in emails.split(','):
                        email = email.strip()
                        if self._is_valid_email(email):
                            contact_info.emails.add(email)
            
            elif line.startswith('LINKEDIN:'):
                linkedin = line.replace('LINKEDIN:', '').strip()
                if linkedin and linkedin.startswith('http'):
                    contact_info.linkedin = linkedin
                    contact_info.social_links['linkedin'] = linkedin
            
            elif line.startswith('TWITTER:'):
                twitter = line.replace('TWITTER:', '').strip()
                if twitter and twitter.startswith('http'):
                    contact_info.twitter = twitter
                    contact_info.social_links['twitter'] = twitter
            
            elif line.startswith('PHONE:'):
                phone = line.replace('PHONE:', '').strip()
                if phone and phone != 'None':
                    contact_info.phone = phone
            
            elif line.startswith('WEBSITE:'):
                website = line.replace('WEBSITE:', '').strip()
                if website and website.startswith('http'):
                    if not contact_info.website:
                        contact_info.website = website
                    if self._is_personal_site(website):
                        contact_info.personal_site = website
            
            elif line.startswith('NEXT_LINKS:') and depth < 2:
                links = line.replace('NEXT_LINKS:', '').strip()
                if links and links != 'None':
                    for link in links.split(','):
                        link = link.strip()
                        if link.startswith('http') and self._is_safe_drill_down_link(link, source_url):
                            next_links.append(link)
        
        # Process next level links
        max_links = self.config.max_links_per_level.get(depth + 1, 2)
        for link in next_links[:max_links]:
            self._scrape_and_extract(link, contact_info, depth + 1, visited_urls)
    
    def _regex_extract(self, content: str, contact_info: ContactInfo) -> None:
        """Fallback regex-based extraction"""
        # Extract emails
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.IGNORECASE)
        emails = email_pattern.findall(content)
        for email in emails:
            if self._is_valid_email(email):
                contact_info.emails.add(email)
        
        # Extract social profiles
        for platform, pattern in self.SOCIAL_PATTERNS.items():
            matches = pattern.findall(content)
            if matches:
                url = f"https://{platform}.com/{'in/' if platform == 'linkedin' else ''}{matches[0]}"
                contact_info.social_links[platform] = url
                if platform == 'linkedin':
                    contact_info.linkedin = url
                elif platform == 'twitter':
                    contact_info.twitter = url
    
    def _extract_from_text(self, text: str, contact_info: ContactInfo) -> None:
        """Extract contact info from plain text (like bio)"""
        # Extract emails
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.IGNORECASE)
        emails = email_pattern.findall(text)
        for email in emails:
            if self._is_valid_email(email):
                contact_info.emails.add(email)
        
        # Extract social handles
        for platform, pattern in self.SOCIAL_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                url = f"https://{platform}.com/{'in/' if platform == 'linkedin' else ''}{matches[0]}"
                contact_info.social_links[platform] = url
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if email is valid and not a fake/template email"""
        if not email or len(email) < 5:
            return False
        
        # Check against fake patterns
        email_lower = email.lower()
        for pattern in self.FAKE_EMAIL_PATTERNS:
            if pattern in email_lower:
                return False
        
        # Basic email validation
        if '@' not in email or '.' not in email.split('@')[1]:
            return False
        
        return True
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        if not url:
            return False
        return url.startswith(('http://', 'https://'))
    
    def _is_personal_site(self, url: str) -> bool:
        """Determine if URL is likely a personal website"""
        personal_indicators = [
            'github.io', 'gitlab.io', 'netlify.app', 'vercel.app',
            'personal', 'portfolio', 'blog', 'me.', 'my.', '.me'
        ]
        return any(indicator in url.lower() for indicator in personal_indicators)
    
    def _is_safe_drill_down_link(self, url: str, parent_url: str) -> bool:
        """Check if link is safe and worthwhile for drilling down"""
        url_lower = url.lower()
        
        # Skip certain patterns
        skip_patterns = [
            '/topics/', '/trending/', '/hashtag/', '/search/',
            'github.com/topics', 'github.com/trending',
            'linkedin.com/feed', 'twitter.com/search'
        ]
        
        if any(pattern in url_lower for pattern in skip_patterns):
            return False
        
        # Prioritize contact-relevant pages
        good_patterns = [
            '/contact', '/about', '/cv', '/resume', '/portfolio',
            'contact.', 'about.', '.me', 'personal', 'bio'
        ]
        
        return any(pattern in url_lower for pattern in good_patterns) or url != parent_url
    
    def _calculate_contact_score(self, contact_info: ContactInfo) -> float:
        """Calculate contact information richness score (0-1)"""
        score = 0.0
        
        # Email presence (40% weight)
        if contact_info.emails:
            score += 0.4
            # Bonus for multiple emails
            if len(contact_info.emails) > 1:
                score += 0.1
        
        # Social media presence (30% weight)
        social_weight = 0.3 / 3  # Distribute across platforms
        if contact_info.linkedin:
            score += social_weight
        if contact_info.twitter:
            score += social_weight
        if len(contact_info.social_links) > 2:
            score += social_weight
        
        # Personal website (20% weight)
        if contact_info.personal_site:
            score += 0.2
        
        # Additional contact methods (10% weight)
        if contact_info.phone:
            score += 0.1
        
        return min(score, 1.0)