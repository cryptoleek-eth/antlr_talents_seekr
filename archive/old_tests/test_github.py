#!/usr/bin/env python3
"""
Test script for GitHub talent discovery
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sources.github_plugin import GitHubPlugin

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_github_plugin():
    """Test the GitHub plugin functionality"""
    
    # Check if token exists
    if not os.getenv('GITHUB_TOKEN'):
        print("❌ GITHUB_TOKEN not found in environment variables")
        return False
    
    try:
        # Initialize plugin
        config = {
            'rate_limit_buffer': 50
        }
        github_plugin = GitHubPlugin(config)
        
        print("✅ GitHub plugin initialized successfully")
        
        # Test search with limited results
        query_params = {
            'queries': ["location:Australia machine learning"],
            'max_results': 5  # Small test
        }
        
        print("🔍 Searching for Australian AI talent...")
        talents = github_plugin.search(query_params)
        
        print(f"📊 Found {len(talents)} talents:")
        
        for talent in talents:
            print(f"\n👤 {talent.name}")
            print(f"   📍 Location: {talent.location}")
            print(f"   🇦🇺 AU Strength: {talent.au_strength:.2f}")
            print(f"   ⭐ GitHub Score: {talent.github_score:.1f}")
            print(f"   🔗 Profile: {talent.github_url}")
            
            # Show AI activity
            ai_activity = talent.platform_data.get('github', {}).get('ai_activity', {})
            ai_repos = ai_activity.get('ai_repo_count', 0)
            if ai_repos > 0:
                print(f"   🤖 AI Repos: {ai_repos}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing GitHub plugin: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing GitHub Talent Discovery")
    print("=" * 40)
    
    success = test_github_plugin()
    
    if success:
        print("\n✅ GitHub integration test completed successfully!")
    else:
        print("\n❌ GitHub integration test failed!")
        sys.exit(1)