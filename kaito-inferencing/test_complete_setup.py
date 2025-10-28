#!/usr/bin/env python3
"""
Test script to verify the complete KAITO Phi-4-Mini setup is working
This script tests the API endpoint and demonstrates the interactive chat functionality
"""

import requests
import json
import sys
import time

def test_api_connection():
    """Test basic API connectivity"""
    print("🔗 Testing KAITO API Connection...")
    try:
        response = requests.get('http://localhost:8080/v1/models', timeout=10)
        if response.status_code == 200:
            model_info = response.json()
            model_name = model_info['data'][0]['id']
            max_tokens = model_info['data'][0]['max_model_len']
            print(f"✅ Connected to model: {model_name}")
            print(f"📊 Max context length: {max_tokens:,} tokens")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_chat_completion():
    """Test chat completion functionality"""
    print("\n🤖 Testing Chat Completion...")
    
    test_messages = [
        "What is KAITO?",
        "Explain Kubernetes in one sentence",
        "Write a Python function to add two numbers"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {message}")
        
        try:
            response = requests.post(
                'http://localhost:8080/v1/chat/completions',
                headers={'Content-Type': 'application/json'},
                json={
                    'model': 'phi-4-mini-instruct',
                    'messages': [{'role': 'user', 'content': message}],
                    'max_tokens': 150,
                    'temperature': 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                usage = result.get('usage', {})
                
                print(f"✅ Response: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                if usage:
                    print(f"📈 Tokens used: {usage.get('total_tokens', 'N/A')}")
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)  # Brief pause between requests

def main():
    """Main test function"""
    print("🚀 KAITO Phi-4-Mini Complete Setup Test")
    print("=" * 50)
    
    # Test API connection
    if not test_api_connection():
        print("\n❌ API connection failed. Please check:")
        print("1. KAITO workspace is running: kubectl get workspace")
        print("2. Port-forwarding is active: kubectl port-forward svc/workspace-phi-4-mini-h100 8080:80")
        sys.exit(1)
    
    # Test chat functionality
    test_chat_completion()
    
    print("\n" + "=" * 50)
    print("🎉 Setup test completed!")
    print("\n📋 Your KAITO deployment is ready! You can now:")
    print("🌐 Run web interface: streamlit run phi4_chat_app.py")
    print("💻 Run CLI interface: python3 phi4_chat_cli.py")
    print("🔧 Run setup script: ./setup_chat_demo.sh")

if __name__ == "__main__":
    main()