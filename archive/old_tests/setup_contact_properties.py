#!/usr/bin/env python3
"""
Add contact-related properties to Notion database
"""

import os
import sys
from dotenv import load_dotenv
from notion_client import Client

def setup_contact_properties():
    """Add contact-related properties to the Notion database"""
    load_dotenv()
    
    print("🔧 Setting up Contact Properties in Notion Database")
    print("=" * 50)
    
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
        current_properties = response['properties']
        
        print(f"📊 Current properties: {list(current_properties.keys())}")
        
        # Define new contact properties
        contact_properties = {
            "Email": {
                "type": "email",
                "email": {}
            },
            "Contact Score": {
                "type": "number",
                "number": {
                    "format": "percent"
                }
            },
            "LinkedIn": {
                "type": "url",
                "url": {}
            },
            "Twitter": {
                "type": "url",
                "url": {}
            },
            "Personal Website": {
                "type": "url",
                "url": {}
            },
            "Phone": {
                "type": "phone_number",
                "phone_number": {}
            },
            "Contact Methods": {
                "type": "rich_text",
                "rich_text": {}
            },
            "Outreach Status": {
                "type": "select",
                "select": {
                    "options": [
                        {
                            "name": "Not Contacted",
                            "color": "gray"
                        },
                        {
                            "name": "Email Sent",
                            "color": "blue"
                        },
                        {
                            "name": "LinkedIn Message Sent",
                            "color": "purple"
                        },
                        {
                            "name": "Responded",
                            "color": "green"
                        },
                        {
                            "name": "Not Interested",
                            "color": "red"
                        },
                        {
                            "name": "Follow Up",
                            "color": "orange"
                        }
                    ]
                }
            },
            "Last Contact Date": {
                "type": "date",
                "date": {}
            }
        }
        
        # Add properties that don't exist
        properties_to_add = {}
        for prop_name, prop_config in contact_properties.items():
            if prop_name not in current_properties:
                properties_to_add[prop_name] = prop_config
                print(f"✅ Will add: {prop_name}")
            else:
                print(f"⏭️  Already exists: {prop_name}")
        
        if properties_to_add:
            print(f"\n🔄 Adding {len(properties_to_add)} new properties...")
            
            # Update database with new properties
            notion.databases.update(
                database_id=database_id,
                properties=properties_to_add
            )
            
            print(f"✅ Successfully added {len(properties_to_add)} contact properties!")
            print("\nNew contact properties:")
            for prop_name in properties_to_add.keys():
                print(f"   📋 {prop_name}")
        else:
            print("\n✅ All contact properties already exist!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up contact properties: {e}")
        return False

if __name__ == "__main__":
    success = setup_contact_properties()
    if success:
        print("\n🎉 Contact properties setup completed successfully!")
    else:
        print("\n❌ Contact properties setup failed!")
        sys.exit(1)