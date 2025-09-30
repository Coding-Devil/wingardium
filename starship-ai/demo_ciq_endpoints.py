#!/usr/bin/env python3
"""
Demo script to test CIQ API endpoints
Run this to see the CIQ integration in action!
"""

import requests
import json
import time
from typing import Optional

# API Base URL (adjust if your server runs on different port)
BASE_URL = "http://localhost:8000"

def test_ciq_payload():
    """Test the CIQ payload schema endpoint."""
    print("🧪 Testing CIQ Payload Schema...")
    
    url = f"{BASE_URL}/ciq_payload"
    payload = {"input": "get schema"}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {len(data['properties'])} parameters")
            
            # Show first few parameters
            print("\n📋 Sample Parameters:")
            for i, (key, schema) in enumerate(list(data['properties'].items())[:5]):
                print(f"  {i+1}. {key}: {schema['x-displayName']}")
            print(f"  ... and {len(data['properties']) - 5} more")
            
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_ciq_chat_flow():
    """Test a complete CIQ chat conversation flow."""
    print("\n🧪 Testing CIQ Chat Flow...")
    
    url = f"{BASE_URL}/ciq_chat"
    session_id = None
    
    # Test messages to simulate a conversation
    test_messages = [
        "Hello, I need help with CMM configuration",
        "192.168.1.100",  # Parameter value
        "What is ALMS?",  # Technical question
        "10.0.0.1",       # Another parameter value
        "skip"            # Skip current parameter
    ]
    
    for i, message in enumerate(test_messages):
        print(f"\n💬 Message {i+1}: '{message}'")
        
        payload = {"input": message}
        if session_id:
            payload["session_id"] = session_id
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                session_id = data["session_id"]
                
                print(f"🤖 Response: {data['response'][:100]}...")
                print(f"📊 Progress: {data['progress']['progress_percentage']:.1f}% ({data['progress']['collected_count']}/{data['progress']['total_params']})")
                
                if data['is_complete']:
                    print("🎉 All parameters collected!")
                    if data['final_yaml']:
                        print("📄 YAML generated successfully!")
                    break
                    
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                break
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            break
    
    return session_id

def test_session_progress(session_id: str):
    """Test session progress endpoint."""
    print(f"\n🧪 Testing Session Progress for {session_id[:8]}...")
    
    url = f"{BASE_URL}/ciq_session/{session_id}/progress"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Progress: {data['progress_percentage']:.1f}%")
            print(f"📝 Missing params: {len(data['missing_params'])}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def show_swagger_info():
    """Show information about accessing Swagger UI."""
    print("\n" + "="*60)
    print("🌟 SWAGGER UI ACCESS")
    print("="*60)
    print(f"📖 Interactive API Docs: {BASE_URL}/docs")
    print(f"📋 OpenAPI Schema: {BASE_URL}/openapi.json")
    print(f"🔄 ReDoc Alternative: {BASE_URL}/redoc")
    print("\n💡 In Swagger UI, you can:")
    print("  • See all CIQ endpoints with descriptions")
    print("  • Test endpoints directly in the browser")
    print("  • View request/response schemas")
    print("  • Copy curl commands")
    print("="*60)

def main():
    """Run the demo."""
    print("🚀 CIQ API Endpoints Demo")
    print("="*40)
    
    # Show Swagger info first
    show_swagger_info()
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print(f"\n✅ Server is running at {BASE_URL}")
        else:
            print(f"\n⚠️ Server responded with {response.status_code}")
    except:
        print(f"\n❌ Server not reachable at {BASE_URL}")
        print("💡 Start your FastAPI server first:")
        print("   cd src && python -m uvicorn main:app --reload --port 8000")
        return
    
    # Run tests
    print("\n" + "="*40)
    print("🧪 RUNNING API TESTS")
    print("="*40)
    
    # Test 1: Payload schema
    success1 = test_ciq_payload()
    
    # Test 2: Chat flow
    session_id = test_ciq_chat_flow()
    
    # Test 3: Session progress (if we have a session)
    if session_id:
        test_session_progress(session_id)
    
    # Final message
    print("\n" + "="*40)
    print("🎯 DEMO COMPLETE!")
    print("="*40)
    print(f"🌐 Visit {BASE_URL}/docs to explore all endpoints interactively!")

if __name__ == "__main__":
    main()
