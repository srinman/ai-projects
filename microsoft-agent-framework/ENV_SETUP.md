# Microsoft Agent Framework Environment Variables

This file helps you set up the required environment variables for the Microsoft Agent Framework.

## Required Environment Variables

1. **AZURE_AI_PROJECT_ENDPOINT**: Your Azure AI project endpoint URL
2. **AZURE_AI_MODEL_DEPLOYMENT_NAME**: The name of your deployed model

## How to Find These Values

### Azure AI Project Endpoint
1. Go to [Azure portal](https://portal.azure.com)
2. Navigate to your Azure AI project (Azure AI Foundry)
3. In the project overview, copy the **Endpoint** URL
   - Format: `https://your-project-name.region.models.ai.azure.com/`

### Model Deployment Name
1. In your Azure AI project, go to **Deployments**
2. Find your deployed model (e.g., `gpt-4o-mini`)
3. Copy the deployment name you assigned to it

## Setup Options

### Option 1: Use the Setup Script (Recommended)
Run the interactive setup script:
```bash
./setup_env.sh
```

### Option 2: Manual Setup

#### Temporary (current session only):
```bash
export AZURE_AI_PROJECT_ENDPOINT="https://your-project.region.models.ai.azure.com/"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
```

#### Permanent (add to ~/.bashrc):
```bash
echo 'export AZURE_AI_PROJECT_ENDPOINT="https://your-project.region.models.ai.azure.com/"' >> ~/.bashrc
echo 'export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"' >> ~/.bashrc
source ~/.bashrc
```

### Option 3: Use .env file
Create a `.env` file in your project directory:
```bash
AZURE_AI_PROJECT_ENDPOINT=https://your-project.region.models.ai.azure.com/
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

Then load it in your Python code using `python-dotenv`.

## Verification

Check that your environment variables are set:
```bash
echo $AZURE_AI_PROJECT_ENDPOINT
echo $AZURE_AI_MODEL_DEPLOYMENT_NAME
```

## Authentication

Make sure you're authenticated with Azure CLI:
```bash
az login
```

## Next Steps

Once the environment variables are set, you can run your agent:
```bash
python agent-ai.py
```