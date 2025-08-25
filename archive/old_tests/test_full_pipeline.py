#!/usr/bin/env python3
"""
Test the full talent discovery pipeline
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sources.github_source import GitHubSource
from core.notion_client import NotionTalentDB
from utils.deduplication import TalentDeduplicator

def test_full_pipeline():
    """Test the complete talent discovery pipeline"""
    load_dotenv()
    
    print("🧪 Testing Full Talent Discovery Pipeline")
    print("=" * 45)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    start_time = datetime.now()
    
    try:
        # 1. Initialize components
        print("\n1️⃣ Initializing components...")
        github_source = GitHubSource({})
        notion_db = NotionTalentDB()
        deduplicator = TalentDeduplicator()
        
        print(f"   ✅ GitHub plugin initialized")
        print(f"   {'✅' if notion_db.is_enabled() else '⚠️'} Notion {'enabled' if notion_db.is_enabled() else 'disabled'}")
        print(f"   ✅ Deduplicator ready")
        
        # 2. Discover talents
        print("\n2️⃣ Discovering talents on GitHub...")
        query_params = {'max_results': 5}  # Small test batch
        talents = github_source.search(query_params)
        
        print(f"   📊 Found {len(talents)} raw talents")
        
        if not talents:
            print("   ❌ No talents found - check GitHub token")
            return False
        
        # 3. Deduplicate
        print("\n3️⃣ Deduplicating talents...")
        unique_talents = deduplicator.deduplicate_talents(talents)
        print(f"   📊 After dedup: {len(unique_talents)} unique talents")
        
        # 4. Quality filter
        print("\n4️⃣ Applying quality filters...")
        quality_threshold = 35
        qualified_talents = [t for t in unique_talents if t.github_score >= quality_threshold]
        print(f"   📊 Qualified (score ≥{quality_threshold}): {len(qualified_talents)}")
        
        # 5. Display results
        print("\n5️⃣ Top discovered talents:")
        print("-" * 50)
        
        if qualified_talents:
            for i, talent in enumerate(qualified_talents[:3], 1):
                print(f"   {i}. {talent.name}")
                print(f"      Score: {talent.github_score:.1f} | AU: {talent.au_strength:.1f}")
                print(f"      Location: {talent.location}")
                print(f"      GitHub: {talent.github_url}")
                print()
        
        # 6. Test Notion integration
        print("6️⃣ Testing Notion integration...")
        
        if notion_db.is_enabled():
            print("   🚀 Attempting to save to Notion...")
            
            # Test with one talent first
            test_talent = qualified_talents[0] if qualified_talents else None
            if test_talent:
                result = notion_db.create_talent_record(test_talent)
                if result:
                    print(f"   ✅ Successfully saved {test_talent.name} to Notion!")
                    print(f"      Notion page ID: {result['id']}")
                else:
                    print(f"   ❌ Failed to save to Notion")
            
        else:
            print("   ⚠️ Notion not configured - would save these records:")
            for talent in qualified_talents[:3]:
                print(f"      - {talent.name} (score: {talent.github_score:.1f})")
        
        # 7. Performance summary
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n⚡ Pipeline completed in {duration:.1f} seconds")
        
        print(f"\n🎉 Test Results:")
        print(f"   ✅ GitHub discovery: {len(talents)} talents found")
        print(f"   ✅ Deduplication: {len(unique_talents)} unique")
        print(f"   ✅ Quality filter: {len(qualified_talents)} qualified")
        print(f"   {'✅' if notion_db.is_enabled() else '⚠️'} Notion: {'Ready' if notion_db.is_enabled() else 'Needs configuration'}")
        print(f"   ⚡ Performance: {duration:.1f}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_full_pipeline()
    sys.exit(0 if success else 1)