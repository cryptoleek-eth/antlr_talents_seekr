#!/usr/bin/env python3
"""
Configuration settings for the talent discovery application
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class APIConfig:
    """API configuration class"""
    github_token: str = None
    notion_token: str = None
    notion_database_id: str = None
    jina_token: str = None
    openai_api_key: str = None
    twitter_api_key: str = None

    @classmethod
    def from_env(cls):
        """Create APIConfig from environment variables"""
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
            notion_token=os.getenv("NOTION_TOKEN"),
            notion_database_id=os.getenv("NOTION_DATABASE_ID"),
            jina_token=os.getenv("JINA_API_TOKEN"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            twitter_api_key=os.getenv("TWITTER_API_KEY")
        )

    def is_github_configured(self) -> bool:
        """Check if GitHub API is properly configured"""
        return bool(self.github_token and len(self.github_token) > 20)

    def is_notion_configured(self) -> bool:
        """Check if Notion API is properly configured"""
        return bool(
            self.notion_token and
            self.notion_database_id and
            self.notion_token.startswith("ntn_")
        )

    def is_jina_configured(self) -> bool:
        """Check if Jina API is properly configured"""
        return bool(self.jina_token and len(self.jina_token) > 10)

    def is_openai_configured(self) -> bool:
        """Check if OpenAI API is properly configured"""
        return bool(self.openai_api_key and self.openai_api_key.startswith("sk-"))

    def is_twitter_configured(self) -> bool:
        """Check if Twitter API is properly configured"""
        return bool(self.twitter_api_key and len(self.twitter_api_key) > 20)

@dataclass
class SearchConfig:
    """Search configuration settings"""
    max_results: int = 50
    min_followers: int = 100
    min_repos: int = 5
    min_commits: int = 10
    score_threshold: float = 0.6
    batch_size: int = 10
    max_talents_per_run: int = 100
    keywords: List[str] = None
    locations: List[str] = None
    default_language: str = "python"
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = [
                "machine learning", "artificial intelligence", "deep learning",
                "data science", "neural networks", "computer vision", "nlp",
                "tensorflow", "pytorch", "scikit-learn"
            ]
        if self.locations is None:
            self.locations = ["Australia", "Sydney", "Melbourne", "Brisbane", "Perth"]

@dataclass
class ContactExtractionConfig:
    """Contact extraction configuration"""
    max_drilling_depth: int = 2
    timeout: int = 10
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
            "github": {
                "configured": self.api.is_github_configured(),
                "status": "Ready" if self.api.is_github_configured() else "Token missing or invalid"
            },
            "notion": {
                "configured": self.api.is_notion_configured(),
                "status": "Ready" if self.api.is_notion_configured() else "Token or database ID missing"
            },
            "jina": {
                "configured": self.api.is_jina_configured(),
                "status": "Ready" if self.api.is_jina_configured() else "Token missing"
            },
            "openai": {
                "configured": self.api.is_openai_configured(),
                "status": "Ready" if self.api.is_openai_configured() else "Using regex fallback"
            },
            "twitter": {
                "configured": self.api.is_twitter_configured(),
                "status": "Ready" if self.api.is_twitter_configured() else "API key missing"
            }
        }

# Global settings instance
settings = Settings()
