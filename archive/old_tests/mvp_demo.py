#!/usr/bin/env python3
"""
Talent-Seekr MVP: Fast AI Founder Discovery Pipeline
Optimized for 3-day development cycle with Notion integration
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
from core.notion_client import NotionTalentDB
from utils.deduplication import TalentDeduplicator

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
        print(f"Warning: Missing environment variables: {missing_vars}")
    
    return config

def setup_logging(config):
    """Setup logging configuration"""
    log_level = getattr(logging, config['logging']['level'], logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def run_mvp_discovery(max_results=20, dry_run=False):
    """Run optimized talent discovery for MVP demo"""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Talent-Seekr MVP - Australian AI Founder Discovery")
    logger.info("=" * 55)
    
    start_time = datetime.now()
    
    try:
        # Initialize components
        github_source = GitHubSource({})
        notion_db = NotionTalentDB()
        deduplicator = TalentDeduplicator()
        
        # Run GitHub discovery
        logger.info("🔍 Discovering Australian AI talent on GitHub...")
        
        query_params = {'max_results': max_results}
        talents = github_source.search(query_params)
        
        if not talents:
            logger.warning("No talents found. Check GitHub token and connection.")
            return
        
        # Deduplicate
        logger.info("🔄 Removing duplicates...")
        unique_talents = deduplicator.deduplicate_talents(talents)
        
        # Filter by quality (score > 30 for MVP)
        quality_threshold = 30
        qualified_talents = [t for t in unique_talents if t.github_score >= quality_threshold]
        
        # Sort by score
        qualified_talents.sort(key=lambda x: x.github_score, reverse=True)
        
        # Display results
        logger.info(f"📊 Discovery Results:")
        logger.info(f"   Raw found: {len(talents)}")
        logger.info(f"   After dedup: {len(unique_talents)}")  
        logger.info(f"   Qualified (score ≥{quality_threshold}): {len(qualified_talents)}")
        
        if qualified_talents:
            logger.info(f"\n🎯 Top Australian AI Founders:")
            logger.info("-" * 60)
            
            for i, talent in enumerate(qualified_talents[:10], 1):
                logger.info(f"{i:2d}. {talent.name}")
                logger.info(f"    Score: {talent.github_score:.1f} | AU: {talent.au_strength:.1f} | 📍 {talent.location}")
                logger.info(f"    🔗 {talent.github_url}")
                
                github_data = talent.platform_data.get('github', {})
                repos = github_data.get('public_repos', 0)
                followers = github_data.get('followers', 0)
                logger.info(f"    📦 {repos} repos | 👥 {followers} followers")
                logger.info("")
        
        # Database sync
        if dry_run:
            logger.info("🏃 Dry run - skipping database write")
        else:
            logger.info("💾 Syncing to Notion database...")
            sync_results = notion_db.batch_create_talents(qualified_talents)
            
            if notion_db.is_enabled():
                logger.info(f"✅ Notion sync: {sync_results['created']} records created")
            else:
                logger.info("ℹ️  Notion not configured - add NOTION_TOKEN and NOTION_DATABASE_ID to .env")
        
        # Performance summary
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"⚡ Pipeline completed in {duration:.1f} seconds")
        
        return {
            'duration': duration,
            'total_found': len(talents),
            'unique': len(unique_talents),
            'qualified': len(qualified_talents),
            'top_talents': qualified_talents[:5]  # Return top 5 for display
        }
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        raise

def main():
    """Main entry point for MVP demo"""
    parser = argparse.ArgumentParser(description='Talent-Seekr MVP - AI Founder Discovery')
    parser.add_argument('--max-results', type=int, default=20, 
                       help='Maximum talents to discover (default: 20)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run without database writes')
    parser.add_argument('--demo', action='store_true',
                       help='Run quick demo with 10 results')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config()
        setup_logging(config)
        
        # Set demo mode
        max_results = 10 if args.demo else args.max_results
        
        # Run discovery
        results = run_mvp_discovery(max_results, args.dry_run)
        
        if results:
            logger = logging.getLogger(__name__)
            logger.info("🎉 MVP Demo Completed Successfully!")
            logger.info(f"📈 Final Stats: {results['qualified']}/{results['total_found']} qualified talents in {results['duration']:.1f}s")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()