#!/usr/bin/env python3
"""
Azure AD Token Helper
This script helps you obtain Azure AD tokens programmatically using various methods.
"""

import json
import subprocess
import sys
from typing import Optional
import os

try:
    from azure.identity import AzureCliCredential, DefaultAzureCredential
    from azure.core.exceptions import ClientAuthenticationError
    AZURE_IDENTITY_AVAILABLE = True
except ImportError:
    AZURE_IDENTITY_AVAILABLE = False
    print("⚠️  azure-identity not installed. Install with: pip install azure-identity")


def get_token_via_cli(resource: str = "https://cognitiveservices.azure.com") -> Optional[str]:
    """
    Get Azure AD token using Azure CLI.
    
    Args:
        resource: The resource URL to get token for
        
    Returns:
        str: Access token or None if failed
    """
    try:
        cmd = ["az", "account", "get-access-token", "--resource", resource, "--query", "accessToken", "--output", "tsv"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get token via CLI: {e}")
        return None
    except FileNotFoundError:
        print("❌ Azure CLI not found. Please install Azure CLI first.")
        return None


def get_token_via_sdk(resource: str = "https://cognitiveservices.azure.com") -> Optional[str]:
    """
    Get Azure AD token using Azure SDK.
    
    Args:
        resource: The resource URL to get token for
        
    Returns:
        str: Access token or None if failed
    """
    if not AZURE_IDENTITY_AVAILABLE:
        return None
    
    try:
        # Try AzureCliCredential first
        credential = AzureCliCredential()
        token = credential.get_token(resource)
        return token.token
    except ClientAuthenticationError:
        print("❌ Authentication failed with AzureCliCredential")
        
        try:
            # Fallback to DefaultAzureCredential
            credential = DefaultAzureCredential()
            token = credential.get_token(resource)
            return token.token
        except ClientAuthenticationError as e:
            print(f"❌ Authentication failed with DefaultAzureCredential: {e}")
            return None


def decode_jwt_token(token: str) -> dict:
    """
    Decode JWT token payload (basic decoding, no signature verification).
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded token payload
    """
    try:
        import base64
        
        # Split token
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
        
        # Decode payload
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        
        decoded_bytes = base64.urlsafe_b64decode(payload)
        payload_data = json.loads(decoded_bytes.decode('utf-8'))
        
        return payload_data
    except Exception as e:
        print(f"❌ Failed to decode token: {e}")
        return {}


def save_token_to_env(token: str, env_file: str = "/home/srinman/git/ai-projects/.env"):
    """
    Save token to .env file.
    
    Args:
        token: The token to save
        env_file: Path to .env file
    """
    try:
        # Read current .env content
        lines = []
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                lines = f.readlines()
        
        # Find and replace existing AZURE_AD_TOKEN line or add new one
        token_line = f"AZURE_AD_TOKEN={token}\n"
        found = False
        
        for i, line in enumerate(lines):
            if line.startswith("AZURE_AD_TOKEN="):
                lines[i] = token_line
                found = True
                break
        
        if not found:
            # Add token at the end
            if lines and not lines[-1].endswith('\n'):
                lines.append('\n')
            lines.append('\n# Azure AD Token\n')
            lines.append(token_line)
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Token saved to {env_file}")
        
    except Exception as e:
        print(f"❌ Failed to save token: {e}")


def main():
    """Main function to get Azure AD token."""
    print("🔐 Azure AD Token Helper (Python)")
    print("=================================")
    print()
    
    # Define resource options
    resources = {
        "1": ("Azure OpenAI / Cognitive Services", "https://cognitiveservices.azure.com"),
        "2": ("Azure Resource Management", "https://management.azure.com/"),
        "3": ("Microsoft Graph", "https://graph.microsoft.com"),
        "4": ("Custom resource", None)
    }
    
    print("Select the resource to get token for:")
    for key, (name, url) in resources.items():
        print(f"{key}. {name}")
        if url:
            print(f"   Resource URL: {url}")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice not in resources:
        print("❌ Invalid choice")
        return
    
    if choice == "4":
        resource_url = input("Enter custom resource URL: ").strip()
        if not resource_url:
            print("❌ Resource URL cannot be empty")
            return
    else:
        resource_url = resources[choice][1]
    
    print(f"\n🎯 Getting token for: {resource_url}")
    print()
    
    # Try to get token
    token = None
    
    # Method 1: Try Azure SDK
    if AZURE_IDENTITY_AVAILABLE:
        print("Trying Azure SDK method...")
        token = get_token_via_sdk(resource_url)
    
    # Method 2: Fallback to CLI
    if not token:
        print("Trying Azure CLI method...")
        token = get_token_via_cli(resource_url)
    
    if not token:
        print("❌ Failed to obtain token with any method")
        return
    
    print("✅ Successfully obtained token!")
    print(f"Token (first 20 chars): {token[:20]}...")
    print()
    
    # Decode token info
    payload = decode_jwt_token(token)
    if payload:
        print("🔍 Token Information:")
        print(f"   Audience: {payload.get('aud', 'N/A')}")
        print(f"   Issuer: {payload.get('iss', 'N/A')}")
        print(f"   Subject: {payload.get('sub', 'N/A')}")
        
        if 'exp' in payload:
            import datetime
            exp_time = datetime.datetime.fromtimestamp(payload['exp'])
            print(f"   Expires: {exp_time}")
        print()
    
    # Ask if user wants to see full token
    show_full = input("Show full token? (y/n): ").strip().lower()
    if show_full == 'y':
        print("\n📋 Full Token:")
        print(token)
        print()
    
    # Ask if user wants to save to .env
    save_env = input("Save token to .env file? (y/n): ").strip().lower()
    if save_env == 'y':
        save_token_to_env(token)
    
    print()
    print("💡 Note: Tokens typically expire after 1 hour")
    print("   For production, implement proper token refresh logic")


if __name__ == "__main__":
    main()