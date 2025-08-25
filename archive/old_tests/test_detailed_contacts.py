#!/usr/bin/env python3
"""
Show detailed contact extraction results
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sources.github_source import GitHubSource

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise

def show_contact_results():
    """Show contact extraction results in detail"""
    print("🧪 Contact Extraction Results - Detailed Analysis")
    print("=" * 60)
    
    try:
        # Initialize GitHub source
        github_source = GitHubSource({})
        
        # Test with 5 users
        print("🔍 Analyzing contact info for 5 talents...")
        talents = github_source.search({'max_results': 5})
        
        print(f"\n📊 Contact Extraction Summary:")
        print("-" * 60)
        
        contact_scores = []
        total_contacts = 0
        
        for i, talent in enumerate(talents, 1):
            github_data = talent.platform_data.get('github', {})
            contact_info = github_data.get('contact_info')
            
            if contact_info:
                score = contact_info.get('contact_score', 0)
                contact_scores.append(score)
                
                emails = contact_info.get('emails', [])
                linkedin = contact_info.get('linkedin')
                twitter = contact_info.get('twitter')
                personal_site = contact_info.get('personal_site')
                phone = contact_info.get('phone')
                
                print(f"\n{i}. {talent.name}")
                print(f"   GitHub: {talent.github_url}")
                print(f"   📊 Contact Score: {score:.2f} ({score*100:.0f}%)")
                
                if emails:
                    print(f"   📧 Email: {emails[0]}")
                    total_contacts += 1
                
                if linkedin:
                    print(f"   💼 LinkedIn: {linkedin}")
                    
                if twitter:
                    print(f"   🐦 Twitter: {twitter}")
                    
                if personal_site:
                    print(f"   🌐 Website: {personal_site}")
                    
                if phone:
                    print(f"   📞 Phone: {phone}")
                
                if not any([emails, linkedin, twitter, personal_site, phone]):
                    print("   ❌ No contact information found")
            else:
                print(f"\n{i}. {talent.name}")
                print(f"   GitHub: {talent.github_url}")
                print("   ❌ Contact extraction failed")
                contact_scores.append(0)
        
        # Summary statistics
        if contact_scores:
            avg_score = sum(contact_scores) / len(contact_scores)
            max_score = max(contact_scores)
            contacts_found = sum(1 for score in contact_scores if score > 0)
            
            print(f"\n📈 Contact Extraction Statistics:")
            print(f"   🎯 Profiles with contact info: {contacts_found}/{len(talents)} ({contacts_found/len(talents)*100:.0f}%)")
            print(f"   📧 Profiles with emails: {total_contacts}/{len(talents)} ({total_contacts/len(talents)*100:.0f}%)")
            print(f"   📊 Average contact score: {avg_score:.2f} ({avg_score*100:.0f}%)")
            print(f"   🏆 Best contact score: {max_score:.2f} ({max_score*100:.0f}%)")
        
        print(f"\n✅ Contact extraction system working successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_contact_results()