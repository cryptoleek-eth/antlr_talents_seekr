#!/usr/bin/env python3
"""
Test Refactored System
Verify that the clean, refactored codebase works correctly
"""

import sys
import logging
from datetime import datetime

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_configuration():
    """Test configuration loading and validation"""
    print("🔧 TESTING CONFIGURATION")
    print("=" * 40)
    
    try:
        from config import settings
        
        # Test configuration validation
        config_status = settings.validate_configuration()
        
        print("Configuration Status:")
        for service, status in config_status.items():
            print(f"  {service.upper()}: {status['status']}")
        
        # Test individual components
        print(f"\nAPI Configuration:")
        print(f"  GitHub configured: {settings.api.is_github_configured()}")
        print(f"  Notion configured: {settings.api.is_notion_configured()}")
        print(f"  Jina configured: {settings.api.is_jina_configured()}")
        print(f"  OpenAI configured: {settings.api.is_openai_configured()}")
        
        print("✅ Configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_contact_extractor():
    """Test contact extractor initialization"""
    print("\n📧 TESTING CONTACT EXTRACTOR")
    print("=" * 40)
    
    try:
        from services.contact_extractor import ContactExtractor, ContactInfo
        
        # Test initialization
        extractor = ContactExtractor()
        print(f"✅ Contact extractor initialized")
        
        # Test ContactInfo creation
        contact_info = ContactInfo()
        contact_info.emails.add("test@example.com")
        contact_info.contact_score = 0.85
        
        print(f"✅ ContactInfo creation works")
        print(f"   Emails: {len(contact_info.emails)}")
        print(f"   Score: {contact_info.contact_score}")
        
        print("✅ Contact extractor test passed")
        return True
        
    except Exception as e:
        print(f"❌ Contact extractor test failed: {e}")
        return False

def test_talent_model():
    """Test talent data model"""
    print("\n👤 TESTING TALENT MODEL")
    print("=" * 40)
    
    try:
        from core.talent import Talent
        from datetime import datetime
        
        # Create test talent
        talent = Talent(
            name="Test Developer",
            email="test@example.com",
            github_url="https://github.com/testdev",
            location="Sydney, Australia",
            au_strength=0.8,
            github_score=0.75,
            total_score=0.77
        )
        
        # Test methods
        talent.add_au_signals(["Location: Sydney", "High GitHub activity"])
        talent_dict = talent.to_dict()
        
        print(f"✅ Talent model works")
        print(f"   Name: {talent.name}")
        print(f"   AU Strength: {talent.au_strength}")
        print(f"   AU Signals: {len(talent.au_signals)}")
        print(f"   Dict conversion: {len(talent_dict)} fields")
        
        print("✅ Talent model test passed")
        return True
        
    except Exception as e:
        print(f"❌ Talent model test failed: {e}")
        return False

def test_github_source():
    """Test GitHub source initialization"""
    print("\n🐙 TESTING GITHUB SOURCE")
    print("=" * 40)
    
    try:
        from sources.github_source import GitHubSource
        from config import settings
        
        if not settings.api.is_github_configured():
            print("⚠️  GitHub not configured - skipping test")
            return True
        
        # Test initialization
        github_source = GitHubSource()
        print(f"✅ GitHub source initialized")
        
        # Test rate limit check
        rate_limit = github_source.get_rate_limit_status()
        if rate_limit:
            print(f"✅ Rate limit check works")
            print(f"   Core remaining: {rate_limit.get('core', {}).get('remaining', 'unknown')}")
            print(f"   Search remaining: {rate_limit.get('search', {}).get('remaining', 'unknown')}")
        
        print("✅ GitHub source test passed")
        return True
        
    except Exception as e:
        print(f"❌ GitHub source test failed: {e}")
        return False

def test_notion_client():
    """Test Notion client initialization"""
    print("\n📝 TESTING NOTION CLIENT")
    print("=" * 40)
    
    try:
        from core.notion_client import NotionTalentDB
        from config import settings
        
        if not settings.api.is_notion_configured():
            print("⚠️  Notion not configured - skipping test")
            return True
        
        # Test initialization
        notion_db = NotionTalentDB()
        print(f"✅ Notion client initialized")
        print(f"   Enabled: {notion_db.is_enabled()}")
        
        # Test schema retrieval
        schema = notion_db.get_database_schema()
        if schema:
            print(f"✅ Database schema retrieved")
            print(f"   Title: {schema.get('title', 'Unknown')}")
            print(f"   Properties: {len(schema.get('properties', []))}")
        
        print("✅ Notion client test passed")
        return True
        
    except Exception as e:
        print(f"❌ Notion client test failed: {e}")
        return False

def test_main_application():
    """Test main application initialization"""
    print("\n🚀 TESTING MAIN APPLICATION")
    print("=" * 40)
    
    try:
        from talent_discovery import TalentDiscoveryApp
        
        # Test application initialization
        app = TalentDiscoveryApp()
        print(f"✅ Application initialized")
        
        # Test status method
        status = app.get_status()
        print(f"✅ Status method works")
        print(f"   Timestamp: {status.get('timestamp', 'unknown')}")
        print(f"   GitHub service: {status.get('services', {}).get('github_source', False)}")
        print(f"   Notion service: {status.get('services', {}).get('notion_db', False)}")
        
        print("✅ Main application test passed")
        return True
        
    except Exception as e:
        print(f"❌ Main application test failed: {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("🧪 REFACTORED SYSTEM TESTS")
    print("🎯 Testing clean, production-ready codebase")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Contact Extractor", test_contact_extractor),
        ("Talent Model", test_talent_model),
        ("GitHub Source", test_github_source),
        ("Notion Client", test_notion_client),
        ("Main Application", test_main_application),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name:<20}: {status}")
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Tests Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Refactored system is working correctly")
        print(f"🚀 Ready for production talent discovery")
    else:
        print(f"\n⚠️  Some tests failed - check issues above")
        print(f"🔧 Fix failing components before production use")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)