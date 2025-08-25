#!/usr/bin/env python3
"""
Verify Notion database setup and integration sharing
"""

import os
import sys
from dotenv import load_dotenv
from notion_client import Client

def main():
    """Check Notion database setup"""
    load_dotenv()
    
    print("🔍 Notion Database Setup Verification")
    print("=" * 40)
    
    # Check environment variables
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    print(f"NOTION_TOKEN: {'✅ Set' if token else '❌ Missing'}")
    print(f"NOTION_DATABASE_ID: {'✅ Set' if database_id else '❌ Missing'}")
    
    if not token or not database_id:
        print("\n❌ Missing required environment variables")
        return False
    
    print(f"\nDatabase ID: {database_id}")
    
    try:
        notion = Client(auth=token)
        
        # Try to access the database
        print("\n📝 Testing database access...")
        response = notion.databases.retrieve(database_id=database_id)
        
        print("✅ SUCCESS! Database accessible")
        print(f"   Database Name: {response['title'][0]['text']['content']}")
        print(f"   Properties: {len(response['properties'])}")
        
        # Check required properties
        required_props = ['Name', 'Talent Score', 'Status', 'AU Connection', 'GitHub Profile']
        existing_props = list(response['properties'].keys())
        
        print(f"\n📊 Required Properties Check:")
        all_good = True
        for prop in required_props:
            if prop in existing_props:
                print(f"   ✅ {prop}")
            else:
                print(f"   ❌ {prop} - Missing!")
                all_good = False
        
        if all_good:
            print(f"\n🎉 Database is ready for talent sync!")
            print(f"You can now run: source .venv/bin/activate && python mvp_demo.py --max-results 20")
        else:
            print(f"\n⚠️  Some required properties are missing in your database")
            
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Database access failed: {error_msg}")
        
        if "Could not find database" in error_msg:
            print(f"\n💡 SOLUTION: Share your database with the integration")
            print(f"   1. Go to your Notion database page")
            print(f"   2. Click '...' menu → 'Add connections'")
            print(f"   3. Search for 'Talent-Seekr' (your integration name)")
            print(f"   4. Click 'Confirm' to grant access")
            print(f"   5. Run this script again to verify")
            
        elif "Unauthorized" in error_msg:
            print(f"\n💡 SOLUTION: Check your integration token")
            print(f"   Your NOTION_TOKEN may be invalid or expired")
            
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 Ready to go!' if success else '🔧 Setup needed'}")
    sys.exit(0 if success else 1)