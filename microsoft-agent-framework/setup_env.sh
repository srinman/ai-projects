#!/bin/bash

# Microsoft Agent Framework Environment Setup Script
# This script helps you set up the required environment variables

echo "Microsoft Agent Framework Environment Setup"
echo "=========================================="
echo ""

# Check if user wants to set environment variables permanently or temporarily
echo "How would you like to set the environment variables?"
echo "1. Temporarily (for this session only)"
echo "2. Permanently (add to ~/.bashrc)"
echo ""
read -p "Enter your choice (1 or 2): " choice

echo ""
echo "You need to find these values from your Azure AI project:"
echo "1. Go to https://portal.azure.com"
echo "2. Navigate to your Azure AI project"
echo "3. Find the endpoint URL (looks like: https://your-project.region.models.ai.azure.com/)"
echo "4. Go to Deployments section to find your model deployment name"
echo ""

# Get Azure AI Project Endpoint
read -p "Enter your AZURE_AI_PROJECT_ENDPOINT (e.g., https://your-project.westus2.models.ai.azure.com/): " endpoint
while [[ -z "$endpoint" ]]; do
    echo "Endpoint cannot be empty!"
    read -p "Enter your AZURE_AI_PROJECT_ENDPOINT: " endpoint
done

# Get Model Deployment Name
read -p "Enter your AZURE_AI_MODEL_DEPLOYMENT_NAME (e.g., gpt-4o-mini): " deployment
while [[ -z "$deployment" ]]; do
    echo "Deployment name cannot be empty!"
    read -p "Enter your AZURE_AI_MODEL_DEPLOYMENT_NAME: " deployment
done

echo ""

if [ "$choice" = "1" ]; then
    # Set temporarily
    echo "Setting environment variables for this session..."
    export AZURE_AI_PROJECT_ENDPOINT="$endpoint"
    export AZURE_AI_MODEL_DEPLOYMENT_NAME="$deployment"
    
    echo "Environment variables set successfully!"
    echo ""
    echo "To use these in your current terminal session, run:"
    echo "source setup_env.sh"
    echo ""
    echo "Or run these commands manually:"
    echo "export AZURE_AI_PROJECT_ENDPOINT=\"$endpoint\""
    echo "export AZURE_AI_MODEL_DEPLOYMENT_NAME=\"$deployment\""
    
elif [ "$choice" = "2" ]; then
    # Set permanently
    echo "Adding environment variables to ~/.bashrc..."
    
    # Remove existing entries if they exist
    grep -v "AZURE_AI_PROJECT_ENDPOINT" ~/.bashrc > ~/.bashrc.tmp && mv ~/.bashrc.tmp ~/.bashrc
    grep -v "AZURE_AI_MODEL_DEPLOYMENT_NAME" ~/.bashrc > ~/.bashrc.tmp && mv ~/.bashrc.tmp ~/.bashrc
    
    # Add new entries
    echo "" >> ~/.bashrc
    echo "# Microsoft Agent Framework Environment Variables" >> ~/.bashrc
    echo "export AZURE_AI_PROJECT_ENDPOINT=\"$endpoint\"" >> ~/.bashrc
    echo "export AZURE_AI_MODEL_DEPLOYMENT_NAME=\"$deployment\"" >> ~/.bashrc
    
    echo "Environment variables added to ~/.bashrc successfully!"
    echo ""
    echo "To apply the changes, either:"
    echo "1. Run: source ~/.bashrc"
    echo "2. Close and reopen your terminal"
    
else
    echo "Invalid choice. Please run the script again and choose 1 or 2."
    exit 1
fi

echo ""
echo "You can verify the environment variables are set by running:"
echo "echo \$AZURE_AI_PROJECT_ENDPOINT"
echo "echo \$AZURE_AI_MODEL_DEPLOYMENT_NAME"
echo ""
echo "Make sure you're logged in with Azure CLI: az login"