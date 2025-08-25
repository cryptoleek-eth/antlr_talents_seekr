#!/usr/bin/env python3
"""
Test script for API connections
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_github_connection():
    """Test GitHub API connection"""
    print("🔍 Testing GitHub API connection...")
    
    try:
        from github import Github
        
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("❌ GITHUB_TOKEN not found in environment")
            return False
            
        github = Github(token)
        
        # Test API call
        user = github.get_user()  # Get authenticated user
        
        print(f"✅ GitHub API connected")
        print(f"   Authenticated as: {user.login}")
        
        # Check rate limits (search API has different limits)
        try:
            rate_limit = github.get_rate_limit()
            print(f"   Core API rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
        except Exception as e:
            print(f"   Rate limit info unavailable: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ GitHub API connection failed: {e}")
        return False

def test_notion_connection():
    """Test Notion API connection"""
    print("\n📝 Testing Notion API connection...")
    
    try:
        from notion_client import Client
        
        token = os.getenv('NOTION_TOKEN')
        database_id = os.getenv('NOTION_DATABASE_ID')
        
        if not token:
            print("❌ NOTION_TOKEN not found in environment")
            return False
            
        if not database_id:
            print("❌ NOTION_DATABASE_ID not found in environment")
            return False
        
        notion = Client(auth=token)
        
        # Test database access
        response = notion.databases.retrieve(database_id=database_id)
        
        print(f"✅ Notion API connected")
        print(f"   Database: {response['title'][0]['text']['content']}")
        print(f"   Properties: {len(response['properties'])} fields")
        
        # List some properties
        props = list(response['properties'].keys())[:5]
        print(f"   Fields: {', '.join(props)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Notion API connection failed: {e}")
        return False

def test_search_functionality():
    """Test a simple GitHub search"""
    print("\n🔍 Testing GitHub search functionality...")
    
    try:
        from github import Github
        
        token = os.getenv('GITHUB_TOKEN')
        github = Github(token)
        
        # Simple test search
        users = github.search_users("location:Australia machine learning", sort="repositories")
        
        count = 0
        for user in users:
            count += 1
            if count <= 3:  # Show first 3 results
                print(f"   Found: {user.name or user.login} | {user.location} | {user.public_repos} repos")
            if count >= 3:
                break
        
        print(f"✅ GitHub search working - found {count}+ results")
        return True
        
    except Exception as e:
        print(f"❌ GitHub search failed: {e}")
        return False

def main():
    """Run connection tests"""
    load_dotenv()
    
    print("🧪 Testing Talent-Seekr API Connections")
    print("=" * 40)
    
    github_ok = test_github_connection()
    notion_ok = test_notion_connection() 
    search_ok = test_search_functionality() if github_ok else False
    
    print(f"\n📊 Test Results:")
    print(f"   GitHub API: {'✅' if github_ok else '❌'}")
    print(f"   Notion API: {'✅' if notion_ok else '❌'}")
    print(f"   Search Test: {'✅' if search_ok else '❌'}")
    
    if github_ok and notion_ok and search_ok:
        print("\n🎉 All connections working! Ready to run MVP pipeline.")
        return True
    else:
        print("\n⚠️  Some connections failed. Check your .env file and API tokens.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)