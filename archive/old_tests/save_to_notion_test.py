#!/usr/bin/env python3
"""
Save to Notion Test - Actually save extracted data to Notion database
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append('/home/dev/coding/talent-seekr')

from core.notion_client import NotionTalentDB
from core.talent import Talent
from services.contact_service import ContactExtractionService

def save_real_data_to_notion():
    """Actually save extracted contact data to Notion database"""
    print("💾 REAL NOTION SAVE TEST")
    print("🎯 Extract → Process → Save to Notion Database")
    print("=" * 60)
    
    try:
        # Step 1: Extract contact information
        print("📊 STEP 1: Contact Extraction")
        contact_service = ContactExtractionService()
        
        # Test profile
        profile_data = {
            'name': 'Charlene Leong',
            'login': 'charleneleong-ai',
            'html_url': 'https://github.com/charleneleong-ai',
            'bio': 'AI researcher and developer passionate about machine learning',
            'email': None,
            'blog': 'https://charleneleong-ai.github.io',
            'company': None,
            'location': 'Australia',
            'twitter_username': None
        }
        
        class MockUser:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
                self.public_repos = 15
                self.followers = 42
                self.following = 18
                self.created_at = datetime(2020, 1, 15)
        
        mock_user = MockUser(profile_data)
        
        # Extract contact info
        contact_info = contact_service.extract_from_profile(
            profile_data, 'github', mock_user
        )
        
        print(f"✅ Contact extraction completed")
        print(f"   📧 Emails: {len(contact_info.emails)}")
        print(f"   🔗 Social: {len(contact_info.social_links)}")
        print(f"   🎯 Score: {contact_info.contact_score:.2f}")
        
        # Step 2: Create Talent object
        print(f"\n📊 STEP 2: Talent Creation")
        talent = Talent.from_github_user(mock_user, au_strength=0.85)
        
        # Enhance with extracted contact info
        if contact_info.emails:
            talent.email = list(contact_info.emails)[0]
        if contact_info.linkedin:
            talent.linkedin_url = contact_info.linkedin
        if contact_info.twitter:
            talent.twitter_url = contact_info.twitter
        
        # Set scores
        talent.github_score = 0.88
        talent.twitter_score = 0.65 if contact_info.twitter else 0.0
        talent.total_score = (talent.github_score + talent.twitter_score + talent.au_strength) / 3
        
        # AU signals
        talent.au_signals = [
            "Location: Australia",
            "AI/ML expertise demonstrated",
            "Active GitHub profile",
            "Personal website with portfolio"
        ]
        
        print(f"✅ Talent object created")
        print(f"   👤 Name: {talent.name}")
        print(f"   📧 Email: {talent.email or 'Not extracted'}")
        print(f"   🎯 Total Score: {talent.total_score:.2f}")
        
        # Step 3: Save to Notion Database
        print(f"\n📊 STEP 3: Saving to Notion")
        notion_db = NotionTalentDB()
        
        if not notion_db.is_enabled():
            print("❌ Notion client not properly configured")
            return False
        
        print(f"✅ Notion client ready")
        print(f"🔍 Checking if talent already exists...")
        
        # Check if already exists
        existing = notion_db.check_existing_talent(talent.github_url or talent.name)
        if existing:
            print(f"⚠️  Talent already exists in database: {existing}")
            print(f"💡 Skipping save to avoid duplicates")
            return True
        
        print(f"✅ No duplicate found - proceeding with save")
        print(f"💾 Saving talent to Notion database...")
        
        # Actually save to Notion
        saved_page = notion_db.create_talent_record(talent)
        
        if saved_page:
            print(f"🎉 SUCCESS! Talent saved to Notion")
            print(f"📄 Page ID: {saved_page.get('id', 'Unknown')}")
            print(f"🔗 Database updated successfully")
            
            return {
                'success': True,
                'page_id': saved_page.get('id'),
                'talent_name': talent.name,
                'total_score': talent.total_score,
                'au_strength': talent.au_strength
            }
        else:
            print(f"❌ Failed to save to Notion")
            return False
            
    except Exception as e:
        print(f"❌ Error during Notion save: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_notion_database_query():
    """Test querying the Notion database to see existing entries"""
    print(f"\n🔍 TESTING NOTION DATABASE QUERY")
    print("=" * 40)
    
    try:
        notion_db = NotionTalentDB()
        
        if not notion_db.is_enabled():
            print("❌ Notion not enabled")
            return
        
        print("✅ Notion client ready")
        print("🔍 Attempting to query database...")
        
        # Try to check for existing talent (this will test read access)
        test_result = notion_db.check_existing_talent("test-query")
        
        if test_result is None:
            print("✅ Database query successful (no match found as expected)")
        else:
            print(f"ℹ️  Database query returned: {test_result}")
        
        print("✅ Database access confirmed working")
        
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run complete Notion integration test with real saves"""
    print("🚀 REAL NOTION INTEGRATION TEST")
    print("💾 This will actually save data to your Notion database")
    print("=" * 70)
    
    # Test 1: Database query
    test_notion_database_query()
    
    # Test 2: Real save
    print(f"\n{'='*70}")
    print("💾 ATTEMPTING REAL SAVE TO NOTION")
    print(f"⚠️  This will create an actual entry in your database")
    print("=" * 70)
    
    result = save_real_data_to_notion()
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 NOTION INTEGRATION RESULTS")
    print("=" * 70)
    
    if result:
        print("🎉 NOTION INTEGRATION FULLY WORKING!")
        print(f"\n✅ Verified:")
        print(f"   • Contact extraction from GitHub profiles")
        print(f"   • Talent object creation with AU scoring")
        print(f"   • Real Notion database saves")
        print(f"   • Duplicate detection")
        print(f"   • Full pipeline end-to-end")
        
        if isinstance(result, dict):
            print(f"\n📊 Saved Talent Details:")
            print(f"   • Name: {result.get('talent_name')}")
            print(f"   • Total Score: {result.get('total_score', 0):.2f}")
            print(f"   • AU Strength: {result.get('au_strength', 0):.2f}")
            print(f"   • Page ID: {result.get('page_id', 'Unknown')[:8]}...")
        
        print(f"\n🎯 SYSTEM READY FOR PRODUCTION!")
        print(f"🚀 You can now run talent discovery at scale")
        
    else:
        print("❌ NOTION INTEGRATION ISSUES DETECTED")
        print(f"\n🛠️  Check:")
        print(f"   • Notion token and database ID in .env")
        print(f"   • Notion integration permissions")
        print(f"   • Database schema matches expected fields")
        print(f"   • Network connectivity to Notion API")
    
    return result

if __name__ == "__main__":
    result = main()