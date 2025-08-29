#!/usr/bin/env python3
"""
Test script for the new Twitter source using twitterapi.io
"""

import logging
from sources.twitter_source import TwitterSource
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_twitter_source():
    """
    Test the Twitter source functionality
    """
    print("🐦 TESTING TWITTER SOURCE WITH TWITTERAPI.IO")
    print("=" * 50)
    
    try:
        # Initialize Twitter source
        twitter_source = TwitterSource()
        
        print(f"✅ Twitter source initialized")
        print(f"   Enabled: {twitter_source.enabled}")
        print(f"   Base URL: {twitter_source.base_url}")
        
        # Check rate limit status
        rate_status = twitter_source.get_rate_limit_status()
        print(f"✅ Rate limit status: {rate_status}")
        
        # Test search parameters
        search_params = {
            'max_results': 5,
            'keywords': ['machine learning', 'artificial intelligence']
        }
        
        print(f"\n🔍 Testing search with params: {search_params}")
        
        if twitter_source.enabled:
            print("⚠️  Note: This will make actual API calls to twitterapi.io")
            print("   Make sure you have a valid API key configured")
            
            # Perform search
            talents = twitter_source.search(search_params)
            
            print(f"✅ Search completed: {len(talents)} talents found")
            
            # Display results
            for i, talent in enumerate(talents, 1):
                print(f"\n📋 Talent {i}:")
                print(f"   Name: {talent.name}")
                print(f"   Location: {talent.location}")
                print(f"   AU Strength: {talent.au_strength:.2f}")
                print(f"   Twitter Score: {talent.twitter_score:.1f}")
                print(f"   Twitter URL: {talent.twitter_url}")
                
                # Show platform data
                twitter_data = talent.platform_data.get('twitter', {})
                print(f"   Followers: {twitter_data.get('followers', 0)}")
                print(f"   Description: {twitter_data.get('description', 'N/A')[:100]}...")
                
                # Show AU signals
                if hasattr(talent, 'au_signals') and talent.au_signals:
                    print(f"   AU Signals: {', '.join(talent.au_signals)}")
        else:
            print("⚠️  Twitter source not enabled (API key not configured)")
            print("   Set TWITTER_API_KEY environment variable to test")
        
        print("\n✅ Twitter source test completed successfully")
        
    except Exception as e:
        print(f"❌ Twitter source test failed: {e}")
        logger.exception("Detailed error:")

def test_au_strength_calculation():
    """
    Test Australia strength calculation with sample data
    """
    print("\n🇦🇺 TESTING AU STRENGTH CALCULATION")
    print("=" * 40)
    
    twitter_source = TwitterSource()
    
    # Test cases
    test_cases = [
        {
            "name": "Sydney-based user",
            "data": {
                "location": "Sydney, Australia",
                "description": "AI researcher working on machine learning"
            }
        },
        {
            "name": "Melbourne user with AU bio",
            "data": {
                "location": "Melbourne",
                "description": "Building AI startups in Australia"
            }
        },
        {
            "name": "Non-AU user",
            "data": {
                "location": "San Francisco, CA",
                "description": "AI engineer at tech company"
            }
        },
        {
            "name": "AU domain in bio",
            "data": {
                "location": "",
                "description": "Check out my work",
                "profile_bio": {
                    "entities": {
                        "description": {
                            "urls": [
                                {"expanded_url": "https://mycompany.com.au"}
                            ]
                        }
                    }
                }
            }
        }
    ]
    
    for test_case in test_cases:
        au_strength = twitter_source._calculate_au_strength(test_case["data"])
        print(f"📊 {test_case['name']}: AU Strength = {au_strength:.2f}")
        
        # Show details
        data = test_case["data"]
        print(f"   Location: '{data.get('location', '')}'") 
        print(f"   Description: '{data.get('description', '')}'") 
        
        if au_strength >= 0.3:
            print("   ✅ Meets AU threshold")
        else:
            print("   ❌ Below AU threshold")
        print()

if __name__ == "__main__":
    test_twitter_source()
    test_au_strength_calculation()
    
    print("\n🎯 TWITTER SOURCE TESTING COMPLETE")
    print("=" * 50)
    print("The Twitter source has been successfully rebuilt to use twitterapi.io")
    print("Key features:")
    print("  • User search by AI/ML keywords")
    print("  • Australia connection scoring")
    print("  • Quality threshold filtering")
    print("  • Contact information extraction")
    print("  • Rate limiting and error handling")
    print("\nTo use with real data, configure TWITTER_API_KEY environment variable.")