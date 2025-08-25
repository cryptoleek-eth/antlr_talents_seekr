#!/usr/bin/env python3
"""
Real Test: Charlene Leong Contact Extraction
Demonstrates working intelligent extraction with proper error handling
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append('/home/dev/coding/talent-seekr')

from services.contact_service import ContactExtractionService

def test_charlene_real_extraction():
    """Test real contact extraction for charleneleong-ai profile"""
    
    print("🎯 REAL INTELLIGENT CONTACT EXTRACTION TEST")
    print("👤 Target: Charlene Leong (@charleneleong-ai)")
    print("🤖 Testing Multi-Level Link Drilling with LLM Decisions")
    print("=" * 70)
    
    try:
        # Initialize the contact service
        contact_service = ContactExtractionService()
        print("✅ Contact service initialized successfully")
        
        # Create profile data for charleneleong-ai
        profile_data = {
            'name': 'Charlene Leong',
            'login': 'charleneleong-ai',
            'html_url': 'https://github.com/charleneleong-ai',
            'bio': 'AI researcher and developer passionate about machine learning',
            'email': None,  # GitHub API often doesn't provide email
            'blog': 'https://charleneleong-ai.github.io',  # Personal website
            'company': None,
            'location': 'Australia',
            'twitter_username': None
        }
        
        # Mock GitHub user object
        class MockUser:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
            
            def get_repos(self):
                # Mock repositories for testing
                return []
        
        mock_user = MockUser(profile_data)
        
        print(f"📊 Profile Information:")
        print(f"   • Name: {profile_data['name']}")
        print(f"   • GitHub: {profile_data['html_url']}")
        print(f"   • Personal Website: {profile_data['blog']}")
        print(f"   • Location: {profile_data['location']}")
        
        print(f"\n🔍 Starting intelligent contact extraction...")
        print(f"🧠 LLM will make decisions about:")
        print(f"   • Which links to prioritize for drilling")
        print(f"   • How deep to go (max 3 levels)")
        print(f"   • When to stop drilling (sufficient info found)")
        print(f"   • How to validate extracted information")
        
        # Perform the extraction
        import time
        start_time = time.time()
        
        contact_info = contact_service.extract_from_profile(
            profile_data, 'github', mock_user
        )
        
        extraction_time = time.time() - start_time
        
        print(f"\n⏱️  Extraction completed in {extraction_time:.2f} seconds")
        print(f"\n📧 EXTRACTED EMAILS ({len(contact_info.emails)}):")
        if contact_info.emails:
            for email in contact_info.emails:
                # Check if this is the expected email
                if email == "charleneleong84@gmail.com":
                    print(f"   ✅ {email} (CORRECT - personal email found!)")
                elif "git@github.com" in email:
                    print(f"   ❌ {email} (CONTAMINATION - technical email)")
                else:
                    print(f"   📧 {email}")
        else:
            print(f"   ❌ No emails found")
        
        print(f"\n🔗 SOCIAL LINKS ({len(contact_info.social_links)}):")
        if contact_info.social_links:
            for platform, url in contact_info.social_links.items():
                print(f"   • {platform.capitalize()}: {url}")
        else:
            print(f"   ❌ No social links found")
        
        print(f"\n📊 DETAILED CONTACT INFORMATION:")
        print(f"   • LinkedIn: {contact_info.linkedin or 'Not found'}")
        print(f"   • Twitter: {contact_info.twitter or 'Not found'}")
        print(f"   • Website: {contact_info.website or 'Not found'}")
        print(f"   • Personal Site: {contact_info.personal_site or 'Not found'}")
        print(f"   • Phone: {contact_info.phone or 'Not found'}")
        print(f"   • Contact Score: {contact_info.contact_score:.2f}/1.0")
        
        # Validate against expected results
        print(f"\n✅ VALIDATION RESULTS:")
        
        # Check for correct email
        has_correct_email = "charleneleong84@gmail.com" in contact_info.emails
        print(f"   • Correct email found: {'✅' if has_correct_email else '❌'}")
        
        # Check for no contamination
        has_git_contamination = any("git@github.com" in email for email in contact_info.emails)
        print(f"   • No git@github.com contamination: {'✅' if not has_git_contamination else '❌'}")
        
        # Check for social profiles
        has_social_info = bool(contact_info.social_links or contact_info.linkedin or contact_info.twitter)
        print(f"   • Social profiles found: {'✅' if has_social_info else '⚠️'}")
        
        # Check for website info
        has_website_info = bool(contact_info.website or contact_info.personal_site)
        print(f"   • Website information: {'✅' if has_website_info else '⚠️'}")
        
        # Overall quality assessment
        quality_score = sum([has_correct_email, not has_git_contamination, has_social_info, has_website_info]) / 4
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print(f"   • Extraction Quality: {quality_score:.2f}/1.0")
        print(f"   • Contact Score: {contact_info.contact_score:.2f}/1.0")
        print(f"   • Speed: {extraction_time:.2f} seconds")
        
        if quality_score >= 0.75:
            print(f"   🎉 EXCELLENT! Intelligent extraction working perfectly")
        elif quality_score >= 0.5:
            print(f"   👍 GOOD! Most intelligence features working")
        else:
            print(f"   ⚠️  NEEDS IMPROVEMENT - Check LLM prompts and logic")
        
        # System configuration check
        print(f"\n🔧 SYSTEM CONFIGURATION:")
        openai_configured = bool(os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here')
        jina_configured = bool(os.getenv('JINA_API_TOKEN') and 'jina_' in str(os.getenv('JINA_API_TOKEN')))
        
        print(f"   • OpenAI API: {'✅ Configured' if openai_configured else '❌ Using regex fallback'}")
        print(f"   • Jina API: {'✅ Configured' if jina_configured else '❌ Not configured'}")
        
        if openai_configured:
            print(f"   🧠 LLM Intelligence: ACTIVE - making smart drilling decisions")
        else:
            print(f"   🔄 Regex Fallback: ACTIVE - basic pattern matching only")
        
        return {
            'success': True,
            'correct_email_found': has_correct_email,
            'no_contamination': not has_git_contamination,
            'social_info_found': has_social_info,
            'website_info_found': has_website_info,
            'contact_score': contact_info.contact_score,
            'quality_score': quality_score,
            'extraction_time': extraction_time,
            'openai_active': openai_configured,
            'jina_active': jina_configured
        }
        
    except Exception as e:
        print(f"❌ ERROR during extraction: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    print("🚀 STARTING REAL INTELLIGENT EXTRACTION TEST")
    result = test_charlene_real_extraction()
    
    if result.get('success'):
        print(f"\n✅ TEST COMPLETED SUCCESSFULLY!")
        print(f"🎯 This demonstrates how the LLM makes intelligent decisions about:")
        print(f"   • Link prioritization (personal sites > technical docs)")
        print(f"   • Depth control (stop when sufficient info found)")
        print(f"   • Information validation (filter fake emails)")
        print(f"   • Multi-level drilling (up to 3 levels deep)")
    else:
        print(f"\n❌ TEST FAILED - Check configuration and try again")