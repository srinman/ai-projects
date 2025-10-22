#!/bin/bash

# Environment Variables Setup Script
# This script helps you set up environment variables for your AI projects

echo "🔧 AI Projects Environment Setup"
echo "================================="
echo ""

ENV_FILE="/home/srinman/git/ai-projects/.env"
TEMPLATE_FILE="/home/srinman/git/ai-projects/.env.template"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env file not found. Creating from template..."
    if [ -f "$TEMPLATE_FILE" ]; then
        cp "$TEMPLATE_FILE" "$ENV_FILE"
        echo "✅ Created .env file from template"
    else
        echo "❌ Template file not found!"
        exit 1
    fi
fi

echo "📝 Current .env file location: $ENV_FILE"
echo ""

# Function to update environment variable
update_env_var() {
    local var_name=$1
    local var_description=$2
    local current_value=$(grep "^$var_name=" "$ENV_FILE" | cut -d'=' -f2-)
    
    echo "🔑 $var_description"
    if [ ! -z "$current_value" ]; then
        echo "   Current value: $current_value"
    else
        echo "   Current value: (not set)"
    fi
    
    read -p "   Enter new value (or press Enter to keep current): " new_value
    
    if [ ! -z "$new_value" ]; then
        # Escape special characters for sed
        escaped_value=$(printf '%s\n' "$new_value" | sed 's/[[\.*^$()+?{|]/\\&/g')
        
        # Update the value in .env file
        if grep -q "^$var_name=" "$ENV_FILE"; then
            sed -i "s|^$var_name=.*|$var_name=$new_value|" "$ENV_FILE"
        else
            echo "$var_name=$new_value" >> "$ENV_FILE"
        fi
        echo "   ✅ Updated $var_name"
    else
        echo "   📌 Keeping current value"
    fi
    echo ""
}

echo "Let's configure your environment variables:"
echo ""

# Azure AI Configuration
echo "🔵 Azure AI Configuration"
update_env_var "AZURE_AI_PROJECT_ENDPOINT" "Azure AI Project Endpoint (e.g., https://your-project.region.models.ai.azure.com/)"
update_env_var "AZURE_AI_MODEL_DEPLOYMENT_NAME" "Azure AI Model Deployment Name (e.g., gpt-4o-mini)"

# Azure OpenAI Configuration
echo "🔵 Azure OpenAI Configuration (optional if using Azure AI)"
read -p "Do you want to configure Azure OpenAI settings? (y/n): " configure_azure_openai
if [[ $configure_azure_openai =~ ^[Yy]$ ]]; then
    update_env_var "AZURE_OPENAI_ENDPOINT" "Azure OpenAI Endpoint"
    update_env_var "AZURE_OPENAI_API_KEY" "Azure OpenAI API Key"
fi

# OpenAI Configuration
echo "🟢 OpenAI Configuration (optional)"
read -p "Do you want to configure OpenAI settings? (y/n): " configure_openai
if [[ $configure_openai =~ ^[Yy]$ ]]; then
    update_env_var "OPENAI_API_KEY" "OpenAI API Key"
    update_env_var "OPENAI_ORG_ID" "OpenAI Organization ID (optional)"
fi

# Other API Keys
echo "🔑 Other API Keys (optional)"
read -p "Do you want to configure other API keys? (y/n): " configure_others
if [[ $configure_others =~ ^[Yy]$ ]]; then
    update_env_var "ANTHROPIC_API_KEY" "Anthropic API Key"
    update_env_var "GOOGLE_API_KEY" "Google API Key"
fi

echo "✅ Environment setup complete!"
echo ""
echo "📁 Your environment file is located at: $ENV_FILE"
echo "🔒 This file is protected by .gitignore and won't be committed to git"
echo ""
echo "To load these variables in your terminal session, run:"
echo "   source .env"
echo "   # or"
echo "   export \$(cat .env | xargs)"
echo ""
echo "To use in Python, install python-dotenv:"
echo "   pip install python-dotenv"
echo ""
echo "Then in your Python code:"
echo "   from dotenv import load_dotenv"
echo "   load_dotenv()"
echo "   import os"
echo "   api_key = os.getenv('OPENAI_API_KEY')"