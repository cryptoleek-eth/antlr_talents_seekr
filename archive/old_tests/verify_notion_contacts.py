#!/usr/bin/env python3
"""
Verify contact information was saved to Notion database
"""

import os
import sys
from dotenv import load_dotenv
from notion_client import Client

def verify_notion_contacts():
    """Check if contact fields are populated in Notion"""
    load_dotenv()
    
    print("🔍 Verifying Contact Information in Notion Database")
    print("=" * 55)
    
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    if not token or not database_id:
        print("❌ Missing NOTION_TOKEN or NOTION_DATABASE_ID")
        return False
    
    try:
        notion = Client(auth=token)
        
        # Query recent records
        response = notion.databases.query(
            database_id=database_id,
            sorts=[
                {
                    "property": "Discovered Date",
                    "direction": "descending"
                }
            ],
            page_size=5
        )
        
        records = response['results']
        print(f"📊 Found {len(records)} recent records to check")
        
        contact_fields = ['Email', 'Contact Score', 'LinkedIn', 'Twitter', 'Personal Website', 'Contact Methods']
        
        for i, record in enumerate(records, 1):
            properties = record['properties']
            name = properties.get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Unknown')
            
            print(f"\n{i}. {name}")
            
            # Check contact fields
            has_contact_info = False
            
            # Email
            email_prop = properties.get('Email', {})
            if email_prop.get('email'):
                print(f"   📧 Email: {email_prop['email']}")
                has_contact_info = True
            
            # Contact Score
            score_prop = properties.get('Contact Score', {})
            if score_prop.get('number') is not None:
                score = score_prop['number']
                print(f"   📊 Contact Score: {score:.0%}")
                has_contact_info = True
            
            # LinkedIn
            linkedin_prop = properties.get('LinkedIn', {})
            if linkedin_prop.get('url'):
                print(f"   💼 LinkedIn: {linkedin_prop['url']}")
                has_contact_info = True
            
            # Twitter
            twitter_prop = properties.get('Twitter', {})
            if twitter_prop.get('url'):
                print(f"   🐦 Twitter: {twitter_prop['url']}")
                has_contact_info = True
            
            # Personal Website
            website_prop = properties.get('Personal Website', {})
            if website_prop.get('url'):
                print(f"   🌐 Website: {website_prop['url']}")
                has_contact_info = True
            
            # Contact Methods Summary
            methods_prop = properties.get('Contact Methods', {})
            if methods_prop.get('rich_text') and methods_prop['rich_text']:
                methods = methods_prop['rich_text'][0].get('text', {}).get('content', '')
                if methods:
                    print(f"   📝 Contact Methods: {methods}")
                    has_contact_info = True
            
            # Outreach Status
            status_prop = properties.get('Outreach Status', {})
            if status_prop.get('select'):
                status = status_prop['select'].get('name', '')
                print(f"   📬 Outreach Status: {status}")
            
            if not has_contact_info:
                print("   ❌ No contact information found")
        
        print(f"\n✅ Contact verification completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying contacts: {e}")
        return False

if __name__ == "__main__":
    verify_notion_contacts()