from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any

@dataclass
class Talent:
    """
    Core talent data model representing a discovered developer
    
    This class encapsulates all information about a talent including:
    - Identity and contact information
    - Platform profiles and scores
    - Australia connection strength
    - Discovery metadata
    """
    
    # Core Identity
    name: str
    email: Optional[str] = None
    
    # Platform Profiles
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    
    # Location and AU Connection
    location: Optional[str] = None
    au_strength: float = 0.0  # 0-1 score indicating connection to Australia
    au_signals: List[str] = field(default_factory=list)
    
    # Quality Scores
    github_score: float = 0.0
    twitter_score: float = 0.0
    contact_score: float = 0.0  # From contact extraction
    total_score: float = 0.0
    
    # Metadata
    platform_data: Dict[str, Any] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    discovered_date: datetime = field(default_factory=datetime.now)
    
    # Notion Status (managed externally)
    status: str = "new"
    notes: str = ""
    
    @classmethod
    def from_github_user(cls, github_user, au_strength: float = 0.0) -> 'Talent':
        """
        Create Talent instance from GitHub user object
        
        Args:
            github_user: GitHub API user object
            au_strength: Pre-calculated Australia connection strength
            
        Returns:
            Talent instance with GitHub data populated
        """
        return cls(
            name=github_user.name or github_user.login,
            email=github_user.email,
            github_url=github_user.html_url,
            location=github_user.location,
            au_strength=au_strength,
            platform_data={
                'github': {
                    'login': github_user.login,
                    'bio': github_user.bio,
                    'company': github_user.company,
                    'blog': github_user.blog,
                    'public_repos': getattr(github_user, 'public_repos', 0),
                    'followers': getattr(github_user, 'followers', 0),
                    'following': getattr(github_user, 'following', 0),
                    'created_at': github_user.created_at.isoformat() if hasattr(github_user, 'created_at') and github_user.created_at else None
                }
            },
            sources=['github']
        )
    
    def add_contact_info(self, contact_info) -> None:
        """
        Add extracted contact information to talent
        
        Args:
            contact_info: ContactInfo object from contact extraction service
        """
        # Update email if found
        if contact_info.emails:
            self.email = list(contact_info.emails)[0]
        
        # Update social profiles
        if contact_info.linkedin:
            self.linkedin_url = contact_info.linkedin
        if contact_info.twitter:
            self.twitter_url = contact_info.twitter
        
        # Update contact score
        self.contact_score = contact_info.contact_score
        
        # Recalculate total score
        self._calculate_total_score()
    
    def add_au_signals(self, signals: List[str]) -> None:
        """Add Australia connection signals"""
        self.au_signals.extend(signals)
    
    def _calculate_total_score(self) -> None:
        """Calculate weighted total score from all components"""
        # Weighted scoring: GitHub (40%), AU strength (30%), Contact (20%), Twitter (10%)
        self.total_score = (
            self.github_score * 0.4 +
            self.au_strength * 0.3 +
            self.contact_score * 0.2 +
            self.twitter_score * 0.1
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert talent to dictionary for serialization"""
        return {
            'name': self.name,
            'email': self.email,
            'github_url': self.github_url,
            'linkedin_url': self.linkedin_url,
            'twitter_url': self.twitter_url,
            'location': self.location,
            'au_strength': self.au_strength,
            'au_signals': self.au_signals,
            'github_score': self.github_score,
            'twitter_score': self.twitter_score,
            'contact_score': self.contact_score,
            'total_score': self.total_score,
            'sources': self.sources,
            'status': self.status,
            'notes': self.notes,
            'discovered_date': self.discovered_date.isoformat()
        }
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        return f"Talent(name='{self.name}', total_score={self.total_score:.2f}, au_strength={self.au_strength:.2f})"