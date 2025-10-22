#!/bin/bash

# Azure AD Token Helper Script
# This script helps you obtain Azure AD tokens for different scenarios

echo "🔐 Azure AD Token Helper"
echo "========================"
echo ""

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ You are not logged in to Azure CLI. Please run: az login"
    exit 1
fi

echo "✅ Azure CLI is installed and you are logged in"
echo ""

# Function to get token for Azure OpenAI
get_openai_token() {
    echo "🎯 Getting Azure AD token for Azure OpenAI..."
    
    # Get token for Azure OpenAI resource
    local token=$(az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken --output tsv)
    
    if [ $? -eq 0 ] && [ ! -z "$token" ]; then
        echo "✅ Successfully obtained Azure OpenAI token"
        echo "Token (first 20 chars): ${token:0:20}..."
        echo ""
        echo "Full token:"
        echo "$token"
        echo ""
        
        # Optionally save to .env file
        read -p "Do you want to save this token to .env file? (y/n): " save_token
        if [[ $save_token =~ ^[Yy]$ ]]; then
            # Update or add the token to .env file
            if grep -q "AZURE_AD_TOKEN=" /home/srinman/git/ai-projects/.env; then
                sed -i "s|^AZURE_AD_TOKEN=.*|AZURE_AD_TOKEN=$token|" /home/srinman/git/ai-projects/.env
            else
                echo "" >> /home/srinman/git/ai-projects/.env
                echo "# Azure AD Token" >> /home/srinman/git/ai-projects/.env
                echo "AZURE_AD_TOKEN=$token" >> /home/srinman/git/ai-projects/.env
            fi
            echo "✅ Token saved to .env file"
        fi
    else
        echo "❌ Failed to obtain token"
        return 1
    fi
}

# Function to get token for Azure Resource Management
get_arm_token() {
    echo "🎯 Getting Azure AD token for Azure Resource Management..."
    
    local token=$(az account get-access-token --resource https://management.azure.com/ --query accessToken --output tsv)
    
    if [ $? -eq 0 ] && [ ! -z "$token" ]; then
        echo "✅ Successfully obtained ARM token"
        echo "Token (first 20 chars): ${token:0:20}..."
        echo ""
        echo "Full token:"
        echo "$token"
    else
        echo "❌ Failed to obtain ARM token"
        return 1
    fi
}

# Function to get token for Microsoft Graph
get_graph_token() {
    echo "🎯 Getting Azure AD token for Microsoft Graph..."
    
    local token=$(az account get-access-token --resource https://graph.microsoft.com --query accessToken --output tsv)
    
    if [ $? -eq 0 ] && [ ! -z "$token" ]; then
        echo "✅ Successfully obtained Graph token"
        echo "Token (first 20 chars): ${token:0:20}..."
        echo ""
        echo "Full token:"
        echo "$token"
    else
        echo "❌ Failed to obtain Graph token"
        return 1
    fi
}

# Function to show token info
show_token_info() {
    local token=$1
    echo "🔍 Token Information:"
    
    # Decode JWT token (basic info only)
    if command -v python3 &> /dev/null; then
        python3 -c "
import json
import base64
import sys

token = '$token'
try:
    # Split token and decode payload
    header, payload, signature = token.split('.')
    
    # Add padding if needed
    payload += '=' * (4 - len(payload) % 4)
    
    # Decode
    decoded = json.loads(base64.urlsafe_b64decode(payload))
    
    print('Audience (aud):', decoded.get('aud', 'Not found'))
    print('Issuer (iss):', decoded.get('iss', 'Not found'))
    print('Subject (sub):', decoded.get('sub', 'Not found'))
    print('Expires (exp):', decoded.get('exp', 'Not found'))
    
except Exception as e:
    print('Could not decode token:', e)
"
    else
        echo "Python3 not available for token decoding"
    fi
}

# Main menu
echo "What type of Azure AD token do you need?"
echo "1. Azure OpenAI / Cognitive Services token (most common for AI projects)"
echo "2. Azure Resource Management token"
echo "3. Microsoft Graph token"
echo "4. Show current account information"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        get_openai_token
        ;;
    2)
        get_arm_token
        ;;
    3)
        get_graph_token
        ;;
    4)
        echo "📋 Current Azure Account Information:"
        az account show --output table
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📝 Note: Azure AD tokens typically expire after 1 hour."
echo "   For production use, implement token refresh logic."
echo ""
echo "💡 For Kagent ModelConfig, you typically need the Azure OpenAI token (option 1)"