"""
Talent Discovery Application
Clean, production-ready talent discovery system for Australian AI talent
"""

import logging
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
import argparse

from config import settings
from sources.github_source import GitHubSource
from core.notion_client import NotionTalentDB
from core.talent import Talent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('talent_discovery.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

class TalentDiscoveryApp:
    """
    Main application class for talent discovery
    
    Features:
    - Configuration validation
    - GitHub talent search
    - Intelligent contact extraction
    - Notion database integration
    - Comprehensive reporting
    """
    
    def __init__(self):
        """Initialize application with configuration validation"""
        self.github_source = None
        self.notion_db = None
        
        # Validate configuration
        config_status = settings.validate_configuration()
        self._report_configuration_status(config_status)
        
        # Initialize services
        try:
            if config_status['github']['configured']:
                self.github_source = GitHubSource()
                logger.info("GitHub source initialized")
            
            if config_status['notion']['configured']:
                self.notion_db = NotionTalentDB()
                logger.info("Notion database initialized")
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            raise
    
    def discover_talents(self, 
                        max_results: int = 10,
                        keywords: Optional[List[str]] = None,
                        locations: Optional[List[str]] = None,
                        save_to_notion: bool = True) -> Dict[str, Any]:
        """
        Main talent discovery workflow
        
        Args:
            max_results: Maximum number of talents to discover
            keywords: AI/ML keywords to search for
            locations: Geographic locations to focus on
            save_to_notion: Whether to save results to Notion database
            
        Returns:
            Discovery results summary
        """
        logger.info(f"Starting talent discovery: {max_results} talents, save_to_notion={save_to_notion}")
        
        if not self.github_source:
            raise ValueError("GitHub source not available - check configuration")
        
        # Prepare search parameters with more permissive defaults
        search_params = {
            'max_results': max_results,
            'keywords': keywords or settings.search.keywords,
            'location': locations or settings.search.locations,
            'min_followers': 1,  # Much lower for broader search
            'min_repos': 1,      # Much lower for broader search
            'language': settings.search.default_language,
            'sort': 'followers'
        }
        
        # Execute discovery
        start_time = datetime.now()
        
        try:
            # Search for talents
            logger.info("Executing GitHub search...")
            talents = self.github_source.search(search_params)
            
            discovery_time = datetime.now() - start_time
            logger.info(f"Discovery completed in {discovery_time.total_seconds():.1f} seconds")
            
            # Sort and select top talents
            talents = self._rank_and_filter_talents(talents, max_results)
            
            # Save to Notion if configured and requested
            notion_results = None
            if save_to_notion and self.notion_db and self.notion_db.is_enabled():
                logger.info("Saving talents to Notion database...")
                notion_results = self.notion_db.batch_create_talents(talents)
            
            # Generate summary
            results = {
                'success': True,
                'discovery_time': discovery_time.total_seconds(),
                'search_params': search_params,
                'talents_found': len(talents),
                'talents': [t.to_dict() for t in talents],
                'notion_results': notion_results,
                'quality_metrics': self._calculate_quality_metrics(talents),
                'timestamp': datetime.now().isoformat()
            }
            
            self._report_discovery_results(results)
            return results
            
        except Exception as e:
            logger.error(f"Talent discovery failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'discovery_time': (datetime.now() - start_time).total_seconds()
            }
    
    def _rank_and_filter_talents(self, talents: List[Talent], max_results: int) -> List[Talent]:
        """Rank talents by total score and filter to top results"""
        # Sort by total score (descending)
        sorted_talents = sorted(talents, key=lambda t: t.total_score, reverse=True)
        
        # Return top results
        top_talents = sorted_talents[:max_results]
        
        logger.info(f"Selected top {len(top_talents)} talents from {len(talents)} candidates")
        return top_talents
    
    def _calculate_quality_metrics(self, talents: List[Talent]) -> Dict[str, float]:
        """Calculate quality metrics for discovered talents"""
        if not talents:
            return {}
        
        metrics = {
            'average_total_score': sum(t.total_score for t in talents) / len(talents),
            'average_au_strength': sum(t.au_strength for t in talents) / len(talents),
            'average_github_score': sum(t.github_score for t in talents) / len(talents),
            'average_contact_score': sum(t.contact_score for t in talents) / len(talents),
            'talents_with_email': sum(1 for t in talents if t.email) / len(talents),
            'talents_with_linkedin': sum(1 for t in talents if t.linkedin_url) / len(talents),
            'talents_with_twitter': sum(1 for t in talents if t.twitter_url) / len(talents),
            'talents_with_strong_au_connection': sum(1 for t in talents if t.au_strength >= 0.5) / len(talents)
        }
        
        return {k: round(v, 3) for k, v in metrics.items()}
    
    def _report_configuration_status(self, config_status: Dict[str, Any]) -> None:
        """Report configuration status to user"""
        logger.info("Configuration Status:")
        for service, status in config_status.items():
            logger.info(f"  {service.upper()}: {status['status']}")
    
    def _report_discovery_results(self, results: Dict[str, Any]) -> None:
        """Report discovery results summary"""
        logger.info("=== TALENT DISCOVERY RESULTS ===")
        logger.info(f"Discovery Time: {results['discovery_time']:.1f} seconds")
        logger.info(f"Talents Found: {results['talents_found']}")
        
        if results.get('notion_results'):
            notion = results['notion_results']
            logger.info(f"Notion Results: {notion['created']} created, {notion['duplicates']} duplicates, {notion['errors']} errors")
        
        if results.get('quality_metrics'):
            metrics = results['quality_metrics']
            logger.info(f"Quality Metrics:")
            logger.info(f"  Average Total Score: {metrics['average_total_score']:.3f}")
            logger.info(f"  Average AU Strength: {metrics['average_au_strength']:.3f}")
            logger.info(f"  Talents with Email: {metrics['talents_with_email']:.1%}")
            logger.info(f"  Strong AU Connection: {metrics['talents_with_strong_au_connection']:.1%}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get application status and configuration"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'configuration': settings.validate_configuration(),
            'services': {
                'github_source': self.github_source is not None,
                'notion_db': self.notion_db is not None and self.notion_db.is_enabled()
            }
        }
        
        # Add rate limit info if GitHub is available
        if self.github_source:
            try:
                status['github_rate_limit'] = self.github_source.get_rate_limit_status()
            except Exception as e:
                status['github_rate_limit'] = {'error': str(e)}
        
        return status

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Australian AI Talent Discovery')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of talents to discover')
    parser.add_argument('--keywords', nargs='+', help='AI/ML keywords to search for')
    parser.add_argument('--locations', nargs='+', help='Geographic locations to focus on')
    parser.add_argument('--no-notion', action='store_true', help='Skip saving to Notion database')
    parser.add_argument('--status', action='store_true', help='Show application status and exit')
    
    args = parser.parse_args()
    
    try:
        # Initialize application
        app = TalentDiscoveryApp()
        
        # Handle status request
        if args.status:
            status = app.get_status()
            print("=== APPLICATION STATUS ===")
            for key, value in status.items():
                print(f"{key}: {value}")
            return
        
        # Run talent discovery
        results = app.discover_talents(
            max_results=args.max_results,
            keywords=args.keywords,
            locations=args.locations,
            save_to_notion=not args.no_notion
        )
        
        # Exit with appropriate code
        sys.exit(0 if results['success'] else 1)
        
    except KeyboardInterrupt:
        logger.info("Discovery interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()