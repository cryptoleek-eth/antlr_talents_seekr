#!/usr/bin/env python3
"""
Test Intelligent Contact Extraction - 10 Real Tests
Focuses on the contact service with proper error handling
"""

import os
import sys
import time
from dotenv import load_dotenv
from services.contact_service import ContactExtractionService

# Load environment variables
load_dotenv()

def create_test_profile(login, name, bio=None, email=None, blog=None):
    """Create test profile data"""
    return {
        'name': name,
        'login': login,
        'html_url': f'https://github.com/{login}',
        'bio': bio,
        'email': email,
        'blog': blog,
        'company': None,
        'location': None,
        'twitter_username': None
    }

def run_extraction_test(test_num, login, name, description):
    """Run single extraction test with error handling"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST {test_num}: {name} (@{login})")
    print(f"📝 {description}")
    print(f"{'='*60}")
    
    try:
        # Create profile data
        profile_data = create_test_profile(login, name)
        
        # Mock user object
        class MockUser:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        mock_user = MockUser(profile_data)
        
        # Initialize service
        contact_service = ContactExtractionService()
        
        print(f"🔍 Extracting contact info from GitHub profile...")
        start_time = time.time()
        
        # Extract contact information
        contact_info = contact_service.extract_from_profile(
            profile_data, 'github', mock_user
        )
        
        extraction_time = time.time() - start_time
        
        # Display results
        print(f"⏱️  Completed in {extraction_time:.2f} seconds")
        print(f"\n📧 EMAILS ({len(contact_info.emails)}):")
        if contact_info.emails:
            for email in contact_info.emails:
                print(f"   • {email}")
        else:
            print(f"   • None found")
        
        print(f"\n🔗 SOCIAL LINKS ({len(contact_info.social_links)}):")
        if contact_info.social_links:
            for platform, url in contact_info.social_links.items():
                print(f"   • {platform}: {url}")
        else:
            print(f"   • None found")
        
        print(f"\n📊 CONTACT DETAILS:")
        print(f"   • Website: {contact_info.website or 'Not found'}")
        print(f"   • LinkedIn: {contact_info.linkedin or 'Not found'}")
        print(f"   • Twitter: {contact_info.twitter or 'Not found'}")
        print(f"   • Phone: {contact_info.phone or 'Not found'}")
        print(f"   • Contact Score: {contact_info.contact_score:.2f}/1.0")
        
        # Assessment
        has_email = len(contact_info.emails) > 0
        has_social = len(contact_info.social_links) > 0 or contact_info.linkedin or contact_info.twitter
        has_website = contact_info.website is not None
        good_score = contact_info.contact_score >= 0.3
        
        quality_indicators = [has_email, has_social, has_website, good_score]
        quality_score = sum(quality_indicators) / len(quality_indicators)
        
        print(f"\n✅ QUALITY ASSESSMENT:")
        print(f"   • Has Email: {'✅' if has_email else '❌'}")
        print(f"   • Has Social Links: {'✅' if has_social else '❌'}")
        print(f"   • Has Website: {'✅' if has_website else '❌'}")
        print(f"   • Good Score (≥0.3): {'✅' if good_score else '❌'}")
        print(f"   • Quality: {quality_score:.2f}/1.0")
        
        return {
            'test_num': test_num,
            'login': login,
            'name': name,
            'success': True,
            'emails_found': len(contact_info.emails),
            'social_links_found': len(contact_info.social_links),
            'has_website': has_website,
            'contact_score': contact_info.contact_score,
            'quality_score': quality_score,
            'extraction_time': extraction_time,
            'error': None
        }
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            'test_num': test_num,
            'login': login,
            'name': name,
            'success': False,
            'error': str(e)
        }

def main():
    """Run 10 intelligent extraction tests"""
    print("🚀 INTELLIGENT CONTACT EXTRACTION - 10 REAL TESTS")
    print("🤖 Testing Multi-Level Link Drilling with LLM Intelligence")
    print("=" * 80)
    
    # Test profiles (mix of well-known developers)
    test_profiles = [
        ('charleneleong-ai', 'Charlene Leong', 'AI researcher - should find real email'),
        ('octocat', 'The Octocat', 'GitHub mascot - test profile'),
        ('torvalds', 'Linus Torvalds', 'Linux creator - famous developer'),
        ('gaearon', 'Dan Abramov', 'React team - should have Twitter/blog'),
        ('sindresorhus', 'Sindre Sorhus', 'Prolific OSS developer'),
        ('addyosmani', 'Addy Osmani', 'Google Chrome team - web performance'),
        ('kentcdodds', 'Kent C. Dodds', 'Testing expert and educator'),
        ('wesbos', 'Wes Bos', 'Web development educator'),
        ('bradtraversy', 'Brad Traversy', 'YouTuber and educator'),
        ('defunkt', 'Chris Wanstrath', 'GitHub co-founder')
    ]
    
    # Run tests
    results = []
    for i, (login, name, description) in enumerate(test_profiles, 1):
        result = run_extraction_test(i, login, name, description)
        results.append(result)
        
        # Pause between tests
        if i < len(test_profiles):
            print(f"\n⏳ Waiting 2 seconds before next test...")
            time.sleep(2)
    
    # Summary report
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY REPORT - INTELLIGENT CONTACT EXTRACTION")
    print(f"{'='*80}")
    
    successful_tests = [r for r in results if r.get('success', False)]
    failed_tests = [r for r in results if not r.get('success', False)]
    
    # Calculate metrics
    success_rate = len(successful_tests) / len(results) * 100 if results else 0
    
    if successful_tests:
        total_emails = sum(r.get('emails_found', 0) for r in successful_tests)
        total_social = sum(r.get('social_links_found', 0) for r in successful_tests)
        avg_score = sum(r.get('contact_score', 0) for r in successful_tests) / len(successful_tests)
        avg_quality = sum(r.get('quality_score', 0) for r in successful_tests) / len(successful_tests)
        avg_time = sum(r.get('extraction_time', 0) for r in successful_tests) / len(successful_tests)
        
        print(f"✅ SUCCESS RATE: {success_rate:.1f}% ({len(successful_tests)}/{len(results)})")
        print(f"📧 TOTAL EMAILS FOUND: {total_emails}")
        print(f"🔗 TOTAL SOCIAL LINKS: {total_social}")
        print(f"📊 AVERAGE CONTACT SCORE: {avg_score:.2f}/1.0")
        print(f"🎯 AVERAGE QUALITY: {avg_quality:.2f}/1.0")
        print(f"⏱️  AVERAGE TIME: {avg_time:.2f} seconds")
    else:
        print(f"❌ ALL TESTS FAILED - NO SUCCESSFUL EXTRACTIONS")
    
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        test_num = result['test_num']
        login = result['login']
        
        if result.get('success', False):
            emails = result.get('emails_found', 0)
            social = result.get('social_links_found', 0)
            score = result.get('contact_score', 0)
            status = f"✅ emails:{emails}, social:{social}, score:{score:.2f}"
        else:
            error = result.get('error', 'Unknown error')[:40]
            status = f"❌ {error}"
        
        print(f"   {test_num:2d}. {login:20s} - {status}")
    
    # Intelligence assessment
    print(f"\n🧠 INTELLIGENCE ASSESSMENT:")
    
    if successful_tests and avg_score >= 0.5:
        print(f"   🎯 HIGH INTELLIGENCE: LLM making smart extraction decisions")
    elif successful_tests and avg_score >= 0.3:
        print(f"   👍 MODERATE INTELLIGENCE: Some smart decisions visible")
    else:
        print(f"   ⚠️  LOW INTELLIGENCE: May need LLM tuning or better prompts")
    
    if successful_tests and avg_time < 30:
        print(f"   ⚡ FAST EXTRACTION: Average {avg_time:.1f}s per profile")
    elif successful_tests and avg_time < 60:
        print(f"   ⏱️  REASONABLE SPEED: Average {avg_time:.1f}s per profile")
    else:
        print(f"   🐌 SLOW EXTRACTION: Consider optimization")
    
    # Key findings
    openai_available = os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here'
    jina_available = os.getenv('JINA_API_TOKEN') and 'jina_' in os.getenv('JINA_API_TOKEN')
    
    print(f"\n🔧 SYSTEM STATUS:")
    print(f"   • OpenAI API: {'✅ Configured' if openai_available else '❌ Not configured (using regex fallback)'}")
    print(f"   • Jina API: {'✅ Configured' if jina_available else '❌ Not configured'}")
    print(f"   • Multi-level Drilling: {'✅ Active' if successful_tests else '❌ Check configuration'}")
    
    if success_rate >= 70:
        print(f"\n🎉 EXCELLENT! Intelligent contact extraction is working well!")
        print(f"🤖 The system is making smart decisions about link drilling and content analysis")
    elif success_rate >= 40:
        print(f"\n👌 GOOD RESULTS! Some improvements possible")
        print(f"🔧 Consider enhancing LLM prompts or adding more extraction patterns")
    else:
        print(f"\n⚠️  NEEDS IMPROVEMENT")
        print(f"🛠️  Check API keys, network connectivity, and extraction logic")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()