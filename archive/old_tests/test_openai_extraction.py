#!/usr/bin/env python3
"""
Test OpenAI intelligent contact extraction
"""

import os
import sys
import logging
from dotenv import load_dotenv
from github import Github

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.contact_service import ContactExtractionService

# Load environment variables
load_dotenv()

# Setup logging to see debug messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_openai_extraction():
    """Test OpenAI-enhanced contact extraction"""
    print("🧠 Testing OpenAI Enhanced Contact Extraction")
    print("=" * 55)
    
    # Check if OpenAI API key is configured
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("❌ OPENAI_API_KEY not configured")
        print("💡 Please set your OpenAI API key in .env file:")
        print("   OPENAI_API_KEY=sk-your-actual-openai-key-here")
        print("\n🔄 Testing without OpenAI (regex fallback only)...")
    else:
        print(f"✅ OpenAI API key configured (ends with ...{openai_key[-8:]})")
    
    try:
        # Initialize GitHub and contact extraction service
        token = os.getenv('GITHUB_TOKEN')
        github = Github(token)
        contact_service = ContactExtractionService()
        
        # Get Alzayat's profile
        print("\n🔍 Fetching Alzayat's GitHub profile...")
        user = github.get_user("alzayats")
        
        print(f"👤 User: {user.name or user.login}")
        print(f"🔗 Profile: {user.html_url}")
        print(f"📝 Bio: {user.bio}")
        print(f"🌐 Website: {user.blog}")
        
        # Test enhanced contact extraction
        print(f"\n🔍 Running enhanced contact extraction...")
        profile_data = {
            'email': user.email,
            'website': user.blog,
            'bio': user.bio,
            'github_url': user.html_url,
            'login': user.login
        }
        contact_info = contact_service.extract_from_profile(profile_data, 'github', user)
        
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
        
        if contact_info.emails:
            print(f"\n✅ SUCCESS: Found email(s): {', '.join(contact_info.emails)}")
        
        if contact_info.contact_score > 0.5:
            print(f"✅ HIGH QUALITY: Contact score above 50%")
        else:
            print(f"⚠️ LOW QUALITY: Contact score below 50%")
            
        if contact_service.openai_client:
            print(f"🧠 OpenAI intelligent extraction: ENABLED")
        else:
            print(f"🔄 OpenAI intelligent extraction: DISABLED (using regex fallback)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openai_extraction()