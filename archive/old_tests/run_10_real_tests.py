#!/usr/bin/env python3
"""
Run 10 Real Contact Extraction Tests
Test the intelligent LLM-driven contact extraction with multi-level drilling
"""

import os
import sys
import time
from dotenv import load_dotenv
from services.contact_service import ContactExtractionService

# Load environment variables
load_dotenv()

def create_mock_user(login, name, bio=None, email=None, blog=None, company=None, location=None, twitter=None):
    """Create mock GitHub user for testing"""
    class MockUser:
        def __init__(self):
            self.login = login
            self.name = name
            self.html_url = f"https://github.com/{login}"
            self.bio = bio
            self.email = email
            self.blog = blog
            self.company = company
            self.location = location
            self.twitter_username = twitter
            
        def get_repos(self):
            # Mock method - in real implementation this would return repositories
            return []
    
    return MockUser()

def run_contact_extraction_test(test_num, user_login, user_name, description, expected_features):
    """Run a single contact extraction test"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST {test_num}: {user_name} (@{user_login})")
    print(f"📝 Description: {description}")
    print(f"🎯 Expected: {expected_features}")
    print(f"{'='*80}")
    
    # Create mock user
    mock_user = create_mock_user(user_login, user_name)
    profile_data = {
        'name': user_name,
        'login': user_login,
        'html_url': f'https://github.com/{user_login}',
        'bio': mock_user.bio,
        'email': mock_user.email,
        'blog': mock_user.blog,
        'company': mock_user.company,
        'location': mock_user.location,
        'twitter_username': mock_user.twitter_username
    }
    
    # Initialize contact service
    contact_service = ContactExtractionService()
    
    try:
        print(f"🔍 Starting intelligent contact extraction...")
        start_time = time.time()
        
        # Extract contact information
        contact_info = contact_service.extract_from_profile(
            profile_data, 'github', mock_user
        )
        
        extraction_time = time.time() - start_time
        
        # Display results
        print(f"⏱️  Extraction completed in {extraction_time:.2f} seconds")
        print(f"\n📧 EMAILS FOUND ({len(contact_info.emails)}):")
        for email in contact_info.emails:
            print(f"   • {email}")
        
        print(f"\n🔗 SOCIAL PROFILES FOUND ({len(contact_info.social_profiles)}):")
        for platform, profile in contact_info.social_profiles.items():
            print(f"   • {platform.capitalize()}: {profile}")
        
        print(f"\n📊 CONTACT DETAILS:")
        print(f"   • Website: {contact_info.website or 'Not found'}")
        print(f"   • Phone: {contact_info.phone or 'Not found'}")
        print(f"   • Location: {contact_info.location or 'Not found'}")
        print(f"   • Contact Score: {contact_info.contact_score:.2f}/1.0")
        
        # Quality assessment
        has_email = len(contact_info.emails) > 0
        has_social = len(contact_info.social_profiles) > 0
        good_score = contact_info.contact_score >= 0.5
        
        quality_score = sum([has_email, has_social, good_score]) / 3
        
        print(f"\n✅ TEST QUALITY ASSESSMENT:")
        print(f"   • Has Email: {'✅' if has_email else '❌'}")
        print(f"   • Has Social Profiles: {'✅' if has_social else '❌'}")
        print(f"   • Good Contact Score (≥0.5): {'✅' if good_score else '❌'}")
        print(f"   • Overall Test Quality: {quality_score:.2f}/1.0")
        
        return {
            'test_num': test_num,
            'user_login': user_login,
            'user_name': user_name,
            'emails_found': len(contact_info.emails),
            'social_profiles_found': len(contact_info.social_profiles),
            'contact_score': contact_info.contact_score,
            'extraction_time': extraction_time,
            'has_email': has_email,
            'has_social': has_social,
            'quality_score': quality_score,
            'success': quality_score >= 0.33  # At least 1 out of 3 criteria
        }
        
    except Exception as e:
        print(f"❌ ERROR during extraction: {e}")
        import traceback
        traceback.print_exc()
        return {
            'test_num': test_num,
            'user_login': user_login,
            'user_name': user_name,
            'error': str(e),
            'success': False
        }

def main():
    """Run 10 comprehensive contact extraction tests"""
    print("🚀 STARTING 10 REAL CONTACT EXTRACTION TESTS")
    print("🤖 Testing Intelligent LLM-Driven Multi-Level Link Drilling")
    print("=" * 80)
    
    # Test cases - diverse set of real GitHub profiles
    test_cases = [
        {
            'login': 'charleneleong-ai',
            'name': 'Charlene Leong',
            'description': 'AI researcher - should find charleneleong84@gmail.com',
            'expected': 'Personal email, LinkedIn, possibly Twitter'
        },
        {
            'login': 'octocat',
            'name': 'The Octocat',
            'description': 'GitHub mascot - famous profile for testing',
            'expected': 'Social profiles, possibly website'
        },
        {
            'login': 'torvalds',
            'name': 'Linus Torvalds',
            'description': 'Linux creator - high-profile developer',
            'expected': 'Email, website, social profiles'
        },
        {
            'login': 'gaearon',
            'name': 'Dan Abramov',
            'description': 'React core team - active developer',
            'expected': 'Email, Twitter, website, blog'
        },
        {
            'login': 'sindresorhus',
            'name': 'Sindre Sorhus',
            'description': 'Prolific open source developer',
            'expected': 'Website, social profiles, contact info'
        },
        {
            'login': 'addyosmani',
            'name': 'Addy Osmani',
            'description': 'Google Chrome team - performance expert',
            'expected': 'Website, Twitter, professional profiles'
        },
        {
            'login': 'kentcdodds',
            'name': 'Kent C. Dodds',
            'description': 'Testing and React educator',
            'expected': 'Website, email, social media, courses'
        },
        {
            'login': 'wesbos',
            'name': 'Wes Bos',
            'description': 'Web development educator',
            'expected': 'Website, courses, social media'
        },
        {
            'login': 'bradtraversy',
            'name': 'Brad Traversy',
            'description': 'Developer educator and YouTuber',
            'expected': 'Website, YouTube, social media'
        },
        {
            'login': 'defunkt',
            'name': 'Chris Wanstrath',
            'description': 'GitHub co-founder',
            'expected': 'Professional contact info, social profiles'
        }
    ]
    
    # Run all tests
    results = []
    for i, test_case in enumerate(test_cases, 1):
        result = run_contact_extraction_test(
            i, 
            test_case['login'], 
            test_case['name'],
            test_case['description'],
            test_case['expected']
        )
        results.append(result)
        
        # Brief pause between tests
        if i < len(test_cases):
            print(f"\n⏳ Waiting 2 seconds before next test...")
            time.sleep(2)
    
    # Summary report
    print(f"\n{'='*80}")
    print(f"📊 FINAL TEST SUMMARY REPORT")
    print(f"{'='*80}")
    
    successful_tests = [r for r in results if r.get('success', False)]
    failed_tests = [r for r in results if not r.get('success', False)]
    
    total_emails = sum(r.get('emails_found', 0) for r in results if 'emails_found' in r)
    total_social = sum(r.get('social_profiles_found', 0) for r in results if 'social_profiles_found' in r)
    avg_score = sum(r.get('contact_score', 0) for r in results if 'contact_score' in r) / len([r for r in results if 'contact_score' in r])
    avg_time = sum(r.get('extraction_time', 0) for r in results if 'extraction_time' in r) / len([r for r in results if 'extraction_time' in r])
    
    print(f"✅ SUCCESSFUL TESTS: {len(successful_tests)}/{len(test_cases)} ({len(successful_tests)/len(test_cases)*100:.1f}%)")
    print(f"❌ FAILED TESTS: {len(failed_tests)}")
    print(f"📧 TOTAL EMAILS FOUND: {total_emails}")
    print(f"🔗 TOTAL SOCIAL PROFILES: {total_social}")
    print(f"📊 AVERAGE CONTACT SCORE: {avg_score:.2f}/1.0")
    print(f"⏱️  AVERAGE EXTRACTION TIME: {avg_time:.2f} seconds")
    
    print(f"\n🎯 INDIVIDUAL TEST RESULTS:")
    for result in results:
        if result.get('success', False):
            status = "✅ PASS"
            details = f"emails: {result.get('emails_found', 0)}, social: {result.get('social_profiles_found', 0)}, score: {result.get('contact_score', 0):.2f}"
        else:
            status = "❌ FAIL"
            details = result.get('error', 'Unknown error')[:50] + "..." if len(result.get('error', '')) > 50 else result.get('error', 'Unknown error')
        
        print(f"   {result['test_num']:2d}. {result['user_login']:20s} - {status} ({details})")
    
    # Performance insights
    print(f"\n🚀 PERFORMANCE INSIGHTS:")
    if avg_time < 30:
        print(f"   ⚡ Excellent speed: Average {avg_time:.1f}s per extraction")
    elif avg_time < 60:
        print(f"   ⏱️  Good speed: Average {avg_time:.1f}s per extraction")
    else:
        print(f"   🐌 Slow extraction: Average {avg_time:.1f}s per extraction")
    
    if avg_score >= 0.7:
        print(f"   🎯 High quality: Average score {avg_score:.2f}")
    elif avg_score >= 0.5:
        print(f"   👍 Good quality: Average score {avg_score:.2f}")
    else:
        print(f"   ⚠️  Low quality: Average score {avg_score:.2f}")
    
    success_rate = len(successful_tests) / len(test_cases) * 100
    if success_rate >= 80:
        print(f"   🏆 Excellent success rate: {success_rate:.1f}%")
    elif success_rate >= 60:
        print(f"   👌 Good success rate: {success_rate:.1f}%")
    else:
        print(f"   ❌ Poor success rate: {success_rate:.1f}%")
    
    print(f"\n{'='*80}")
    if success_rate >= 70:
        print(f"🎉 INTELLIGENT CONTACT EXTRACTION SYSTEM IS WORKING WELL!")
        print(f"🤖 LLM is making smart decisions about link drilling and content extraction")
    else:
        print(f"⚠️  SYSTEM NEEDS IMPROVEMENT")
        print(f"🔧 Consider tuning the LLM prompts or extraction logic")
    
    return results

if __name__ == "__main__":
    results = main()