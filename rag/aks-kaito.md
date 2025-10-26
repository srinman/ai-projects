
# Building RAG Applications with KAITO on Azure Kubernetes Service

## Introduction to Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) is a powerful AI pattern that combines the capabilities of Large Language Models (LLMs) with external knowledge sources to provide more accurate, contextual, and up-to-date responses. Instead of relying solely on the model's training data, RAG systems dynamically retrieve relevant information from knowledge bases, databases, or document collections to enhance the quality of generated responses.

### How RAG Works

The RAG pattern operates through several key components:

1. **Knowledge Base**: A collection of documents, articles, or data that serves as the external knowledge source
2. **Vector Database**: Stores document embeddings that enable semantic similarity search
3. **Embedding Model**: Converts text into high-dimensional vectors for similarity matching
4. **Retrieval System**: Searches the vector database for relevant context based on user queries
5. **Language Model**: Generates responses using both the original query and retrieved context

### Benefits of RAG

- **Accuracy**: Provides factual, source-backed responses instead of potentially hallucinated content
- **Currency**: Access to up-to-date information beyond the model's training cutoff
- **Transparency**: Responses can be traced back to specific source documents
- **Domain Expertise**: Enables specialized knowledge without requiring model retraining
- **Cost Efficiency**: Avoids the expense of fine-tuning large models for specific domains

### RAG vs Traditional Approaches

| Approach | Training Data | Knowledge Updates | Transparency | Cost |
|----------|---------------|-------------------|--------------|------|
| **Traditional LLM** | Static training set | Requires retraining | Limited | High for updates |
| **RAG System** | Base model + External sources | Real-time updates | High (source citations) | Low for updates |
| **Fine-tuning** | Custom training data | Requires retraining | Medium | Very high |

## KAITO RAGEngine on Azure Kubernetes Service

KAITO (Kubernetes AI Toolchain Operator) simplifies the deployment of RAG applications on Azure Kubernetes Service (AKS) by providing:

- **Automated Infrastructure**: Handles GPU nodes, storage, and networking automatically
- **Pre-built Components**: Includes vector databases, embedding models, and inference services
- **Kubernetes-Native**: Leverages CRDs for declarative RAG application management
- **Scalability**: Auto-scaling based on demand with Azure's GPU instances

---

## Prerequisites and Setup

### Install KAITO RAGEngine Helm Chart

```bash 
helm repo add kaito https://kaito-project.github.io/kaito/charts/kaito
helm repo update
helm upgrade --install kaito-ragengine kaito/ragengine \
  --namespace kaito-ragengine \
  --create-namespace
``` 

### Verify Installation

```bash
helm list -n kaito-ragengine
kubectl describe deploy kaito-ragengine -n kaito-ragengine
```

## Deploy KAITO Workspace for Inference

### Deploy Phi-4-Mini Workspace with H100 GPU

### Deploy Phi-4-Mini Workspace with H100 GPU

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

## Deploy RAGEngine Instance

### Create RAGEngine with BGE Embedding Model

```bash 
kubectl apply -f - << EOF
apiVersion: kaito.sh/v1alpha1
kind: RAGEngine
metadata:
  name: ragengine-start
spec:
  compute:
    instanceType: "Standard_D8s_v6"
    labelSelector:
      matchLabels:
        apps: rag-demo
  embedding:
    local:
      modelID: "BAAI/bge-small-en-v1.5"
  inferenceService:
    url: "http://workspace-phi-4-mini-h100/v1/completions"
    contextWindowSize: 8192
EOF
```

## Access RAGEngine Service

### Port Forward to Local Machine

```bash
kubectl port-forward svc/ragengine-start 8000:80
```

## RAG Operations and Testing

### API Reference
For complete API documentation: https://kaito-project.github.io/kaito/docs/rag-api

### Index Your Data

```bash
# Build index from rag_index.json
curl -X POST http://localhost:8000/index \
-H "Content-Type: application/json" \
-d @rag_index.json | jq
```

### Verify Index Creation

```bash
# Check available indexes
curl  http://localhost:8000/indexes

# List documents in blog_index
curl  http://localhost:8000/indexes/blog_index/documents | jq
```

### Query with RAG (Retrieval-Augmented) 

### Query with RAG (Retrieval-Augmented)

```bash
# Query with index_name for RAG-enhanced responses
curl -X POST http://localhost:8000/v1/chat/completions \
 -H "Content-Type: application/json" \
 -d '{
    "index_name": "blog_index",
    "model": "phi-4-mini-instruct",
    "messages": [
      {
        "role": "user",
        "content": "really confused with options in Azure for containerized apps. Can you suggest a blog?"
      }
    ], "max_tokens": 100
   }' | jq -r '.choices[0].message.content'
```

### Query without RAG (Direct LLM)

```bash
# Query without index_name for standard LLM responses
curl -X POST http://localhost:8000/v1/chat/completions \
 -H "Content-Type: application/json" \
 -d '{
    "model": "phi-4-mini-instruct",
    "messages": [
      {
        "role": "user",
        "content": "really confused with options in Azure for containerized apps. Can you suggest a blog?"
      }
    ], "max_tokens": 100
   }' | jq -r '.choices[0].message.content'
```

---

## RAG Chat Interface

For an interactive web interface to test RAG capabilities, use the provided Streamlit application.

### Prerequisites
- Ensure RAGEngine port-forwarding is running: `kubectl port-forward svc/ragengine-start 8000:80`
- Install required Python packages: `pip install streamlit requests`

### Run the RAG Chat Application

```bash
# Navigate to the rag directory
cd /home/srinman/git/ai-projects/rag

# Run the Streamlit app
streamlit run rag_chat_app.py
```

**Note**: The application will be available at `http://localhost:8501` in your browser.

### Troubleshooting

If you encounter an `AttributeError: 'NoneType' object has no attribute 'get'` error, this typically means:

1. **RAGEngine service not running**: Ensure port-forwarding is active
2. **API response format issues**: The RAGEngine might return incomplete responses during startup
3. **Network connectivity**: Check if the service is accessible at `http://localhost:8000`

The application includes robust error handling for these scenarios and will display appropriate error messages.

### Features

The RAG chat interface provides:

- **RAG Toggle**: Switch between RAG-enhanced responses and direct LLM queries
- **Real-time Index Status**: Shows available indexes and document counts
- **Source Citations**: Displays retrieved sources with relevance scores
- **Example Queries**: Pre-built questions about AKS, containers, and cloud technologies
- **Response Metadata**: Token usage and timing information
- **Interactive Chat**: Full conversation history with timestamps

### RAG vs Direct LLM Comparison

Use the toggle to compare responses:

- **🔍 RAG Mode**: Responses enhanced with context from your blog index
- **🚫 Direct LLM Mode**: Standard responses using only the base model's training data

This allows you to see the difference in accuracy and relevance when external knowledge is used versus relying solely on the model's training data.

```

