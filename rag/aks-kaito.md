
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

## Deploy KAITO CRDs  

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


### Verify workspace and ragengine

```bash
k get workspace
k get ragengine
``` 



### API Reference
For complete API documentation: https://kaito-project.github.io/kaito/docs/rag-api




## RAG Operations and Testing - Complete Workflow Summary

### End-to-End RAG Setup

Here's the complete workflow from setup to querying:


#### Prep work 

A sample index file has been generated for testing, using content from blog.srinman.com. Once this index is ingested, the RAG pipeline can retrieve relevant blog information without requiring internet access or direct connectivity to the blog site.  

Start port-forwarding (keep running in separate terminal)   

```bash 
kubectl port-forward svc/ragengine-start 8000:80
``` 



#### Populate RAG with index   


Following command creates index 
```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d @rag_simple_index.json | jq
``` 

#### Verify indexing
```bash 
curl http://localhost:8000/indexes
curl http://localhost:8000/indexes/blog_simple_index/documents  
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



##### Issue a query against simple index - with a totally different search subject
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






##### Delete index   

```bash   
curl http://localhost:8000/indexes

curl -X DELETE http://localhost:8000/indexes/blog_simple_index
```  




### Cleanup  

Delete these two resources as soon as the testing is complete.  GPU nodes are expensive.  In a non-prod env, this practice helps you to keep the cost down.     

```bash
k delete workspace workspace-phi-4-mini-h100
k delete ragengine ragengine-start
``` 


## Resources

- **KAITO Documentation**: https://kaito-project.github.io/kaito/
- **RAG API Reference**: https://kaito-project.github.io/kaito/docs/rag-api
- **Example Cookbook**: https://github.com/kaito-project/kaito-cookbook
- **Blog Source**: https://blog.srinman.com/
- **Blog from AKS Engineering**: https://blog.aks.azure.com/2025/09/12/pair-llmd-and-rag-on-aks  
---

**Built with ❤️ for learning RAG patterns on Azure Kubernetes Service**

```

