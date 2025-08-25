#!/usr/bin/env python3
"""
Test Notion database setup
"""

import os
import sys
from dotenv import load_dotenv
from notion_client import Client

def test_notion_database():
    """Test Notion database connection and structure"""
    load_dotenv()
    
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    if not token or not database_id:
        print("❌ Missing NOTION_TOKEN or NOTION_DATABASE_ID in .env")
        return False
    
    print(f"🔍 Testing Notion integration...")
    print(f"   Database ID: {database_id}")
    
    try:
        notion = Client(auth=token)
        
        # Test database access
        print("📝 Attempting to retrieve database...")
        response = notion.databases.retrieve(database_id=database_id)
        
        print("✅ Database found!")
        print(f"   Title: {response['title'][0]['text']['content']}")
        print(f"   Properties: {len(response['properties'])}")
        
        # Check required properties
        required_props = ['Name', 'Talent Score', 'Status', 'AU Connection', 'GitHub Profile']
        existing_props = list(response['properties'].keys())
        
        print(f"\n📊 Property Check:")
        for prop in required_props:
            if prop in existing_props:
                print(f"   ✅ {prop}")
            else:
                print(f"   ❌ {prop} - Missing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database access failed: {e}")
        
        if "Could not find database" in str(e):
            print("\n💡 Fix: Share your Notion database with the integration:")
            print("   1. Go to your Notion database page")
            print("   2. Click '...' → 'Add connections'")
            print("   3. Search for 'Talent-Seekr' (your integration name)")
            print("   4. Click 'Confirm' to grant access")
            
        return False

if __name__ == "__main__":
    test_notion_database()