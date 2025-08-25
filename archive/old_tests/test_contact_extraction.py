#!/usr/bin/env python3
"""
Test contact extraction in detail
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sources.github_source import GitHubSource

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_contact_extraction():
    """Test contact extraction with detailed output"""
    print("🧪 Testing Contact Extraction System")
    print("=" * 50)
    
    try:
        # Initialize GitHub source
        github_source = GitHubSource({})
        
        # Test with 1 user
        print("🔍 Searching for 1 test user...")
        talents = github_source.search({'max_results': 1})
        
        if not talents:
            print("❌ No talents found")
            return
        
        talent = talents[0]
        print(f"\n🎯 Analyzing: {talent.name}")
        print(f"   GitHub: {talent.github_url}")
        
        # Show contact info from platform_data
        github_data = talent.platform_data.get('github', {})
        contact_info = github_data.get('contact_info')
        
        if contact_info:
            print(f"\n📞 Contact Information:")
            print(f"   Emails: {contact_info.get('emails', [])}")
            print(f"   LinkedIn: {contact_info.get('linkedin', 'N/A')}")
            print(f"   Twitter: {contact_info.get('twitter', 'N/A')}")
            print(f"   Personal Site: {contact_info.get('personal_site', 'N/A')}")
            print(f"   Phone: {contact_info.get('phone', 'N/A')}")
            print(f"   Contact Score: {contact_info.get('contact_score', 0):.2f}")
            print(f"   Social Links: {contact_info.get('social_links', {})}")
        else:
            print("❌ No contact information extracted")
        
        # Show full platform data
        print(f"\n📊 Full GitHub Platform Data:")
        print(json.dumps(github_data, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_contact_extraction()