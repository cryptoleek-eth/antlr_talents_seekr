#!/usr/bin/env python3
"""
Test website scraping with Jina.ai to see what we get from Alzayat's site
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_jina_scraping():
    """Test Jina.ai scraping of Alzayat's website"""
    print("🌐 Testing Jina.ai Website Scraping")
    print("=" * 45)
    
    jina_token = os.getenv('JINA_API_TOKEN')
    if not jina_token:
        print("❌ JINA_API_TOKEN not found")
        return
    
    website = "https://www.alzayat.com"
    
    headers = {
        'Authorization': f'Bearer {jina_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"🔍 Scraping: {website}")
        response = requests.get(
            f"https://r.jina.ai/{website}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ Successfully scraped website ({len(content)} characters)")
            print(f"\n📄 Content Preview (first 1000 chars):")
            print("-" * 50)
            print(content[:1000])
            print("\n" + "." * 20 + " [truncated] " + "." * 20)
            
            # Look for obvious contact patterns
            import re
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content, re.IGNORECASE)
            linkedin_links = re.findall(r'linkedin\.com/in/[a-zA-Z0-9-]+', content, re.IGNORECASE)
            twitter_links = re.findall(r'twitter\.com/[a-zA-Z0-9_]+', content, re.IGNORECASE)
            
            print(f"\n🔍 Contact Info Found in Website:")
            print(f"   📧 Emails: {emails}")
            print(f"   💼 LinkedIn: {linkedin_links}")  
            print(f"   🐦 Twitter: {twitter_links}")
            
            if not any([emails, linkedin_links, twitter_links]):
                print("   ❌ No obvious contact info found in basic patterns")
                print("   💡 This is where OpenAI 4o-mini would be helpful!")
            
        else:
            print(f"❌ Scraping failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_jina_scraping()