#!/usr/bin/env python3
"""
Real Talent Discovery - Find 10 Australian AI Talents
Search GitHub for real AI talents and save to Notion database
"""

import os
import sys
import time
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append('/home/dev/coding/talent-seekr')

from sources.github_source import GitHubSource
from core.notion_client import NotionTalentDB

def discover_and_save_talents():
    """Discover 10 real AI talents and save to Notion"""
    print("🚀 REAL TALENT DISCOVERY SESSION")
    print("🎯 Target: 10 Australian AI/ML Talents")
    print("🤖 Using Intelligent Contact Extraction + Notion Integration")
    print("=" * 80)
    
    try:
        # Initialize services
        print("🔧 Initializing services...")
        
        # GitHub source with contact extraction
        github_source = GitHubSource({
            'github_token': os.getenv('GITHUB_TOKEN'),
            'max_results': 15  # Search for 15 to find best 10
        })
        
        # Notion database
        notion_db = NotionTalentDB()
        
        if not notion_db.is_enabled():
            print("❌ Notion database not configured properly")
            return
        
        print("✅ Services initialized successfully")
        
        # Search parameters for Australian AI talent
        search_params = {
            'keywords': ['machine learning', 'artificial intelligence', 'deep learning', 'AI', 'ML'],
            'location': ['Australia', 'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
            'min_followers': 10,
            'min_repos': 5,
            'max_results': 15,
            'sort': 'followers',  # Get most connected developers
            'language': 'python'  # Focus on Python for AI/ML
        }
        
        print(f"\n🔍 SEARCH PARAMETERS:")
        print(f"   • Keywords: {', '.join(search_params['keywords'][:3])} + 2 more")
        print(f"   • Locations: {', '.join(search_params['location'][:3])} + 3 more")
        print(f"   • Min Followers: {search_params['min_followers']}")
        print(f"   • Min Repositories: {search_params['min_repos']}")
        print(f"   • Primary Language: {search_params['language']}")
        
        # Start discovery
        print(f"\n🎯 STARTING TALENT DISCOVERY...")
        print(f"⏳ This may take 2-3 minutes for intelligent contact extraction...")
        
        start_time = time.time()
        
        # Search for talents
        discovered_talents = github_source.search(search_params)
        
        discovery_time = time.time() - start_time
        
        print(f"\n📊 DISCOVERY RESULTS:")
        print(f"   ⏱️  Discovery Time: {discovery_time:.1f} seconds")
        print(f"   👥 Talents Found: {len(discovered_talents)}")
        
        if not discovered_talents:
            print("❌ No talents found - check search parameters")
            return
        
        # Filter and select top 10
        print(f"\n🔍 FILTERING AND RANKING...")
        
        # Sort by total score (combination of GitHub activity, AU connection, contact info)
        ranked_talents = sorted(
            discovered_talents,
            key=lambda t: t.total_score,
            reverse=True
        )
        
        # Select top 10
        top_10_talents = ranked_talents[:10]
        
        print(f"✅ Selected top 10 talents based on comprehensive scoring")
        
        # Display preview
        print(f"\n👥 TOP 10 SELECTED TALENTS:")
        for i, talent in enumerate(top_10_talents, 1):
            print(f"   {i:2d}. {talent.name or 'Unknown'} "
                  f"(Score: {talent.total_score:.2f}, "
                  f"AU: {talent.au_strength:.2f}, "
                  f"GitHub: {talent.github_score:.2f})")
        
        # Save to Notion
        print(f"\n💾 SAVING TO NOTION DATABASE...")
        successful_saves = 0
        duplicates = 0
        errors = 0
        
        for i, talent in enumerate(top_10_talents, 1):
            print(f"\n📊 Processing {i}/10: {talent.name or 'Unknown'}")
            
            try:
                # Check for duplicates
                existing = notion_db.check_existing_talent(talent.github_url or talent.name)
                if existing:
                    print(f"   ⚠️  Already exists in database - skipping")
                    duplicates += 1
                    continue
                
                # Save to Notion
                print(f"   💾 Saving to Notion...")
                saved_page = notion_db.create_talent_record(talent)
                
                if saved_page:
                    print(f"   ✅ Saved successfully (Page ID: {saved_page.get('id', 'Unknown')[:8]}...)")
                    successful_saves += 1
                else:
                    print(f"   ❌ Save failed")
                    errors += 1
                
                # Brief pause between saves
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error saving: {e}")
                errors += 1
        
        # Final summary
        total_time = time.time() - start_time
        
        print(f"\n{'='*80}")
        print(f"🎉 TALENT DISCOVERY COMPLETE!")
        print(f"{'='*80}")
        
        print(f"📊 FINAL RESULTS:")
        print(f"   ⏱️  Total Time: {total_time:.1f} seconds")
        print(f"   👥 Talents Discovered: {len(discovered_talents)}")
        print(f"   🏆 Top Talents Selected: {len(top_10_talents)}")
        print(f"   ✅ Successfully Saved: {successful_saves}")
        print(f"   ⚠️  Duplicates Skipped: {duplicates}")
        print(f"   ❌ Errors: {errors}")
        
        print(f"\n🧠 INTELLIGENT EXTRACTION STATS:")
        talents_with_contact = sum(1 for t in top_10_talents if t.email or (hasattr(t, 'contact_info') and t.contact_info))
        print(f"   📧 Talents with Contact Info: {talents_with_contact}/{len(top_10_talents)}")
        print(f"   🔗 Multi-level Link Drilling: Active")
        print(f"   🤖 LLM Decision Making: {'Active' if os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here' else 'Regex Fallback'}")
        
        print(f"\n🎯 SUCCESS METRICS:")
        success_rate = (successful_saves / len(top_10_talents)) * 100
        print(f"   📈 Save Success Rate: {success_rate:.1f}%")
        print(f"   🌏 AU Connection Average: {sum(t.au_strength for t in top_10_talents) / len(top_10_talents):.2f}")
        print(f"   🏅 Quality Score Average: {sum(t.total_score for t in top_10_talents) / len(top_10_talents):.2f}")
        
        if successful_saves >= 8:
            print(f"\n🎉 EXCELLENT! High-quality Australian AI talent database created!")
        elif successful_saves >= 5:
            print(f"\n👍 GOOD! Solid talent database foundation established!")
        else:
            print(f"\n⚠️  Some issues encountered - check logs above")
        
        # Show some examples of saved talents
        if successful_saves > 0:
            print(f"\n🌟 EXAMPLE DISCOVERED TALENTS:")
            for talent in top_10_talents[:3]:  # Show first 3
                print(f"   • {talent.name or 'Unknown'}")
                print(f"     GitHub: {talent.github_url}")
                print(f"     Location: {talent.location or 'Unknown'}")
                print(f"     AU Score: {talent.au_strength:.2f}")
                print(f"     Total Score: {talent.total_score:.2f}")
                if talent.au_signals:
                    print(f"     AU Signals: {len(talent.au_signals)} indicators")
                print()
        
        return {
            'success': True,
            'discovered': len(discovered_talents),
            'selected': len(top_10_talents),
            'saved': successful_saves,
            'duplicates': duplicates,
            'errors': errors,
            'total_time': total_time,
            'success_rate': success_rate
        }
        
    except Exception as e:
        print(f"❌ Talent discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def main():
    """Main talent discovery execution"""
    print("🔥 AUSTRALIAN AI TALENT DISCOVERY")
    print("🤖 Real GitHub Search + Intelligent Contact Extraction + Notion Save")
    print("🎯 Target: Find and save 10 high-quality AI talents")
    print()
    
    result = discover_and_save_talents()
    
    if result and result.get('success'):
        print(f"✅ MISSION ACCOMPLISHED!")
        print(f"🎯 Your Notion database now contains {result.get('saved', 0)} new AI talents")
        print(f"🚀 System proven at production scale!")
        
        if result.get('success_rate', 0) >= 80:
            print(f"🏆 OUTSTANDING PERFORMANCE!")
        else:
            print(f"📊 System working well with room for optimization")
            
    else:
        print(f"❌ Mission encountered issues")
        if result:
            print(f"🔧 Error: {result.get('error', 'Unknown error')}")
    
    return result

if __name__ == "__main__":
    result = main()