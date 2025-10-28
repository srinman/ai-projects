
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

You can apply workspace and ragengine one after the other - don't need to wait for workspace to complete before applying ragengine    


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


## Verify workspace and ragengine

```bash
k get workspace
k get ragengine
``` 

## Access RAGEngine Service

### Port Forward to Local Machine

```bash
kubectl port-forward svc/ragengine-start 8000:80
```

## RAG Operations and Testing

### Building Your Own RAG Index

For production RAG systems, you should crawl actual blog content and chunk it appropriately. Use the provided `build_rag_index.py` program:

```bash
# Install dependencies
pip install requests beautifulsoup4

# Build index from blog.srinman.com
python build_rag_index.py

# This will create: rag_blog_chunked_index.json
```

**What the builder does:**
1. Crawls all blog posts from blog.srinman.com
2. Extracts clean text content
3. Chunks content into ~300 word sections with overlap
4. Adds metadata (author, category, URL, section)
5. Creates RAGEngine-compatible JSON index

**Index Quality Benefits:**
- ✅ Full blog content (not just titles)
- ✅ Semantic chunking (paragraph boundaries)
- ✅ Rich context for embeddings
- ✅ Better retrieval accuracy

See `RAG_INDEX_README.md` for detailed documentation on the RAG pattern and program usage.

### API Reference
For complete API documentation: https://kaito-project.github.io/kaito/docs/rag-api

### Index Your Data

```bash
# Build index from rag_index.json (simple version)
curl -X POST http://localhost:8000/index \
-H "Content-Type: application/json" \
-d @rag_index.json | jq

# OR build from crawled content (recommended)
curl -X POST http://localhost:8000/index \
-H "Content-Type: application/json" \
-d @rag_blog_chunked_index.json | jq
```

### Verify Index Creation

```bash
# Check available indexes
curl  http://localhost:8000/indexes

# List documents in blog_index
curl  http://localhost:8000/indexes/blog_index/documents | jq
```

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


## Complete Workflow Summary

### End-to-End RAG Setup

Here's the complete workflow from setup to querying:


#### Prep work 

```bash
# 1. Prerequisites (one-time setup)
pip install streamlit requests beautifulsoup4

# 2. Build your RAG index (from actual blog content)
python build_rag_index.py
# Output: rag_blog_chunked_index.json
``` 

Start port-forwarding (keep running in separate terminal)   

```bash 
kubectl port-forward svc/ragengine-start 8000:80
``` 

#### Verify indexing
```bash 
curl http://localhost:8000/indexes
curl http://localhost:8000/indexes/blog_index/documents  
``` 


#### Populate RAG with index  (two indexes - one simple and another with all the chunks)    

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d @rag_blog_chunked_index.json | jq

curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d @rag_simple_index.json | jq
``` 

#### Verify indexing
```bash 
curl http://localhost:8000/indexes
curl http://localhost:8000/indexes/blog_index/documents  
```


#### Verify Query with RAG index   

https://kaito-project.github.io/kaito/docs/rag-api#query-index 


##### Issue a query against simple index   
```bash 
curl -s http://localhost:8000/query \
-X POST \
-H "Content-Type: application/json" \
-d '{
  "index_name": "blog_simple_index",
  "model": "phi-4-mini-instruct",
  "query": "blog about container apps",
  "top_k": 1,
  "llm_params": {
    "temperature": 0.7,
    "max_tokens": 2048
  }
}' | jq
```

##### Issue a query against simple index   

```bash 
curl -s http://localhost:8000/query \
-X POST \
-H "Content-Type: application/json" \
-d '{
  "index_name": "blog_chunked_index",
  "model": "phi-4-mini-instruct",
  "query": "blog about container apps",
  "top_k": 1,
  "llm_params": {
    "temperature": 0.7,
    "max_tokens": 2048
  }
}' | jq
``` 


##### Issue a query against simple index   
```bash 
curl -s http://localhost:8000/query \
-X POST \
-H "Content-Type: application/json" \
-d '{
  "index_name": "blog_simple_index",
  "model": "phi-4-mini-instruct",
  "query": "solar",
  "top_k": 1,
  "llm_params": {
    "temperature": 0.7,
    "max_tokens": 2048
  }
}' | jq
```


##### Issue a query against simple index   
```bash 
curl -s http://localhost:8000/query \
-X POST \
-H "Content-Type: application/json" \
-d '{
  "index_name": "blog_simple_index",
  "model": "phi-4-mini-instruct",
  "query": "what is rag",
  "top_k": 2,
  "llm_params": {
    "temperature": 0.3,
    "max_tokens": 2048
  }
}' | jq
```

##### Issue a chat completion against simple index    

```bash
# Query with index_name for RAG-enhanced responses
curl -X POST http://localhost:8000/v1/chat/completions \
 -H "Content-Type: application/json" \
 -d '{
    "index_name": "blog_simple_index",
    "model": "phi-4-mini-instruct",
    "messages": [
      {
        "role": "user",
        "content": "really confused with options in Azure for containerized apps. Can you suggest a blog?"
      }
    ], "max_tokens": 100
   }' | jq -r '.choices[0].message.content'
```




##### Issue a chat completion against simple index    

```bash   
curl http://localhost:8000/indexes

curl -X DELETE http://localhost:8000/indexes/blog_index
curl -X DELETE http://localhost:8000/indexes/blog_simple_index
```  


# 7. Test with UI
```bash 
streamlit run rag_chat_app.py
```



### Cleanup  

Delete these two resources as soon as the testing is complete.  GPU nodes are expensive.  In a non-prod env, this practice helps you to keep the cost down.     

```bash
k delete workspace workspace-phi-4-mini-h100
k delete ragengine ragengine-start
``` 


### Resources

- **KAITO Documentation**: https://kaito-project.github.io/kaito/
- **RAG API Reference**: https://kaito-project.github.io/kaito/docs/rag-api
- **Example Cookbook**: https://github.com/kaito-project/kaito-cookbook
- **Blog Source**: https://blog.srinman.com/

---

**Built with ❤️ for learning RAG patterns on Azure Kubernetes Service**

```

