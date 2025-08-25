#!/usr/bin/env python3
"""
Test multi-level link drilling with OpenAI intelligence
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

def test_multi_level_drilling():
    """Test multi-level intelligent contact extraction with link drilling"""
    print("🕳️ Testing Multi-Level Link Drilling")
    print("=" * 50)
    
    # Check if OpenAI API key is configured
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("❌ OPENAI_API_KEY not configured")
        print("💡 Please set your OpenAI API key in .env file for multi-level drilling")
        print("🔄 Testing without OpenAI (basic extraction only)...")
        use_openai = False
    else:
        print(f"✅ OpenAI API key configured - MULTI-LEVEL DRILLING ENABLED")
        use_openai = True
    
    try:
        # Initialize GitHub and contact extraction service
        token = os.getenv('GITHUB_TOKEN')
        github = Github(token)
        contact_service = ContactExtractionService()
        
        # Test with a few different profiles
        test_users = ["alzayats", "charleneleong-ai"]
        
        for username in test_users:
            print(f"\n🔍 Testing multi-level drilling for: {username}")
            print("-" * 60)
            
            user = github.get_user(username)
            print(f"👤 User: {user.name or user.login}")
            print(f"🌐 Website: {user.blog}")
            
            if use_openai:
                print(f"\n🧠 Running OpenAI multi-level extraction (up to 3 levels deep)...")
            else:
                print(f"\n🔄 Running basic extraction (no drilling)...")
            
            profile_data = {
                'email': user.email,
                'website': user.blog,
                'bio': user.bio,
                'github_url': user.html_url,
                'login': user.login
            }
            contact_info = contact_service.extract_from_profile(profile_data, 'github', user)
            
            print(f"\n📞 Multi-Level Extraction Results:")
            print("-" * 40)
            print(f"✉️  Emails: {list(contact_info.emails)}")
            print(f"💼 LinkedIn: {contact_info.linkedin}")
            print(f"🐦 Twitter: {contact_info.twitter}")
            print(f"🌐 Personal Site: {contact_info.personal_site}")
            print(f"🔗 Website: {contact_info.website}")
            print(f"📱 Phone: {contact_info.phone}")
            print(f"📊 Contact Score: {contact_info.contact_score:.2f} ({contact_info.contact_score*100:.0f}%)")
            print(f"🔗 All Social: {contact_info.social_links}")
            
            # Quality assessment
            email_count = len(contact_info.emails)
            social_count = len(contact_info.social_links)
            
            print(f"\n🎯 Quality Assessment:")
            print(f"   📧 Emails found: {email_count}")
            print(f"   🔗 Social profiles: {social_count}")
            print(f"   📊 Overall score: {contact_info.contact_score:.0%}")
            
            if use_openai and (email_count > 0 or social_count > 2):
                print(f"   ✅ EXCELLENT: Multi-level drilling successful!")
            elif email_count > 0 or social_count > 1:
                print(f"   ✅ GOOD: Basic extraction successful")
            else:
                print(f"   ⚠️  LIMITED: Minimal contact info found")
            
            print("\n" + "="*60)
        
        print(f"\n🎉 Multi-Level Drilling Test Complete!")
        
        if use_openai:
            print(f"🧠 OpenAI ENABLED: Should see multi-level link analysis in debug logs")
            print(f"🔍 Look for 'Level 0:', 'Level 1:', 'Level 2:' messages")
            print(f"🔗 Should see 'Drilling X priority links' messages")
        else:
            print(f"🔄 OpenAI DISABLED: Using regex fallback only")
            print(f"💡 Set OPENAI_API_KEY to enable intelligent multi-level drilling")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multi_level_drilling()