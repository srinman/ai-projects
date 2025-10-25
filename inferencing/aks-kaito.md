
# KAITO: Simplified Inferencing with Open Source Models

## Overview

KAITO (Kubernetes AI Toolchain Operator) revolutionizes how organizations deploy and manage open source large language models (LLMs) for inference workloads. This document demonstrates building a complete self-hosted AI chat application using KAITO to deploy Microsoft's Phi-4-Mini model on Azure Kubernetes Service.

## The Traditional Challenge: Complex Model Inferencing

Deploying and managing LLMs for inference traditionally requires extensive infrastructure setup and expertise:

### Manual Implementation Requirements:
1. **Infrastructure Provisioning**: Setting up GPU-enabled compute instances
2. **Container Orchestration**: Configuring Kubernetes deployments, services, and ingress
3. **GPU Management**: Installing NVIDIA drivers, CUDA libraries, and device plugins
4. **Model Loading**: Downloading multi-gigabyte model weights and configuring storage
5. **Inference Engine Setup**: Installing and configuring vLLM, TensorRT, or similar frameworks
6. **API Development**: Creating OpenAI-compatible REST endpoints for applications
7. **Resource Optimization**: Tuning GPU memory utilization and tensor parallelism
8. **Monitoring & Scaling**: Implementing health checks, metrics, and autoscaling
9. **Security & Networking**: Managing secrets, network policies, and access controls
10. **Version Management**: Handling model updates and rollback procedures

This complexity often leads to months of development time and requires specialized DevOps and ML engineering expertise.

### Reference links   
https://kaito-project.github.io/kaito/docs/inference/#inference-api   
https://kaito-project.github.io/kaito/docs/inference/   
https://github.com/kaito-project/kaito/blob/main/presets/workspace/inference/vllm/api_spec.json   
   

### KAITO based steps   

#### Step 1
```bash
# Deploy with custom instance type (H100)
kubectl apply -f - << EOF
apiVersion: kaito.sh/v1beta1
kind: Workspace
metadata:
  name: workspace-phi-4-mini-h100
resource:
  instanceType: "Standard_NC40ads_H100_v5"
  labelSelector:
    matchLabels:
      apps: phi-4-h100
inference:
  preset:
    name: phi-4-mini-instruct
EOF
```

#### Step 2: Monitor Deployment Progress

```bash
# Check workspace status
kubectl get workspace workspace-phi-4-mini-h100

# Monitor node provisioning
kubectl get nodes --show-labels | grep -i phi

kubectl get node aks-ws7332bdd6a-26399086-vmss000000 -o json | jq .status.allocatable 

Check for # of GPUs.

KAITO supports vLLM.  

Verify inferencing 

```bash
# Test the deployed model with a simple curl command
kubectl run -it --rm --restart=Never curl --image=curlimages/curl -- curl -X POST http://workspace-phi-4-mini-h100/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi-4-mini-instruct",
    "messages": [{"role": "user", "content": "What is kubernetes?"}],
    "max_tokens": 50,
    "temperature": 0
  }'
```

---

# Building Interactive Chat Applications

Now that we have our self-hosted Phi-4-Mini model deployed via KAITO, let's create sophisticated chat applications to interact with it.

## 🔒 Self-Hosted AI: Complete Data Privacy & Control

**Important:** This implementation demonstrates a **fully self-contained AI chat application** that doesn't rely on external AI services like OpenAI, Azure OpenAI, or other cloud-hosted AI endpoints. All inference processing happens within your own AKS cluster using your self-hosted Phi-4-Mini model.

**Key Benefits:**
- 🛡️ **Data Privacy**: All conversations and processing stay within your infrastructure
- 💰 **Cost Control**: No per-token charges or API rate limits from external providers  
- 🚀 **Performance**: Direct access to your GPU resources without network latency to external APIs
- 🔧 **Customization**: Full control over model parameters, fine-tuning, and deployment configuration
- 📊 **Compliance**: Meet strict data governance requirements for sensitive workloads
- 🌐 **Offline Capability**: Works without internet connectivity to external AI services

**Perfect Use Cases:**
- Enterprise applications requiring data sovereignty
- Financial services with strict compliance requirements
- Healthcare applications handling sensitive patient data
- Government and defense applications
- Development environments for AI application prototyping
- Educational institutions teaching AI implementation concepts

This architecture showcases how to build production-ready AI chat applications using **your own infrastructure**, giving you complete ownership of both the data and the AI processing pipeline.

## 🏗️ Architecture Overview

Here's how our Python applications interact with KAITO components and Kubernetes services for inferencing:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Developer/User Environment                             │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐  │
│  │  Streamlit App  │    │   CLI App       │    │  setup_chat_demo.sh         │  │
│  │  phi4_chat_app  │    │  phi4_chat_cli  │    │  (Automation Script)        │  │
│  │                 │    │                 │    │                             │  │
│  │ • Web UI        │    │ • Terminal      │    │ • Workspace validation      │  │
│  │ • Chat History  │    │ • Colored       │    │ • Port-forward setup       │  │
│  │ • Configuration │    │ • Interactive   │    │ • Health checks             │  │
│  │ • Token metrics │    │ • Session mgmt  │    │ • Cleanup handling          │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────────┘  │
│           │                       │                            │                │
│           └───────────┬───────────┘                            │                │
│                       │                                        │                │
│              ┌─────────▼─────────┐                    ┌────────▼─────────┐      │
│              │   HTTP Requests   │                    │   kubectl CLI    │      │
│              │ localhost:8080    │                    │   Commands       │      │
│              │                   │                    │                  │      │
│              │ POST /v1/chat/    │                    │ • port-forward   │      │
│              │    completions    │                    │ • get workspace  │      │
│              │ GET /v1/models    │                    │ • get service    │      │
│              └─────────┬─────────┘                    │ • get nodes      │      │
│                        │                              └──────────────────┘      │
└────────────────────────┼─────────────────────────────────────────────────────────┘
                         │
                 ┌───────▼────────┐
                 │ Port-Forward   │
                 │ localhost:8080 │ ◄──── kubectl port-forward
                 │       ↕        │       svc/workspace-phi-4-mini-h100 8080:80
                 │   Tunnel       │
                 └───────┬────────┘
                         │
┌────────────────────────┼─────────────────────────────────────────────────────────┐
│                 Azure Kubernetes Service (AKS) Cluster                          │
│                        │                                                        │
│  ┌─────────────────────▼──────────────────────────────────────────────────────┐ │
│  │                    Kubernetes Service Layer                                │ │
│  │                                                                            │ │
│  │    ┌──────────────────────────────────────────────────────────────────┐    │ │
│  │    │              Service: workspace-phi-4-mini-h100                 │    │ │
│  │    │                                                                  │    │ │
│  │    │  • ClusterIP: 10.0.154.158:80                                  │    │ │
│  │    │  • LoadBalancer/Ingress capabilities                           │    │ │
│  │    │  • Routes traffic to KAITO workload pods                       │    │ │
│  │    │  • Health checks and service discovery                         │    │ │
│  │    └────────────────────────┬─────────────────────────────────────────┘    │ │
│  └─────────────────────────────┼──────────────────────────────────────────────┘ │
│                                │                                                │
│  ┌─────────────────────────────▼──────────────────────────────────────────────┐ │
│  │                         KAITO Components                                   │ │
│  │                                                                            │ │
│  │  ┌──────────────────┐                  ┌──────────────────────────────────┐ │ │
│  │  │  KAITO Operator  │                  │     Workspace Controller         │ │ │
│  │  │                  │                  │                                  │ │ │
│  │  │ • CRD Management │                  │ • Workspace lifecycle mgmt       │ │ │
│  │  │ • Resource       │◄────────────────►│ • Node provisioning              │ │ │
│  │  │   Reconciliation │                  │ • GPU resource allocation        │ │ │
│  │  │ • Event handling │                  │ • Model deployment orchestration │ │ │
│  │  └──────────────────┘                  └──────────────────────────────────┘ │ │
│  │                                                         │                   │ │
│  │  ┌──────────────────────────────────────────────────────▼─────────────────┐ │ │
│  │  │                    Workspace: workspace-phi-4-mini-h100                │ │ │
│  │  │                                                                         │ │ │
│  │  │  apiVersion: kaito.sh/v1beta1                                          │ │ │
│  │  │  kind: Workspace                                                       │ │ │
│  │  │  spec:                                                                 │ │ │
│  │  │    resource:                                                           │ │ │
│  │  │      instanceType: "Standard_NC40ads_H100_v5"                         │ │ │
│  │  │    inference:                                                          │ │ │
│  │  │      preset:                                                           │ │ │
│  │  │        name: "phi-4-mini-instruct"                                     │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                │                                  │
│  ┌─────────────────────────────────────────────▼────────────────────────────────┐ │
│  │                       Workload Pods                                          │ │
│  │                                                                              │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐  │ │
│  │  │  Pod: workspace-phi-4-mini-h100-xxxxx                                 │  │ │
│  │  │                                                                        │  │ │
│  │  │  ┌─────────────────┐              ┌─────────────────────────────────┐  │  │ │
│  │  │  │  vLLM Server    │              │     Model Storage               │  │  │ │
│  │  │  │                 │              │                                 │  │  │ │
│  │  │  │ • OpenAI API    │              │ • Phi-4-Mini weights           │  │  │ │
│  │  │  │   Compatible    │              │ • Tokenizer files              │  │  │ │
│  │  │  │ • Port 5000     │◄────────────►│ • Configuration files          │  │  │ │
│  │  │  │ • GPU Memory    │              │ • Mounted from persistent       │  │  │ │
│  │  │  │   Optimization  │              │   storage or registry           │  │  │ │
│  │  │  │ • Tensor        │              │                                 │  │  │ │
│  │  │  │   Parallelism   │              │                                 │  │  │ │
│  │  │  └─────────────────┘              └─────────────────────────────────┘  │  │ │
│  │  └────────────────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                │                                  │
│  ┌─────────────────────────────────────────────▼────────────────────────────────┐ │
│  │                       GPU Node Infrastructure                                │ │
│  │                                                                              │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐  │ │
│  │  │   Node: aks-ws7332bdd6a-26399086-vmss000000                           │  │ │
│  │  │                                                                        │  │ │
│  │  │   Instance Type: Standard_NC40ads_H100_v5                             │  │ │
│  │  │   GPU: NVIDIA H100 (80GB HBM3)                                       │  │ │
│  │  │   Labels: apps=phi-4-h100                                            │  │ │
│  │  │                                                                        │  │ │
│  │  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐    │  │ │
│  │  │   │   NVIDIA    │  │   CUDA      │  │      Kubernetes            │    │  │ │
│  │  │   │   Drivers   │  │   Runtime   │  │      Device Plugin         │    │  │ │
│  │  │   │             │  │             │  │                             │    │  │ │
│  │  │   │ • GPU Mgmt  │  │ • Memory    │  │ • GPU resource allocation   │    │  │ │
│  │  │   │ • Hardware  │  │ • Compute   │  │ • Container runtime         │    │  │ │
│  │  │   │   Interface │  │ • Tensor    │  │ • Resource scheduling       │    │  │ │
│  │  │   └─────────────┘  └─────────────┘  └─────────────────────────────┘    │  │ │
│  │  └────────────────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘

                              Data Flow & API Interactions

┌─────────────────┐    HTTP POST     ┌──────────────┐    K8s Service    ┌─────────────┐
│   Python Apps  │ ───────────────► │ Port-Forward │ ─────────────────► │   vLLM      │
│                 │  /v1/chat/       │ localhost:   │   ClusterIP:80    │   Server    │
│ • Streamlit     │   completions    │   8080       │                   │             │
│ • CLI           │                  │              │                   │ • Inference │
│ • Test Scripts  │ ◄─────────────── │              │ ◄───────────────── │ • Response  │
└─────────────────┘    JSON Response └──────────────┘    JSON Response  └─────────────┘
       │                                                                        │
       │                                                                        │
       └── Configuration & Management ──┐                        ┌─────────────┘
                                        │                        │
       ┌─────────────────────────────────▼─────────────────────────▼─────────────┐
       │                    KAITO Workspace Management                           │
       │                                                                         │
       │  • Resource provisioning (H100 GPU nodes)                             │
       │  • Model deployment (Phi-4-Mini preset)                               │
       │  • Service exposure (LoadBalancer/ClusterIP)                          │
       │  • Health monitoring and auto-recovery                                │
       │  • Scaling and resource optimization                                  │
       └─────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Request Flow Walkthrough

1. **🚀 Application Start**: Python apps (`phi4_chat_app.py` or `phi4_chat_cli.py`) start up
2. **🔌 Port Forward**: `kubectl port-forward` creates secure tunnel from localhost:8080 to service
3. **🌐 Service Discovery**: Kubernetes service routes traffic to healthy pod replicas
4. **📡 API Request**: Apps send HTTP POST to `/v1/chat/completions` with user messages
5. **⚡ Inference**: vLLM server processes request using Phi-4-Mini model on H100 GPU
6. **📤 Response**: Generated text returns through the same path back to user interface
7. **📊 Monitoring**: KAITO operator continuously monitors workspace health and performance

## 🎛️ Component Responsibilities

| Component | Function | Technology |
|-----------|----------|------------|
| **Python Apps** | User interface & experience | Streamlit, CLI, HTTP requests |
| **Port-Forward** | Secure tunnel for development | kubectl proxy tunnel |
| **Kubernetes Service** | Load balancing & service discovery | K8s ClusterIP/LoadBalancer |
| **KAITO Operator** | Infrastructure automation | Custom Resource Controllers |
| **Workspace CRD** | Declarative model deployment | YAML configuration |
| **vLLM Server** | High-performance inference | OpenAI-compatible API |
| **H100 GPU** | Accelerated compute | NVIDIA CUDA, Tensor cores |

---

# Application Development Guide

## Step 1: Get the Service ClusterIP

```bash
# Get the service details
kubectl get svc workspace-phi-4-mini-h100

# Extract the ClusterIP
export CLUSTER_IP=$(kubectl get svc workspace-phi-4-mini-h100 -o jsonpath='{.spec.clusterIP}')
echo "Service ClusterIP: $CLUSTER_IP"

# Check GPU allocation on the node
kubectl get node --show-labels | grep -i phi
kubectl get node aks-ws7332bdd6a-26399086-vmss000000 -o json | jq .status.allocatable
```

## Step 2: Setup Port-Forwarding

```bash
# Forward the service to localhost for easy access
kubectl port-forward svc/workspace-phi-4-mini-h100 8080:80

# In another terminal, test the connection
curl http://localhost:8080/v1/models
```

## Step 3: Install Python Dependencies

```bash
# Install required packages
pip install streamlit requests

# Or use the requirements file
pip install -r requirements.txt
```

## Step 4: Launch the Chat Interface

You have two options for interacting with Phi-4-Mini:

### Option A: Web-based Streamlit Interface
```bash
# Launch the interactive web UI
streamlit run phi4_chat_app.py

# This will open http://localhost:8501 in your browser
```

**Features:**
- 🌐 **Modern Web UI**: Clean, responsive Streamlit interface
- ⚙️ **Live Configuration**: Adjust temperature, max tokens, system prompts
- 💬 **Chat History**: Persistent conversation with timestamps
- 📊 **Token Usage**: Real-time statistics and performance metrics
- 🔄 **Auto-Reconnection**: Health checks and connection status
- 🎨 **Rich Formatting**: Markdown support for code and formatting

### Option B: Command-Line Interface
```bash
# Launch the CLI chat application
python3 phi4_chat_cli.py
```

**Features:**
- 💻 **Terminal-based**: No browser required, works in SSH sessions
- 🎨 **Colored Output**: Syntax highlighting for better readability
- ⚡ **Quick Setup**: Faster startup than web interface
- 📋 **Session Config**: Configure parameters at startup
- 🔧 **Lightweight**: Minimal dependencies and resource usage

## Step 5: Automated Setup (Recommended)

For the complete setup experience, use our automation script:

```bash
# Run the complete setup script
./setup_chat_demo.sh
```

**What the script does:**
1. ✅ **Validates workspace** is ready and healthy
2. 🔌 **Sets up port-forwarding** automatically
3. 🧪 **Tests connectivity** to ensure everything works
4. 🚀 **Provides usage instructions** for both interfaces
5. 🧹 **Handles cleanup** when stopped

## Sample Interaction

Once your chat interface is running, you can have conversations like:

**You:** *What is Kubernetes?*

**Phi-4-Mini:** *Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It provides features like service discovery, load balancing, storage orchestration, and automated rollouts and rollbacks, making it easier to manage complex distributed systems at scale.*

**Advanced Examples:**

```python
# Code generation
"Write a Python function to calculate Fibonacci numbers"

# Technical explanations  
"Explain the differences between microservices and monolithic architecture"

# Problem solving
"How would I optimize a SQL query that's running slowly?"

# Creative tasks
"Write a haiku about cloud computing"
```

---

# Performance & Optimization

## KAITO + vLLM Optimizations:
- 🚀 **High Throughput**: vLLM provides optimized inference with attention optimizations
- 🎯 **GPU Utilization**: 95% GPU memory utilization for maximum performance
- ⚡ **Fast Response**: H100 GPU delivers sub-second response times
- 📊 **Batch Processing**: Efficient handling of multiple concurrent requests
- 🔄 **Continuous Batching**: Dynamic batching for optimal resource usage

## Expected Performance:
- **Latency**: ~200-500ms for typical responses
- **Throughput**: ~50-100 tokens/second on H100
- **Concurrent Users**: 5-10 users simultaneously
- **Model Size**: 14B parameters loaded in GPU memory

---

# Summary

This document demonstrates how **KAITO transforms complex OSS model deployment into a simple, declarative experience**. With a single Workspace CRD, you can:

✅ **Deploy enterprise-grade AI models** without months of infrastructure work  
✅ **Build self-hosted chat applications** with complete data privacy  
✅ **Leverage OpenAI-compatible APIs** for seamless integration  
✅ **Scale on Azure H100 GPUs** with optimized performance  
✅ **Maintain full control** over your AI infrastructure and data  

**Key Resources:**
- [KAITO Documentation](https://kaito-project.github.io/kaito/docs/inference/)
- [API Specification](https://github.com/kaito-project/kaito/blob/main/presets/workspace/inference/vllm/api_spec.json)
- [Model Presets](https://github.com/kaito-project/kaito/tree/main/presets)
```