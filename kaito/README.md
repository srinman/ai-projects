# KAITO (Kubernetes AI Toolchain Operator) - Complete Guide

## 🚀 Introduction to KAITO

**KAITO** (Kubernetes AI Toolchain Operator) is a Cloud Native Computing Foundation (CNCF) Sandbox project that simplifies the deployment and management of open-source Large Language Models (LLMs) on Kubernetes. It's designed for organizations that want to self-host AI models while maintaining control over their data and reducing per-token API costs.

### What KAITO Addresses

KAITO provides comprehensive solutions across the entire ML lifecycle:

#### 🛠 **Infrastructure Automation**
- **Auto-Provisioning**: On-demand GPU node creation and lifecycle management
- **Resource Optimization**: Intelligent instance selection based on model requirements
- **Cost Management**: Automatic scaling and node deallocation when not in use
- **Multi-Cloud Support**: Azure (production) with AKS add-on, other clouds (coming soon)

#### 🎯 **Inferencing with Open-Source Models**
- **50+ Pre-configured Models**: Phi, Llama, Mistral, Qwen, Falcon families ready to deploy
- **Automatic Optimization**: GPU memory utilization, tensor parallelism, and batching
- **OpenAI Compatibility**: Drop-in replacement for OpenAI API endpoints
- **Production Ready**: Built-in health checks, metrics, and scaling capabilities

#### 🔧 **Fine-Tuning Models**
- **Parameter-Efficient Training**: LoRA, QLoRA, and adapter-based approaches
- **Distributed Training**: Multi-GPU and multi-node training orchestration
- **Custom Dataset Support**: Automated data loading and preprocessing pipelines
- **Experiment Management**: Version control for models, datasets, and training configurations

#### 🔍 **Retrieval-Augmented Generation (RAG) with Your Data**
- **RAGEngine CRD**: Kubernetes-native RAG deployment with vector databases and embedding models
- **Automated Components**: Built-in FAISS vector database and BGE embedding model integration
- **Custom Knowledge Bases**: Index your documents, blogs, wikis, or internal knowledge repositories
- **OpenAI-Compatible API**: Drop-in RAG endpoints that extend LLM responses with your data
- **Production-Ready**: Automatic scaling, persistent storage, and health monitoring
- **Zero-Infrastructure Overhead**: Deploy RAG applications without managing vector databases separately

---

## 📚 Documentation Structure

This repository provides comprehensive guides for different KAITO use cases:

### Core Documentation
- **This Document**: KAITO overview, architecture, and fundamental concepts
- **[Inferencing Guide](../kaito-inferencing/README.md)**: Deploy and serve pre-trained models for real-time inference
- **[RAG Implementation Guide](../kaito-rag/README.md)**: Build Retrieval-Augmented Generation systems with custom data

### What Each Guide Covers

**Inferencing Guide** - Focus on model deployment:
- Deploying 12+ pre-configured models (Phi, Llama, Mistral, etc.) - supported [models](https://github.com/kaito-project/kaito/tree/main/presets/workspace/models)
- OpenAI-compatible API endpoints
- Performance optimization and scaling
- Production monitoring and troubleshooting

**RAG Guide** - Focus on knowledge-enhanced AI:
- RAG pattern fundamentals and architecture
- Crawling and chunking your content
- Building vector indexes from custom data
- Deploying RAGEngine with embedding models
- Interactive chat interfaces for testing

---

### When Self-Hosted Models Make Sense:

**Enterprise Use Cases:**
- **Regulated Industries**: Healthcare, finance, government with strict data governance
- **Proprietary Data**: Training on confidential business data that cannot leave premises
- **Cost Optimization**: High-volume inference where per-token costs become prohibitive
- **Latency Requirements**: Real-time applications needing sub-100ms response times
- **Customization Needs**: Domain-specific fine-tuning for specialized vocabularies
- **Air-Gapped Environments**: Isolated networks without internet connectivity
- **Data Sovereignty**: Legal requirements to keep data within specific geographic regions

**Technical Scenarios:**
- **Batch Processing**: Large-scale document analysis, code generation, or data transformation
- **Edge Deployment**: Running inference on IoT devices or edge computing infrastructure
- **Multi-Modal Applications**: Combining text, image, and audio models in integrated workflows
- **Research & Development**: Experimenting with cutting-edge open-source models

### How KAITO Solves This

KAITO transforms complex infrastructure management into a simple **10-line YAML declaration**:

```yaml
apiVersion: kaito.sh/v1beta1
kind: Workspace
metadata:
  name: my-llm
resource:
  instanceType: "Standard_NC40ads_H100_v5"
inference:
  preset:
    name: phi-4-mini-instruct
```

**That's it!** This simple configuration automatically handles all 10 manual steps listed above.



**References**   
Kaito:  
  https://kaito-project.github.io/kaito/docs/  
vLLM:   
  https://www.youtube.com/watch?v=McLdlg5Gc9s  
  https://www.youtube.com/watch?v=lxjWiVuK5cA   
Steve Griffith:    
  https://www.youtube.com/watch?v=u9rnPE8mpps    
Upstream @AKS with Ernest Wong: 
  https://www.youtube.com/watch?v=ItVNurreU-g  
Kubernetes Bytes Podcast with Sachi and Paul:  
  https://www.youtube.com/watch?v=q83sB1SSALQ

KAITO Architecture:  
https://kaito-project.github.io/kaito/docs/#architecture   

![alt text](image-3.png)
---

## 📋 Prerequisites

### System Requirements
- Azure subscription with GPU VM quota
- Azure CLI version 2.76.0 or later
- kubectl installed and configured
- Basic understanding of Kubernetes concepts

### Supported Configurations
- ✅ **OS**: Ubuntu, CentOS, RHEL (AzureLinux and Windows not supported)
- ✅ **GPU**: NVIDIA GPU VM sizes  
- ✅ **Regions**: All public Azure regions

---

## 🛠️ Step-by-Step Deployment Guide

### Step 1: Environment Setup

First, let's set up our environment variables:

```bash
# Export environment variables
export AZURE_RESOURCE_GROUP="kaito-rg"
export AZURE_LOCATION="eastus2"
export CLUSTER_NAME="kaito-aks"

# Verify Azure CLI login
az account show
```

### Step 2: Create Resource Group

```bash
# Create Azure resource group
az group create \
    --name $AZURE_RESOURCE_GROUP \
    --location $AZURE_LOCATION
```

### Step 3: Create AKS Cluster with KAITO Add-on

```bash
# Create AKS cluster with AI toolchain operator enabled
az aks create \
    --location $AZURE_LOCATION \
    --resource-group $AZURE_RESOURCE_GROUP \
    --name $CLUSTER_NAME \
    --enable-ai-toolchain-operator \
    --enable-oidc-issuer \
    --node-count 1 \
    --generate-ssh-keys \
    --tier standard

# Alternative: Enable on existing cluster
# az aks update \
#     --name $CLUSTER_NAME \
#     --resource-group $AZURE_RESOURCE_GROUP \
#     --enable-ai-toolchain-operator \
#     --enable-oidc-issuer
```

### Step 4: Connect to Your Cluster

```bash
# Configure kubectl
az aks get-credentials \
    --resource-group $AZURE_RESOURCE_GROUP \
    --name $CLUSTER_NAME

# Verify connection
kubectl get nodes
kubectl get pods -n kube-system | grep kaito
```

---

## 🎯 Demo 1: Microsoft Phi-4-Mini Model

This demo deploys the high-performant multimodal Microsoft Phi-4-mini language model.

### Deploy Phi-4-Mini Model

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


```bash
kubectl get workspace workspace-phi-4-mini-h100

# Example output during deployment:
# NAME                        INSTANCE                   RESOURCEREADY   INFERENCEREADY   JOBSTARTED   WORKSPACESUCCEEDED   AGE
# workspace-phi-4-mini-h100   Standard_NC40ads_H100_v5   False           False            False        False                2m
#
# Status meanings:
# - INSTANCE: GPU VM type being provisioned (Standard_NC40ads_H100_v5 = H100 GPU)
# - RESOURCEREADY: True when GPU nodes are provisioned and available
# - INFERENCEREADY: True when model container is running and healthy
# - JOBSTARTED: True when inference workload has started
# - WORKSPACESUCCEEDED: True when everything is ready and serving requests
#
# Deployment progression:
# RESOURCEREADY: False → True (node provisioning complete)
# INFERENCEREADY: False → True (model loaded and container healthy)
# WORKSPACESUCCEEDED: False → True (ready to serve requests)
```

#### What happens during deployment:
1. **Resource Planning**: KAITO analyzes the model requirements (GPU memory, compute)
2. **Node Provisioning**: Automatically creates GPU-enabled nodes if none are available
3. **Image Pulling**: Downloads the pre-built Phi-4-Mini model image (~2-4GB)
4. **Model Loading**: Loads the model into GPU memory using vLLM
5. **Service Creation**: Exposes the model via Kubernetes service with OpenAI-compatible API
6. **Health Checks**: Verifies the model is responding correctly

#### Expected timeline:
- **0-2 minutes**: Workspace creation and validation
- **2-10 minutes**: Node provisioning (if new GPU nodes needed)
- **10-15 minutes**: Container image download and model loading
- **15-20 minutes**: Final health checks and service readiness

### Monitor Deployment

```bash
# Check workspace status (current state)
kubectl describe workspace workspace-phi-4-mini-h100

# Monitor workspace status  
kubectl get workspace workspace-phi-4-mini-h100 

# Check if GPU nodes are being provisioned
kubectl get nodes -o wide

# Check pods status
kubectl get pods -l app=workspace-phi-4-mini-h100

# Check events for troubleshooting
kubectl get events --sort-by=.metadata.creationTimestamp

# Check node provisioning specifically
kubectl get nodes -l kaito.sh/workspace=workspace-phi-4-mini-h100

# Monitor node pool creation (may take 5-10 minutes)
az aks nodepool list --resource-group $AZURE_RESOURCE_GROUP --cluster-name $CLUSTER_NAME -o table
```


![alt text](image.png)
![alt text](image-1.png)   
k logs workspace-phi-4-mini-h100-7f74bf6b6c-nfms8   
![alt text](image-2.png)

![alt text](image-4.png)
#### What's happening now:
1. **Azure is provisioning** a `Standard_NC40ads_H100_v5` VM (H100 GPU)
2. **Node pool creation** in your AKS cluster (5-10 minutes)
3. **Once nodes are ready**, RESOURCEREADY will change to True
4. **Then model container** will be deployed and loaded (5-10 more minutes)

### Test the Model

```bash
# Get service IP for H100 workspace
export SERVICE_IP=$(kubectl get svc workspace-phi-4-mini-h100 -o jsonpath='{.spec.clusterIP}')

# Test with a simple prompt
kubectl run -it --rm --restart=Never curl --image=curlimages/curl -- \
curl -X POST http://$SERVICE_IP/v1/completions \
-H "Content-Type: application/json" \
-d '{
    "model": "phi-4-mini-instruct",
    "prompt": "Explain quantum computing in simple terms",
    "max_tokens": 100
}'

# Test with chat completions API
kubectl run -it --rm --restart=Never curl --image=curlimages/curl -- \
curl -X POST http://$SERVICE_IP/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
    "model": "phi-4-mini-instruct",
    "messages": [
        {
            "role": "user",
            "content": "Write a Python function to calculate fibonacci numbers"
        }
    ],
    "max_tokens": 200
}'
```


### Complete Cleanup



```bash
# Delete all workspaces
kubectl delete workspace --all
k get node 
k describe node <replace-with-gpunode>

# Delete the entire cluster
az aks delete \
    --name $CLUSTER_NAME \
    --resource-group $AZURE_RESOURCE_GROUP \
    --yes --no-wait

# Delete resource group
az group delete \
    --name $AZURE_RESOURCE_GROUP \
    --yes --no-wait
```

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Workspace Not Ready
```bash
# Check quota issues
az vm list-usage --location $AZURE_LOCATION -o table | grep -i gpu

# Request quota increase if needed
# Go to Azure Portal > Subscriptions > Usage + quotas
```

#### 2. Pod Scheduling Issues
```bash
# Check node availability
kubectl describe nodes

# Check resource constraints
kubectl describe workspace workspace-name

```


### Useful Debug Commands

```bash
# Get comprehensive cluster info
kubectl cluster-info dump

# Check KAITO operator logs (correct pod names)
kubectl logs -n kube-system -l app=kaito-workspace


# Verify KAITO CRDs are installed
kubectl get crd | grep kaito

# Check KAITO system pods
kubectl get pods -n kube-system | grep kaito
```

### Note on Pod Names
The KAITO components are named with "kaito" prefix, not "ai-toolchain":
- `kaito-workspace-*` - Main KAITO controller
- `kaito-nvidia-device-plugin-*` - GPU device plugin

---

## 📚 Additional Resources


https://kaito-project.github.io/kaito/docs/quick-start  

### Model Registry
- [KAITO Model Registry](https://github.com/kaito-project/kaito/tree/main/presets)
- [Supported Models List](https://github.com/kaito-project/kaito/blob/main/docs/inference/README.md)

### Official Documentation
- [KAITO GitHub Repository](https://github.com/kaito-project/kaito)
- [Azure AKS AI Toolchain Operator](https://learn.microsoft.com/en-us/azure/aks/ai-toolchain-operator)
- [KAITO Custom Model Deployment](https://learn.microsoft.com/en-us/azure/aks/kaito-custom-inference-model)

### Advanced Topics
- [Fine-tuning Models with KAITO](https://learn.microsoft.com/en-us/azure/aks/ai-toolchain-operator-fine-tune)
- [Monitoring KAITO Workloads](https://learn.microsoft.com/en-us/azure/aks/ai-toolchain-operator-monitoring)
- [Tool Calling with KAITO](https://learn.microsoft.com/en-us/azure/aks/ai-toolchain-operator-tool-calling)

---

## 🏷️ Quick Reference Commands

```bash
# Essential KAITO commands
kubectl get workspace                           # List all workspaces
kubectl describe workspace <name>              # Get workspace details
kubectl logs -l app=<workspace-name>          # View logs
kubectl get svc <workspace-name>              # Get service info
kubectl delete workspace <name>               # Delete workspace

# Cluster management
az aks get-credentials --resource-group $RG --name $CLUSTER  # Connect to cluster
kubectl get nodes                             # List nodes
kubectl top nodes                             # Node resource usage
kubectl get pods --all-namespaces            # All pods in cluster

# GPU monitoring
kubectl describe nodes | grep -A 5 gpu        # GPU availability
nvidia-smi                                     # GPU usage (on nodes)
```

---

## 📝 Notes

- **Deployment Time**: Initial model deployment can take 10-20 minutes depending on model size
- **Resource Requirements**: Ensure adequate GPU quota in your Azure subscription
- **Cost Optimization**: Use appropriate instance types for your workload requirements
- **Security**: KAITO workspaces run within your cluster's security boundary
- **Updates**: KAITO add-on currently supports version 0.6.0

---

*This guide provides comprehensive coverage of KAITO deployment and management. For the latest updates and advanced configurations, refer to the official KAITO documentation.*

---

## 📋 Appendix: KAITO Workspace Lifecycle Analysis

This section documents the complete lifecycle of a KAITO workspace deployment based on actual controller logs from a cluster with KAITO installed. Understanding these events helps with troubleshooting and monitoring deployments.

### Background: Cluster Environment
- **Cluster**: Azure AKS with KAITO add-on enabled
- **Workspace**: `workspace-phi-4-mini-h100` targeting H100 GPU
- **Instance Type**: `Standard_NC40ads_H100_v5`
- **Timeline**: ~7 minutes from creation to model serving

### Phase 1: Controller Initialization (14:17:59)

```
I1023 14:17:59.391345 "starting webhook reconcilers"
2025/10/23 14:17:59 Registering 1 clients
2025/10/23 14:17:59 Registering 2 informer factories
I1023 14:18:01.392389 "starting manager"
2025-10-23T14:18:01Z INFO Starting Controller {"controller": "workspace"}
```

**What's happening:**
- KAITO workspace controller starts up
- Registers event sources for Workspace, NodeClaim, Service, Deployment resources
- Initializes webhook validation and metrics endpoints
- Controller is ready to process workspace requests

### Phase 2: Workspace Creation & Validation (14:21:05)

```
I1023 14:21:05.819205 "Validate creation" workspace="default/workspace-phi-4-mini-h100"
I1023 14:21:05.819242 Inference config not specified. Using default: "inference-params-template"
I1023 14:21:05.925678 "Reconciling" workspace="default/workspace-phi-4-mini-h100"
```

**What's happening:**
- User applies workspace YAML configuration
- KAITO validates the workspace specification
- Applies default inference configuration template
- Adds finalizer for cleanup management
- Begins reconciliation process

### Phase 3: Resource Assessment & Node Provisioning (14:21:06)

```
I1023 14:21:06.197544 "no current nodes match the workspace resource spec"
I1023 14:21:06.197566 "need to create more nodes" NodeCount=1
I1023 14:21:06.347004 "CreateNodeClaim" nodeClaim="default/wsbfbd4f7e7"
I1023 14:21:06.404142 "NodeClaim created successfully" nodeClaim="wsbfbd4f7e7"
```

**What's happening:**
- KAITO scans existing cluster nodes for H100 GPU availability
- No suitable nodes found (no existing `Standard_NC40ads_H100_v5` instances)
- Creates NodeClaim `wsbfbd4f7e7` to request new H100 node from Azure
- Updates workspace status: `ResourceReady=False`, `NodeClaimReady=Unknown`

### Phase 4: Node Provisioning & Initial Timeout (14:21:06 - 14:25:06)

```
I1023 14:21:06.594671 "CheckNodeClaimStatus" nodeClaim="wsbfbd4f7e7"
I1023 14:25:06.741297 "check nodeClaim status timed out. nodeClaim wsbfbd4f7e7 is not ready"
2025-10-23T14:25:06Z ERROR Reconciler error ... "error": "check nodeClaim status timed out"
```

**What's happening:**
- KAITO waits for Azure to provision the H100 VM instance
- Initial timeout after 4 minutes (expected behavior)
- Azure continues provisioning in background
- Controller continues checking status every reconciliation cycle

### Phase 5: Node Ready & Plugin Installation (14:26:26)

```
I1023 14:26:26.886272 "nodeClaim status is ready" nodeClaim="wsbfbd4f7e7"
I1023 14:26:26.886416 "NodeClaimReady" status="True" reason="installNodePluginsSuccess"
I1023 14:26:26.947383 "ResourceReady" status="True" reason="workspaceResourceStatusSuccess"
```

**What's happening:**
- H100 node successfully joins the cluster (~5.5 minutes total)
- KAITO installs GPU drivers and device plugins
- Node labeled with workspace-specific tags
- Workspace status: `ResourceReady=True`, `NodeClaimReady=True`

### Phase 6: Application Deployment (14:26:27)

```
I1023 14:26:27.327435 "CreateService" service="default/workspace-phi-4-mini-h100"
I1023 14:26:27.685407 "CreateDeployment" deployment="default/workspace-phi-4-mini-h100"
```

**What's happening:**
- Creates Kubernetes Service for OpenAI-compatible API endpoints
- Creates Deployment with Phi-4-Mini model container
- Applies resource requests: `nvidia.com/gpu: 1`
- Configures volume mounts for model weights and configuration

### Background: Webhook Configuration Conflicts

```
{"level":"error","ts":"2025-10-23T14:18:09.449Z","logger":"webhook.ValidationWebhook"...
"failed to update webhook: Operation cannot be fulfilled on validatingwebhookconfigurations..."
```

**What's happening:**
- Multiple KAITO components trying to update webhook configurations simultaneously
- Common in Kubernetes environments with multiple controllers
- **These errors are harmless** and don't affect workspace functionality
- Part of eventual consistency model in distributed systems

### Key Timing Observations

| Phase | Duration | Critical Path |
|-------|----------|---------------|
| Controller Startup | ~2 minutes | System initialization |
| Workspace Validation | ~1 second | Input validation |
| NodeClaim Creation | ~1 second | Resource request |
| **Azure H100 Provisioning** | **~5.5 minutes** | **Bottleneck** |
| Service/Deployment Creation | ~1 second | Kubernetes objects |
| **Total (to ResourceReady)** | **~7 minutes** | **End-to-end** |

### Troubleshooting Insights

**Normal Behavior:**
- Initial timeout errors during node provisioning (4-6 minutes)
- Webhook configuration conflicts (harmless background noise)
- Multiple validation events during reconciliation

**Warning Signs:**
- NodeClaim timeout beyond 10 minutes (check quotas)
- Persistent validation failures (check YAML syntax)
- Service/Deployment creation failures (check RBAC)

**Monitoring Commands:**
```bash
# Track workspace progression
kubectl get workspace -w

# Monitor node provisioning
kubectl get nodeclaim

# Check detailed events
kubectl describe workspace <workspace-name>

# View controller logs
kubectl logs -n kube-system -l app=kaito-workspace
```

This lifecycle analysis demonstrates KAITO's robust handling of infrastructure provisioning and application deployment in a cloud-native environment.