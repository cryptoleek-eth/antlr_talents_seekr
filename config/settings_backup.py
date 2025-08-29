"""
Configuration management for Talent-Seekr
Centralized configuration with environment variable handling
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class APIConfig:
    """API configuration settings"""
    github_token: Optional[str] = None
    notion_token: Optional[str] = None
    notion_database_id: Optional[str] = None
    jina_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Create APIConfig from environment variables"""
        return cls(
            github_token=os.getenv('GITHUB_TOKEN'),
            notion_token=os.getenv('NOTION_TOKEN'),
            notion_database_id=os.getenv('NOTION_DATABASE_ID'),
            jina_token=os.getenv('JINA_API_TOKEN'),
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
    
    def is_github_configured(self) -> bool:
        """Check if GitHub API is properly configured"""
        return bool(self.github_token and len(self.github_token) > 20)
    
    def is_notion_configured(self) -> bool:
        """Check if Notion API is properly configured"""
        return bool(
            self.notion_token and 
            self.notion_database_id and
            self.notion_token.startswith('ntn_')
        )
    
    def is_jina_configured(self) -> bool:
        """Check if Jina AI API is properly configured"""
        return bool(self.jina_token and 'jina_' in self.jina_token)
    
    def is_openai_configured(self) -> bool:
        """Check if OpenAI API is properly configured"""
        return bool(
            self.openai_api_key and 
            self.openai_api_key != 'your_openai_api_key_here'
        )

@dataclass
class SearchConfig:
    """Search configuration settings"""
    max_results: int = 10
    min_followers: int = 5
    min_repos: int = 3
    default_language: str = 'python'
    locations: list = None
    keywords: list = None
    
    def __post_init__(self):
        if self.locations is None:
            self.locations = ['Australia', 'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide']
        if self.keywords is None:
            self.keywords = ['machine learning', 'artificial intelligence', 'deep learning', 'AI', 'ML']

@dataclass
class ContactExtractionConfig:
    """Contact extraction configuration"""
    max_drilling_depth: int = 3
    request_timeout: int = 10
    max_links_per_level: Dict[int, int] = None
    enable_fake_email_filtering: bool = True
    
    def __post_init__(self):
        if self.max_links_per_level is None:
            self.max_links_per_level = {0: 4, 1: 3, 2: 2}

class Settings:
    """Main settings class"""
    
    def __init__(self):
        self.api = APIConfig.from_env()
        self.search = SearchConfig()
        self.contact_extraction = ContactExtractionConfig()
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate all configuration and return status"""
        return {
            'github': {
                'configured': self.api.is_github_configured(),
                'status': '✅ Ready' if self.api.is_github_configured() else '❌ Token missing or invalid'
            },
            'notion': {
                'configured': self.api.is_notion_configured(),
                'status': '✅ Ready' if self.api.is_notion_configured() else '❌ Token or database ID missing'
            },
            'jina': {
                'configured': self.api.is_jina_configured(),
                'status': '✅ Ready' if self.api.is_jina_configured() else '❌ Token missing'
            },
            'openai': {
                'configured': self.api.is_openai_configured(),
                'status': '✅ Ready' if self.api.is_openai_configured() else '⚠️ Using regex fallback'
            }
        }

# Global settings instance
settings = Settings()