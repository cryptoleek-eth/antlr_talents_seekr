#!/usr/bin/env python3
"""
Talent-Seekr: AI Founder Discovery Pipeline
Main entry point for talent discovery system
"""

import os
import sys
import logging
import argparse
import yaml
from datetime import datetime
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sources.github_source import GitHubSource

def load_config():
    """Load configuration from config.yaml and environment variables"""
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Load environment variables
    load_dotenv()
    
    # Validate required environment variables
    required_env_vars = ['GITHUB_TOKEN']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    return config

def setup_logging(config):
    """Setup logging configuration"""
    log_level = getattr(logging, config['logging']['level'], logging.INFO)
    log_format = config['logging']['format']
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
        ]
    )

def run_discovery(config, sources=None, dry_run=False):
    """Run the talent discovery pipeline"""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Talent-Seekr Discovery Pipeline")
    logger.info("=" * 50)
    
    all_talents = []
    
    # GitHub Discovery
    if not sources or 'github' in sources:
        if config['sources']['github']['enabled']:
            logger.info("🔍 Running GitHub talent discovery...")
            
            try:
                github_source = GitHubSource(config['sources']['github'])
                
                query_params = {
                    'queries': config['sources']['github']['search_queries'],
                    'max_results': config['sources']['github']['max_results_per_query']
                }
                
                github_talents = github_source.search(query_params)
                all_talents.extend(github_talents)
                
                logger.info(f"✅ GitHub: Found {len(github_talents)} talents")
                
            except Exception as e:
                logger.error(f"❌ GitHub discovery failed: {e}")
    
    # Filter by quality threshold
    quality_threshold = config['pipeline']['score_threshold']
    qualified_talents = [t for t in all_talents if t.github_score >= quality_threshold]
    
    logger.info(f"📊 Discovery Summary:")
    logger.info(f"   Total found: {len(all_talents)}")
    logger.info(f"   Quality threshold ({quality_threshold}): {len(qualified_talents)}")
    
    # Display results
    if qualified_talents:
        logger.info(f"\n🎯 Top Qualified Talents:")
        for i, talent in enumerate(sorted(qualified_talents, key=lambda x: x.github_score, reverse=True)[:10]):
            logger.info(f"   {i+1:2d}. {talent.name}")
            logger.info(f"       Score: {talent.github_score:.1f} | AU: {talent.au_strength:.2f} | Location: {talent.location}")
            logger.info(f"       GitHub: {talent.github_url}")
            
            # Show AI activity
            ai_activity = talent.platform_data.get('github', {}).get('ai_activity', {})
            ai_repos = ai_activity.get('ai_repo_count', 0)
            ai_stars = ai_activity.get('total_ai_stars', 0)
            if ai_repos > 0:
                logger.info(f"       AI Activity: {ai_repos} repos, {ai_stars} stars")
            logger.info("")
    
    if dry_run:
        logger.info("🏃 Dry run completed - no database writes performed")
    else:
        logger.info("💾 Ready for database integration (Notion API)")
        # TODO: Add Notion integration here
    
    return {
        'total_found': len(all_talents),
        'qualified': len(qualified_talents),
        'talents': qualified_talents
    }

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Talent Discovery Pipeline')
    parser.add_argument('--sources', type=str, default='github', 
                       help='Comma-separated list of sources (github,twitter)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run without database writes')
    parser.add_argument('--score-threshold', type=int, 
                       help='Override score threshold')
    parser.add_argument('--max-results', type=int, 
                       help='Maximum results to process')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config()
        setup_logging(config)
        
        # Override config with CLI arguments
        if args.score_threshold:
            config['pipeline']['score_threshold'] = args.score_threshold
        
        if args.max_results:
            config['sources']['github']['max_results_per_query'] = args.max_results
        
        # Parse sources
        sources = [s.strip() for s in args.sources.split(',')] if args.sources else None
        
        # Run discovery
        results = run_discovery(config, sources, args.dry_run)
        
        logger = logging.getLogger(__name__)
        logger.info("✅ Pipeline completed successfully!")
        logger.info(f"📈 Results: {results['qualified']}/{results['total_found']} qualified talents discovered")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()