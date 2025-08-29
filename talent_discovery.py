#!/usr/bin/env python3
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
from sources.twitter_source import TwitterSource
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
    - Multi-source talent search (GitHub, Twitter)
    - Intelligent contact extraction
    - Notion database integration
    - Comprehensive reporting
    """

    def __init__(self):
        """Initialize application with configuration validation"""
        self.github_source = None
        self.twitter_source = None
        self.notion_db = None

        # Validate configuration
        config_status = settings.validate_configuration()
        self._report_configuration_status(config_status)

        # Initialize services
        try:
            if config_status['github']['configured']:
                self.github_source = GitHubSource()
                logger.info("GitHub source initialized")

            if config_status['twitter']['configured']:
                self.twitter_source = TwitterSource()
                logger.info("Twitter source initialized")

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
                        sources: Optional[List[str]] = None,
                        save_to_notion: bool = True) -> Dict[str, Any]:
        """
        Main talent discovery workflow

        Args:
            max_results: Maximum number of talents to discover
            keywords: AI/ML keywords to search for
            locations: Geographic locations to focus on
            sources: List of sources to search (github, twitter). Defaults to all available
            save_to_notion: Whether to save results to Notion database

        Returns:
            Discovery results summary
        """
        logger.info(f"Starting talent discovery (max_results={max_results})")

        # Build search parameters
        search_params = {
            'keywords': keywords or settings.search.keywords,
            'location': locations or settings.search.locations,
            'min_followers': 1,  # Much lower for broader search
            'min_repos': 1,      # Much lower for broader search
            'language': settings.search.default_language,
            'sort': 'followers'
        }

        # Determine which sources to use
        available_sources = []
        if sources is None:
            sources = ['github', 'twitter']  # Default to all available
        
        if 'github' in sources and self.github_source:
            available_sources.append(('github', self.github_source))
        if 'twitter' in sources and self.twitter_source:
            available_sources.append(('twitter', self.twitter_source))
        
        if not available_sources:
            raise ValueError("No configured sources available for the requested search")
        
        # Execute discovery
        start_time = datetime.now()
        all_talents = []
        
        try:
            # Search across all available sources
            for source_name, source_instance in available_sources:
                logger.info(f"Executing {source_name} search...")
                source_talents = source_instance.search(search_params)
                logger.info(f"Found {len(source_talents)} talents from {source_name}")
                all_talents.extend(source_talents)

            discovery_time = datetime.now() - start_time
            logger.info(f"Discovery completed in {discovery_time.total_seconds():.1f} seconds")
            
            # Sort and select top talents
            talents = self._rank_and_filter_talents(all_talents, max_results)

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
        """Rank talents by combined score and filter to max_results"""
        # Sort by combined score (descending)
        ranked_talents = sorted(talents, key=lambda t: t.total_score, reverse=True)
        
        # Apply deduplication if needed
        from utils.deduplication import deduplicate_talents
        deduplicated = deduplicate_talents(ranked_talents)
        
        return deduplicated[:max_results]

    def _calculate_quality_metrics(self, talents: List[Talent]) -> Dict[str, Any]:
        """Calculate quality metrics for discovered talents"""
        if not talents:
            return {'avg_score': 0, 'avg_au_strength': 0, 'contact_coverage': 0}
        
        avg_score = sum(t.total_score for t in talents) / len(talents)
        avg_au_strength = sum(t.au_strength for t in talents) / len(talents)
        
        # Calculate contact coverage
        with_contacts = sum(1 for t in talents if t.email)
        contact_coverage = with_contacts / len(talents) if talents else 0
        
        return {
            'avg_score': round(avg_score, 2),
            'avg_au_strength': round(avg_au_strength, 2),
            'contact_coverage': round(contact_coverage, 2)
        }

    def _report_configuration_status(self, config_status: Dict[str, Any]):
        """Report configuration status"""
        logger.info("=== CONFIGURATION STATUS ===")
        for service, status in config_status.items():
            status_text = " CONFIGURED" if status['configured'] else " NOT CONFIGURED"
            logger.info(f"{service.upper()}: {status_text}")
            if not status['configured'] and 'reason' in status:
                logger.warning(f"  Reason: {status['reason']}")

    def _report_discovery_results(self, results: Dict[str, Any]):
        """Report discovery results"""
        if results['success']:
            logger.info("=== DISCOVERY RESULTS ===")
            logger.info(f"Talents found: {results['talents_found']}")
            logger.info(f"Discovery time: {results['discovery_time']:.1f}s")
            logger.info(f"Quality metrics: {results['quality_metrics']}")
            
            if results['notion_results']:
                logger.info(f"Notion records created: {results['notion_results']['created']}")
        else:
            logger.error(f"Discovery failed: {results['error']}")

    def get_status(self) -> Dict[str, Any]:
        """Get application status"""
        config_status = settings.validate_configuration()
        
        return {
            'github_configured': config_status['github']['configured'],
            'twitter_configured': config_status['twitter']['configured'],
            'notion_configured': config_status['notion']['configured'],
            'jina_configured': config_status['jina']['configured'],
            'openai_configured': config_status['openai']['configured'],
            'github_source_ready': self.github_source is not None,
            'twitter_source_ready': self.twitter_source is not None,
            'notion_db_ready': self.notion_db is not None and self.notion_db.is_enabled()
        }

def main():
    """Application entry point"""
    parser = argparse.ArgumentParser(description='Australian AI Talent Discovery')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of talents to discover')
    parser.add_argument('--keywords', nargs='+', help='AI/ML keywords to search for')
    parser.add_argument('--locations', nargs='+', help='Geographic locations to focus on')
    parser.add_argument('--sources', nargs='+', choices=['github', 'twitter'], help='Sources to search (github, twitter)')
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
            sources=args.sources,
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
