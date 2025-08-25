#!/usr/bin/env python3
"""
Run Talent-Seekr pipeline without Notion integration
Perfect for testing or when Notion database isn't ready yet
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sources.github_source import GitHubSource
from utils.deduplication import TalentDeduplicator

def run_github_only_pipeline(max_results=20):
    """Run GitHub discovery without Notion"""
    load_dotenv()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Talent-Seekr - GitHub-Only Discovery Mode")
    logger.info("=" * 50)
    logger.info("💡 Running without Notion - results displayed only")
    
    start_time = datetime.now()
    
    try:
        # Initialize components
        github_source = GitHubSource({})
        deduplicator = TalentDeduplicator()
        
        # Run GitHub discovery
        logger.info(f"🔍 Discovering Australian AI talent on GitHub (max: {max_results})...")
        
        query_params = {'max_results': max_results}
        talents = github_source.search(query_params)
        
        if not talents:
            logger.warning("No talents found. Check GitHub token and connection.")
            return
        
        # Deduplicate
        logger.info("🔄 Removing duplicates...")
        unique_talents = deduplicator.deduplicate_talents(talents)
        
        # Filter by quality
        quality_threshold = 35
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
            
            for i, talent in enumerate(qualified_talents[:15], 1):  # Show top 15
                logger.info(f"{i:2d}. {talent.name}")
                logger.info(f"    Score: {talent.github_score:.1f} | AU: {talent.au_strength:.1f} | 📍 {talent.location}")
                logger.info(f"    🔗 {talent.github_url}")
                
                github_data = talent.platform_data.get('github', {})
                repos = github_data.get('public_repos', 0)
                followers = github_data.get('followers', 0)
                logger.info(f"    📦 {repos} repos | 👥 {followers} followers")
                logger.info("")
        
        # Performance summary
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"⚡ Pipeline completed in {duration:.1f} seconds")
        
        # Export results to CSV for easy review
        if qualified_talents:
            csv_file = f"talents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(csv_file, 'w') as f:
                f.write("Name,Score,AU_Strength,Location,GitHub_URL,Repos,Followers\n")
                for talent in qualified_talents:
                    github_data = talent.platform_data.get('github', {})
                    repos = github_data.get('public_repos', 0)
                    followers = github_data.get('followers', 0)
                    
                    f.write(f'"{talent.name}",{talent.github_score:.1f},{talent.au_strength:.1f}')
                    f.write(f',"{talent.location}",{talent.github_url},{repos},{followers}\n')
            
            logger.info(f"📄 Results exported to: {csv_file}")
        
        logger.info(f"\n🎉 GitHub-Only Discovery Completed!")
        logger.info(f"📈 Final Stats: {len(qualified_talents)}/{len(talents)} qualified talents in {duration:.1f}s")
        logger.info(f"\n💡 To enable Notion sync:")
        logger.info(f"   1. Share your Notion database with 'Talent-Seekr' integration")
        logger.info(f"   2. Run: source .venv/bin/activate && python verify_notion_setup.py")
        logger.info(f"   3. When ready: source .venv/bin/activate && python mvp_demo.py")
        
        return {
            'total_found': len(talents),
            'unique': len(unique_talents),
            'qualified': len(qualified_talents),
            'duration': duration,
            'csv_file': csv_file if qualified_talents else None
        }
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        raise

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Talent-Seekr GitHub-Only Mode')
    parser.add_argument('--max-results', type=int, default=20, 
                       help='Maximum talents to discover (default: 20)')
    
    args = parser.parse_args()
    
    try:
        results = run_github_only_pipeline(args.max_results)
        
        if results:
            print(f"\n✅ Success! Check {results['csv_file']} for results")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()