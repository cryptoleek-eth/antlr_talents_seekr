#!/usr/bin/env python3
"""
Test enhanced contact extraction with Alzayat's profile specifically
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv
from github import Github

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.contact_extractor import ContactExtractor

# Load environment variables
load_dotenv()

# Setup logging to see debug messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_alzayat_profile():
    """Test contact extraction specifically with Alzayat Saleh's profile"""
    print("🧪 Testing Enhanced Contact Extraction - Alzayat Saleh")
    print("=" * 60)
    
    try:
        # Initialize GitHub and contact extractor
        token = os.getenv('GITHUB_TOKEN')
        github = Github(token)
        extractor = ContactExtractor()
        
        # Get Alzayat's profile
        print("🔍 Fetching Alzayat's GitHub profile...")
        user = github.get_user("alzayats")
        
        print(f"👤 User: {user.name or user.login}")
        print(f"🔗 Profile: {user.html_url}")
        print(f"📝 Bio: {user.bio}")
        print(f"🌐 Website: {user.blog}")
        
        # Test contact extraction
        print(f"\n🔍 Running enhanced contact extraction...")
        contact_info = extractor.extract_from_github_profile(user)
        
        print(f"\n📞 Contact Information Extracted:")
        print("-" * 40)
        print(f"Emails: {list(contact_info.emails)}")
        print(f"LinkedIn: {contact_info.linkedin}")
        print(f"Twitter: {contact_info.twitter}")
        print(f"Personal Site: {contact_info.personal_site}")
        print(f"Website: {contact_info.website}")
        print(f"Phone: {contact_info.phone}")
        print(f"Contact Score: {contact_info.contact_score:.2f} ({contact_info.contact_score*100:.0f}%)")
        print(f"Social Links: {contact_info.social_links}")
        
        if contact_info.contact_score > 0:
            print(f"\n✅ SUCCESS: Contact extraction improved!")
        else:
            print(f"\n❌ Still no contact information found")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alzayat_profile()