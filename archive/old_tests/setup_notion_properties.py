#!/usr/bin/env python3
"""
Setup required properties in Notion database
"""

import os
import sys
from dotenv import load_dotenv
from notion_client import Client

def setup_database_properties():
    """Add required properties to the Notion database"""
    load_dotenv()
    
    print("🔧 Setting up Notion Database Properties")
    print("=" * 40)
    
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    if not token or not database_id:
        print("❌ Missing NOTION_TOKEN or NOTION_DATABASE_ID")
        return False
    
    try:
        notion = Client(auth=token)
        
        # Get current database structure
        print("📋 Checking current database structure...")
        response = notion.databases.retrieve(database_id=database_id)
        current_props = response['properties']
        
        print(f"   Current properties: {list(current_props.keys())}")
        
        # Define required properties
        required_properties = {
            "Name": {
                "title": {}
            },
            "Talent Score": {
                "number": {
                    "format": "number"
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "New", "color": "blue"},
                        {"name": "Contacted", "color": "yellow"}, 
                        {"name": "Follow-up", "color": "orange"},
                        {"name": "Potential", "color": "green"},
                        {"name": "Reject", "color": "red"},
                        {"name": "Later", "color": "gray"}
                    ]
                }
            },
            "AU Connection": {
                "number": {
                    "format": "percent"
                }
            },
            "GitHub Profile": {
                "url": {}
            },
            "Recent Activity": {
                "rich_text": {}
            },
            "Discovered Date": {
                "date": {}
            },
            "Source Platforms": {
                "multi_select": {
                    "options": [
                        {"name": "GitHub", "color": "gray"},
                        {"name": "Twitter", "color": "blue"},
                        {"name": "LinkedIn", "color": "blue"}
                    ]
                }
            }
        }
        
        # Update database with required properties
        print("\n🔨 Adding missing properties...")
        
        # Merge existing properties with required ones
        updated_properties = {**current_props, **required_properties}
        
        update_response = notion.databases.update(
            database_id=database_id,
            properties=updated_properties
        )
        
        print("✅ Database properties updated successfully!")
        
        # Verify the update
        print("\n🔍 Verifying updated properties...")
        updated_db = notion.databases.retrieve(database_id=database_id)
        final_props = list(updated_db['properties'].keys())
        
        print(f"   Final properties: {final_props}")
        
        # Check all required properties
        missing = []
        for prop in ["Name", "Talent Score", "Status", "AU Connection", "GitHub Profile"]:
            if prop in final_props:
                print(f"   ✅ {prop}")
            else:
                print(f"   ❌ {prop} - Still missing!")
                missing.append(prop)
        
        if not missing:
            print(f"\n🎉 Database is fully configured!")
            print(f"You can now run the full pipeline:")
            print(f"   source .venv/bin/activate && python mvp_demo.py --max-results 20")
            return True
        else:
            print(f"\n⚠️  Some properties still missing: {missing}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to setup database properties: {e}")
        return False

if __name__ == "__main__":
    success = setup_database_properties()
    sys.exit(0 if success else 1)