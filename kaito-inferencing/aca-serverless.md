# Serverless GPU Inferencing with Azure Container Apps

## Overview

Azure Container Apps now supports **serverless GPUs** with NVIDIA A100 GPUs, providing automatic scaling, scale-to-zero capabilities, and per-second billing. This guide demonstrates deploying a simple AI inference application using serverless A100 GPUs.

## 🚀 Serverless GPU Benefits

**Key Features:**
- ⚡ **Scale-to-zero GPUs**: Automatic serverless scaling of NVIDIA A100 GPUs
- 💰 **Per-second billing**: Pay only for the GPU compute you use
- 🛡️ **Built-in data governance**: Your data never leaves the container boundary
- 🔧 **NVIDIA A100 GPU**: High-performance 80GB VRAM for large models
- 🎯 **Real-time inferencing**: Perfect for dynamic applications with variable load

**GPU Type:**
- **NVIDIA A100**: High-performance for large models (80GB VRAM, 220GB system RAM)

**Supported Regions:**
- West US 3 (A100)
- East US 2 (A100)
- Australia East (A100)
- Sweden Central (A100)

---

## Prerequisites

### Required Setup
1. **Azure Subscription** with GPU quota enabled
2. **Azure CLI** installed and configured
3. **GPU Quota Request** (automatic for Enterprise/Pay-as-you-go customers)

### Request GPU Quota (if needed)
```bash
# Check current quota
az vm list-usage --location "West US 3" --query "[?contains(name.value, 'GPU')]"

# If quota request needed, create support ticket:
# 1. Go to Azure Portal > New Support Request
# 2. Issue type: "Service and subscription limits (quotas)"
# 3. Quota type: "Container Apps"
# 4. Select "Managed Environment Consumption NCA100 Gpus"
```

---

# Simple Inferencing Example

Let's deploy the Phi-3.5-mini-instruct model using Azure AI Foundry templates with A100 GPU.

## Step 1: Create Azure Resources

```bash
# Set deployment variables
export RESOURCE_GROUP="rg-aca-gpu-demo"
export LOCATION="westus3"  # Supports A100 GPUs
export ACA_ENVIRONMENT="aca-gpu-env"
export CONTAINER_APP_NAME="phi-35-a100-aca"  # Using A100 for reliability

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create Container Apps environment with GPU workload profile
az containerapp env create \
  --name $ACA_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --enable-workload-profiles

# Add GPU workload profile for serverless GPU support
az containerapp env workload-profile add \
  --name $ACA_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --workload-profile-name "gpu-a100" \
  --workload-profile-type "Consumption-GPU-NC24-A100"
```

## Step 2: Deploy Azure ML Foundry Model

Microsoft provides pre-built templates for popular AI models through Azure AI Foundry. This feature requires specific Azure CLI versions.

### Prerequisites

**Required Azure CLI Version:**
- **Azure CLI**: 2.78.0+ (current: 2.78.0 ✅)
- **Container Apps Extension**: 1.2.0b4+ (preview)

```bash
# Check your current versions
az version
az extension show --name containerapp | grep version

# Update to required versions if needed
az upgrade
az extension add --name containerapp --yes
az extension update --name containerapp
```

### Available Pre-built Models:
- **Phi-4** (Latest Microsoft model, 14B parameters)
- **Phi-4-reasoning** (Reasoning-optimized variant) 
- **Phi-3.5-mini-instruct** (Lightweight alternative)
- **GPT2-medium** (Simple baseline model)

### Deploy Phi-3.5-mini Model (Recommended)

```bash
### Deploy Phi-3.5-mini-instruct model using Azure AI Foundry

Now deploy the Phi-3.5-mini-instruct model using the Azure AI Foundry template:

```bash
# Deploy with A100 GPU
az containerapp create \
  --name "phi-35-a100-aca" \
  --resource-group $RESOURCE_GROUP \
  --environment $ACA_ENVIRONMENT \
  --model-registry "azureml://registries/azureml/models/Phi-3.5-mini-instruct/versions/1" \
  --target-port 8000 \
  --ingress external \
  --workload-profile-name "gpu-a100"
```

Note: The deployment will take several minutes as the model is downloaded and initialized.
```

### Deploy Phi-4 Model (Advanced)

```bash
# Deploy Phi-4 model using Azure AI Foundry template with A100 GPU
az containerapp up \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --environment $ACA_ENVIRONMENT \
  --model-registry azureml \
  --model-name "Phi-4" \
  --model-version "7" \
  --ingress external \
  --target-port 8000 \
  --workload-profile-name "gpu-a100"

**Note**: The `--model-registry`, `--model-name`, and `--model-version` parameters are in preview. Azure AI Foundry templates come with pre-configured CPU, memory, and scaling settings optimized for each model, so you don't need to specify `--cpu`, `--memory`, `--min-replicas`, or `--max-replicas`.

### Troubleshooting

**Startup Probe Failures (Normal Behavior)**

Azure AI Foundry models may show startup probe failures during initial deployment:
```
Probe of StartUp failed with status code: 1
```
This is **normal** and expected behavior while the container downloads and initializes the model (5-15 minutes).

**Model Download Issues**

If you see `azcopy failed with return code 137` errors:
```
RuntimeError: azcopy failed with return code 137. Stderr: Killed
```
This indicates the model download was terminated due to memory constraints. Solutions:

1. **Try a smaller model first** (GPT2-medium):
```bash
az containerapp up \
  --name "gpt2-test-aca" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --environment $ACA_ENVIRONMENT \
  --model-registry azureml \
  --model-name "gpt2-medium" \
  --model-version "1" \
  --ingress external \
  --target-port 8000 \
  --workload-profile-name "gpu-a100"
```

### Troubleshooting
az containerapp up \
  --name "phi-35-a100-aca" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --environment $ACA_ENVIRONMENT \
  --model-registry azureml \
  --model-name "Phi-3.5-mini-instruct" \
  --model-version "1" \
  --ingress external \
  --target-port 8000 \
  --workload-profile-name "gpu-a100"
```

**Monitor Deployment Progress:**
```bash
# Check deployment status
az containerapp show \
  --name "phi-35-a100-aca" \
  --resource-group $RESOURCE_GROUP \
  --query "{revision: properties.latestRevisionName, status: properties.runningStatus}" \
  --output table

# Monitor logs for model loading progress
az containerapp logs show \
  --name "phi-35-a100-aca" \
  --resource-group $RESOURCE_GROUP \
  --tail 20

# Test when ready (may take 5-15 minutes)
APP_URL="phi-35-a100-aca.lemonsmoke-0d453817.westus3.azurecontainerapps.io"
curl -s "https://$APP_URL/v1/models" || echo "Still loading..."
```

If you get "unrecognized arguments" errors for `--model-registry`:

```bash
# Option 1: Update Azure CLI and extension
az upgrade
az extension update --name containerapp

# Option 2: Use alternative deployment with vLLM
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ACA_ENVIRONMENT \
  --image "vllm/vllm-openai:latest" \
  --workload-profile-name "Consumption" \
  --cpu 4.0 \
  --memory 8Gi \
  --min-replicas 0 \
  --max-replicas 3 \
  --target-port 8000 \
  --ingress external \
  --env-vars "MODEL=microsoft/Phi-3.5-mini-instruct"
```

## Step 3: Test the Deployment

```bash
# Get the application URL
APP_URL=$(az containerapp show \
  --name "phi-35-a100-aca" \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv)

echo "🚀 Application URL: https://$APP_URL"

# Wait for deployment to complete (Foundry models need time to download)
echo "⏳ Waiting for model to be ready..."
sleep 60

# Test health endpoint (Azure ML templates typically expose /health)
curl -s "https://$APP_URL/health" || curl -s "https://$APP_URL/"

# Test text completion with OpenAI-compatible API
curl -X POST "https://$APP_URL/v1/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Phi-3.5-mini-instruct",
    "prompt": "The future of artificial intelligence is",
    "max_tokens": 100,
    "temperature": 0.7
  }' | jq .

# Alternative: Test with chat completions format
curl -X POST "https://$APP_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Phi-3.5-mini-instruct",
    "messages": [
      {"role": "user", "content": "What are the benefits of serverless computing?"}
    ],
    "max_tokens": 150,
    "temperature": 0.7
  }' | jq .
```

### Expected Output

The Azure ML Foundry templates provide OpenAI-compatible endpoints:

```json
{
  "id": "cmpl-xyz123",
  "object": "text_completion",
  "created": 1699123456,
  "model": "Phi-4",
  "choices": [
    {
      "text": "The future of artificial intelligence is incredibly promising, with advances in machine learning...",
      "index": 0,
      "finish_reason": "length"
    }
  ],
  "usage": {
    "prompt_tokens": 8,
    "completion_tokens": 100,
    "total_tokens": 108
  }
}
```
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The future of AI is",
    "max_length": 50,
    "temperature": 0.7
  }' | jq .

# Check available models
curl -s "https://$APP_URL/models" | jq .
```

---

# Monitoring and Scaling

## View GPU Usage and Scaling

```bash
# Monitor container app logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# Check scaling status and GPU utilization
az containerapp revision list \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table

# View workload profile usage and GPU allocation
az containerapp env workload-profile list \
  --name $ACA_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --output table

# Check specific GPU metrics
az monitor metrics list \
  --resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$CONTAINER_APP_NAME" \
  --metric "WorkloadProfileMemoryUsage,WorkloadProfileCpuUsage" \
  --output table
```

## Model Performance and Cold Start

Azure ML Foundry templates are optimized for serverless deployment:

- **Model Caching**: Pre-downloaded models in container layers
- **Fast GPU Initialization**: Optimized CUDA runtime startup  
- **Scale-to-Zero**: Automatic scale down to 0 replicas when idle
- **Warm Start**: Models remain loaded during scaling events

### Monitor Performance

```bash
# Test response time
time curl -X POST "https://$APP_URL/v1/completions" \
  -H "Content-Type: application/json" \
  -d '{"model": "Phi-4", "prompt": "Hello", "max_tokens": 10}'

# Check model loading status in logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[?contains(message, 'model') || contains(message, 'GPU')].message"
```
  --image text-generator:v1
```

---

# Upgrading to A100 for Larger Models

For larger models or higher throughput, upgrade to A100 GPUs:

```bash
# Deploy with A100 for better performance
az containerapp up \
  --name "phi4-a100-aca" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --environment $ACA_ENVIRONMENT \
  --model-registry azureml \
  --model-name "Phi-4" \
  --model-version "7" \
  --ingress external \
  --target-port 8000 \
  --workload-profile-name "gpu-a100"

# Or deploy larger model variants
az containerapp up \
  --name "phi4-reasoning-aca" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --environment $ACA_ENVIRONMENT \
  --model-registry azureml \
  --model-name "Phi-4-reasoning" \
  --model-version "1" \
  --ingress external \
  --target-port 8000 \
  --workload-profile-name "gpu-a100"
```

---

# Cost Monitoring

```bash
# Set up cost monitoring for GPU usage
az monitor action-group create \
  --resource-group $RESOURCE_GROUP \
  --name "gpu-cost-alerts" \
  --short-name "gpu-alerts"

# Monitor GPU costs with budget
az consumption budget create \
  --resource-group $RESOURCE_GROUP \
  --budget-name "gpu-inference-budget" \
  --amount 50 \
  --time-grain Monthly \
  --start-date $(date -d "first day of this month" +%Y-%m-%d) \
  --end-date $(date -d "last day of next month" +%Y-%m-%d)
```

---

# Using the Python Chat Applications

The existing Python chat applications (from the KAITO guide) work seamlessly with Azure Container Apps endpoints thanks to the OpenAI-compatible API format.

## Quick Setup

```bash
# Copy the Python apps from the KAITO directory
cp /home/srinman/git/ai-projects/inferencing/phi4_chat_*.py .
cp /home/srinman/git/ai-projects/inferencing/setup_chat_demo.sh .

# Update the API endpoint to use your ACA deployment
export API_BASE_URL="https://$APP_URL/v1"
export MODEL_NAME="Phi-4"

# Install dependencies and run
bash setup_chat_demo.sh

# Run the Streamlit web interface
streamlit run phi4_chat_app.py

# Or use the CLI version
python phi4_chat_cli.py
```

## API Compatibility

Both Python applications automatically detect and use the OpenAI-compatible endpoints:

- **Streamlit Web UI**: Interactive chat interface at `http://localhost:8501`
- **CLI Chat**: Terminal-based conversation interface
- **OpenAI Format**: Uses `v1/chat/completions` endpoint
- **Model Selection**: Automatically uses deployed Phi-4 model

The same Python code works with both KAITO (port-forward) and ACA (HTTPS) deployments! 🎉

---

# Example API Usage with Azure ML Foundry Templates

The Azure ML Foundry templates provide OpenAI-compatible endpoints:

```bash
# Simple text completion using OpenAI format
curl -X POST "https://$APP_URL/v1/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Phi-4",
    "prompt": "Azure Container Apps with GPUs enables",
    "max_tokens": 80,
    "temperature": 0.8
  }'

# Chat completion for conversations
curl -X POST "https://$APP_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Phi-4", 
    "messages": [
      {"role": "user", "content": "Explain the benefits of serverless GPUs"}
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }'

# Creative writing with higher temperature
curl -X POST "https://$APP_URL/v1/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Phi-4",
    "prompt": "Once upon a time in a serverless cloud",
    "max_tokens": 100,
    "temperature": 0.9
  }'

# Technical explanation with lower temperature
curl -X POST "https://$APP_URL/v1/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Phi-4",
    "prompt": "Serverless GPUs are beneficial because",
    "max_tokens": 60,
    "temperature": 0.3
  }'

# List available models
curl -X GET "https://$APP_URL/v1/models" \
  -H "Content-Type: application/json"
```

---

# Key Benefits Demonstrated

## ✅ What This Example Shows

1. **🚀 True Serverless GPUs**: Automatic scaling from 0 to multiple GPU replicas
2. **💰 Cost Efficiency**: Pay-per-second GPU billing with scale-to-zero
3. **⚡ GPU Performance**: CUDA acceleration for fast inference
4. **🛡️ Data Privacy**: Your data never leaves your container boundary
5. **🔧 Simple Deployment**: Standard container deployment with GPU enablement
6. **📊 Built-in Monitoring**: Automatic logging and metrics collection

## 🎯 Comparison with Other Approaches

| Feature | ACA Serverless GPU | AKS + KAITO | Traditional GPU VMs |
|---------|-------------------|-------------|-------------------|
| **Setup Time** | 5-10 minutes | 30-60 minutes | Hours |
| **Scaling** | Automatic (0 to N) | Manual/HPA | Manual |
| **Idle Cost** | $0 (scale-to-zero) | Node reservation | Full VM cost |
| **Management** | Fully managed | Kubernetes mgmt | Full VM mgmt |
| **GPU Types** | A100 | H100, A100, V100 | Any supported |
| **Best For** | Variable workloads | Enterprise production | Custom requirements |

---

# Summary

This simple example demonstrates how Azure Container Apps with serverless GPUs provides:

- **🎯 Rapid deployment** of GPU-accelerated AI models
- **💰 Cost-effective scaling** with automatic scale-to-zero
- **⚡ Production-ready performance** with NVIDIA A100 GPUs
- **🛡️ Enterprise security** with data governance and VNet integration
- **🔧 Developer-friendly** experience with standard container workflows

The serverless GPU capability bridges the gap between managed AI services and self-managed infrastructure, providing the perfect balance of control, cost-efficiency, and ease of use for AI inferencing workloads! 🚀
