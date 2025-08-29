#!/usr/bin/env python3
"""
Test script for the new sendEmail endpoint
"""

import requests
import json
import sys

def test_send_email():
    """Test the sendEmail endpoint"""
    base_url = "http://localhost:8001"
    
    print("🚀 Testing sendEmail Endpoint")
    print("=" * 50)
    
    # Test data
    test_cases = [
        {
            "name": "Alex Chen",
            "company": "Antler",
            "position": "AI Founder",
            "template_id": "startup_founder",
            "message": "Your work on AI tools and community engagement really caught our attention."
        },
        {
            "name": "John Doe",
            "company": "TechCorp",
            "position": "Senior Developer",
            "template_id": "professional_intro",
            "message": "I'd love to discuss a Python development role."
        },
        {
            "name": "Jane Smith",
            "company": "Innovation Labs",
            "position": "ML Engineer",
            "template_id": "job_opportunity",
            "message": "We have an exciting machine learning opportunity."
        },
        {
            "name": "Bob Wilson",
            "company": "StartupXYZ",
            "position": "Full Stack Developer",
            "template_id": "networking"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 Test Case {i}: {test_case['template_id']}")
        print("-" * 40)
        
        # Prepare request data
        request_data = {
            "send_to_email": "test@example.com",  # Replace with real email for testing
            "name": test_case["name"],
            "company": test_case["company"],
            "position": test_case["position"],
            "template_id": test_case["template_id"]
        }
        
        if test_case.get("message"):
            request_data["message"] = test_case["message"]
        
        print(f"📤 Sending to: {request_data['send_to_email']}")
        print(f"👤 Name: {request_data['name']}")
        print(f"🏢 Company: {request_data['company']}")
        print(f"💼 Position: {request_data['position']}")
        print(f"📝 Template: {request_data['template_id']}")
        if test_case.get("message"):
            print(f"💬 Custom Message: {test_case['message']}")
        
        try:
            # Send request
            response = requests.post(
                f"{base_url}/api/v1/outreach/sendEmail",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"📧 Email ID: {result.get('email_id', 'N/A')}")
                print(f"📋 Subject: {result.get('subject', 'N/A')}")
                print(f"📄 Template Used: {result.get('template_used', 'N/A')}")
            else:
                print(f"❌ Failed (Status: {response.status_code})")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to API server")
            print("Make sure the server is running at http://localhost:8001")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print("The sendEmail endpoint is now available at:")
    print(f"POST {base_url}/api/v1/outreach/sendEmail")
    print("\nRequired parameters:")
    print("• send_to_email: Recipient email address")
    print("• name: Recipient name")
    print("\nOptional parameters:")
    print("• company: Company name (default: TalentSeeker)")
    print("• position: Job position (default: Recruiter)")
    print("• message: Custom message to append")
    print("• template_id: Template to use (default: professional_intro)")
    print("\nAvailable templates:")
print("• startup_founder ⭐ (NEW - for AI founders)")
print("• professional_intro")
print("• technical_role")
print("• networking")
print("• job_opportunity")

if __name__ == "__main__":
    test_send_email()
