#!/usr/bin/env python3
"""
Simple CLI Chat Application for KAITO Phi-4-Mini Inference
Alternative to Streamlit for environments where web UI isn't preferred
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
KAITO_API_URL = "http://localhost:8080/v1/chat/completions"
MODEL_NAME = "phi-4-mini-instruct"

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color):
    print(f"{color}{text}{Colors.END}")

def call_kaito_inference(messages, max_tokens=500, temperature=0.7):
    """
    Call the KAITO inference API
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print_colored("🤔 Phi-4-Mini is thinking...", Colors.YELLOW)
        response = requests.post(
            KAITO_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print_colored("❌ Cannot connect to KAITO service!", Colors.RED)
        print_colored("Make sure port-forwarding is active:", Colors.YELLOW)
        print_colored("kubectl port-forward svc/workspace-phi-4-mini-h100 8080:80", Colors.BLUE)
        return None
    except requests.exceptions.Timeout:
        print_colored("⏱️ Request timed out. The model might be loading.", Colors.RED)
        return None
    except requests.exceptions.RequestException as e:
        print_colored(f"🔥 Request failed: {str(e)}", Colors.RED)
        return None

def check_service_health():
    """
    Check if the KAITO service is accessible
    """
    try:
        health_url = "http://localhost:8080/v1/models"
        response = requests.get(health_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print_colored("🤖 KAITO Phi-4-Mini Chat Interface", Colors.BOLD + Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)
    print("Powered by Microsoft Phi-4-Mini on Azure H100 GPU")
    print()
    
    # Check service health
    if check_service_health():
        print_colored("✅ KAITO Service Connected", Colors.GREEN)
    else:
        print_colored("❌ KAITO Service Disconnected", Colors.RED)
        print_colored("Setup port-forwarding: kubectl port-forward svc/workspace-phi-4-mini-h100 8080:80", Colors.YELLOW)
        print()
    
    # Configuration
    print_colored("⚙️ Configuration (press Enter for defaults):", Colors.BLUE)
    
    try:
        max_tokens_input = input("Max tokens (default: 500): ").strip()
        max_tokens = int(max_tokens_input) if max_tokens_input else 500
        
        temperature_input = input("Temperature 0.0-1.0 (default: 0.7): ").strip()
        temperature = float(temperature_input) if temperature_input else 0.7
        
        system_prompt = input("System prompt (default: helpful assistant): ").strip()
        if not system_prompt:
            system_prompt = "You are a helpful AI assistant that provides clear and concise answers."
    
    except (ValueError, KeyboardInterrupt):
        print_colored("\nUsing default settings.", Colors.YELLOW)
        max_tokens = 500
        temperature = 0.7
        system_prompt = "You are a helpful AI assistant that provides clear and concise answers."
    
    print()
    print_colored("💬 Chat started! Type 'quit', 'exit', or Ctrl+C to end.", Colors.GREEN)
    print_colored("=" * 50, Colors.BLUE)
    print()
    
    # Chat history
    messages = [{"role": "system", "content": system_prompt}]
    
    try:
        while True:
            # Get user input
            user_input = input(f"{Colors.BOLD}You:{Colors.END} ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print_colored("👋 Goodbye!", Colors.GREEN)
                break
            
            if not user_input:
                continue
            
            # Add user message
            messages.append({"role": "user", "content": user_input})
            
            # Get AI response
            response = call_kaito_inference(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if response and "choices" in response:
                assistant_message = response["choices"][0]["message"]["content"]
                print(f"{Colors.BOLD + Colors.GREEN}Phi-4-Mini:{Colors.END} {assistant_message}")
                
                # Show usage statistics
                if "usage" in response:
                    usage = response["usage"]
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print_colored(
                        f"📊 [{timestamp}] Tokens: {usage.get('total_tokens', 'N/A')} "
                        f"(prompt: {usage.get('prompt_tokens', 'N/A')}, "
                        f"completion: {usage.get('completion_tokens', 'N/A')})",
                        Colors.YELLOW
                    )
                
                # Add assistant response to history
                messages.append({"role": "assistant", "content": assistant_message})
                
            else:
                print_colored("❌ Failed to get response from KAITO service", Colors.RED)
            
            print()  # Add spacing between exchanges
            
    except KeyboardInterrupt:
        print()
        print_colored("👋 Chat ended by user.", Colors.GREEN)

if __name__ == "__main__":
    main()