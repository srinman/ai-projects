#!/usr/bin/env python3
"""
RAG Chat Application for KAITO RAGEngine
Connects to KAITO RAGEngine via port-forwarding for Retrieval-Augmented Generation
"""

import requests
import json
import streamlit as st
import time
from datetime import datetime
import os

# Configuration
RAG_API_URL = "http://localhost:8000/v1/chat/completions"
INDEX_API_URL = "http://localhost:8000/indexes"
MODEL_NAME = "phi-4-mini-instruct"
INDEX_NAME = "blog_index"

def call_rag_inference(messages, max_tokens=500, temperature=0.7, use_rag=True):
    """
    Call the KAITO RAGEngine API with or without RAG
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }
    
    # Add index_name for RAG-enabled queries
    if use_rag:
        payload["index_name"] = INDEX_NAME
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            RAG_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to RAGEngine service. Make sure port-forwarding is active!")
        st.code("kubectl port-forward svc/ragengine-start 8000:80")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The model might be loading or processing embeddings.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"🔥 Request failed: {str(e)}")
        return None

def check_service_health():
    """
    Check if the RAGEngine service is accessible
    """
    try:
        response = requests.get(INDEX_API_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_available_indexes():
    """
    Get list of available indexes
    """
    try:
        response = requests.get(INDEX_API_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_index_documents(index_name):
    """
    Get documents in a specific index
    """
    try:
        response = requests.get(f"{INDEX_API_URL}/{index_name}/documents", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def main():
    st.set_page_config(
        page_title="KAITO RAG Chat",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 KAITO RAG Chat Interface")
    st.markdown("### Retrieval-Augmented Generation with Phi-4-Mini on Azure H100 GPU")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ RAG Configuration")
        
        # Service status check
        if check_service_health():
            st.success("✅ RAGEngine Service Connected")
            
            # Show available indexes
            indexes = get_available_indexes()
            if indexes:
                st.info(f"📚 Available Indexes: {', '.join(indexes)}")
                
                # Show document count for blog_index
                if INDEX_NAME in indexes:
                    docs = get_index_documents(INDEX_NAME)
                    st.info(f"📄 Documents in {INDEX_NAME}: {len(docs)}")
            else:
                st.warning("📭 No indexes found")
        else:
            st.error("❌ RAGEngine Service Disconnected")
            st.markdown("**Setup port-forwarding:**")
            st.code("kubectl port-forward svc/ragengine-start 8000:80")
        
        st.divider()
        
        # RAG toggle
        use_rag = st.toggle("🔍 Enable RAG", value=True, help="Use Retrieval-Augmented Generation")
        
        if use_rag:
            st.info("🔍 **RAG Mode**: Queries will be enhanced with retrieved context from your blog index")
        else:
            st.warning("🚫 **Direct LLM Mode**: Queries will use only the base model without external knowledge")
        
        st.divider()
        
        # Model parameters
        max_tokens = st.slider("Max Tokens", 50, 1000, 500)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        st.divider()
        
        # System prompt
        if use_rag:
            default_prompt = "You are a helpful AI assistant that answers questions using the provided context from Sridher Manivel's blog. Always cite sources when available and provide direct links to relevant blog posts."
        else:
            default_prompt = "You are a helpful AI assistant that provides clear and concise answers about cloud technologies and containerization."
            
        system_prompt = st.text_area(
            "System Prompt",
            value=default_prompt,
            height=120
        )
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        # Example queries
        st.header("💡 Example Queries")
        if st.button("Ask about AKS scaling"):
            st.session_state.example_query = "How do I scale AKS clusters effectively?"
        if st.button("Container Apps vs AKS"):
            st.session_state.example_query = "What are the differences between AKS and Azure Container Apps?"
        if st.button("Workload Identity"):
            st.session_state.example_query = "How does AKS workload identity work in practice?"
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Handle example queries
    if "example_query" in st.session_state:
        prompt = st.session_state.example_query
        del st.session_state.example_query
        
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": timestamp,
            "rag_enabled": use_rag
        })
        
        # Process the query
        process_query(prompt, system_prompt, max_tokens, temperature, use_rag)
        st.rerun()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show metadata
                metadata_parts = [f"🕐 {message.get('timestamp', 'N/A')}"]
                if message["role"] == "user" and "rag_enabled" in message:
                    if message["rag_enabled"]:
                        metadata_parts.append("🔍 RAG")
                    else:
                        metadata_parts.append("🚫 Direct LLM")
                elif message["role"] == "assistant" and "usage" in message and message["usage"]:
                    usage = message["usage"]
                    if usage is not None and isinstance(usage, dict):
                        metadata_parts.append(f"📊 Tokens: {usage.get('total_tokens', 'N/A')}")
                
                st.caption(" | ".join(metadata_parts))
                
                # Show sources if available
                if "sources" in message and message["sources"]:
                    with st.expander("📚 Sources"):
                        for source in message["sources"]:
                            st.markdown(f"- **{source.get('title', 'Unknown')}** - Score: {source.get('score', 'N/A')}")
                            if 'url' in source:
                                st.markdown(f"  🔗 [{source['url']}]({source['url']})")
    
    # Chat input
    if prompt := st.chat_input("Ask about cloud technologies, AKS, containers..."):
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": timestamp,
            "rag_enabled": use_rag
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            metadata = f"🕐 {timestamp}"
            if use_rag:
                metadata += " | 🔍 RAG"
            else:
                metadata += " | 🚫 Direct LLM"
            st.caption(metadata)
        
        # Process the query
        process_query(prompt, system_prompt, max_tokens, temperature, use_rag)

def process_query(prompt, system_prompt, max_tokens, temperature, use_rag):
    """
    Process user query and generate response
    """
    # Prepare messages for API call
    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"]:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Processing... (RAG retrieval + generation)" if use_rag else "🤔 Phi-4-Mini is thinking..."):
            response = call_rag_inference(
                messages=api_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                use_rag=use_rag
            )
        
        if response and "choices" in response:
            assistant_message = response["choices"][0]["message"]["content"]
            st.markdown(assistant_message)
            
            # Show response metadata
            response_time = datetime.now().strftime("%H:%M:%S")
            metadata_parts = [f"🕐 {response_time}"]
            
            if "usage" in response and response["usage"]:
                usage = response["usage"]
                if usage is not None and isinstance(usage, dict):
                    metadata_parts.append(f"📊 Tokens: {usage.get('total_tokens', 'N/A')}")
                    metadata_parts.append(f"⚡ Prompt: {usage.get('prompt_tokens', 'N/A')}")
                    metadata_parts.append(f"🎯 Completion: {usage.get('completion_tokens', 'N/A')}")
            
            st.caption(" | ".join(metadata_parts))
            
            # Extract and show sources if available in response
            sources = []
            if "source_nodes" in response:
                for node in response["source_nodes"]:
                    source_info = {
                        "title": node.get("metadata", {}).get("title", "Unknown"),
                        "score": node.get("score", 0),
                        "url": node.get("metadata", {}).get("url", "")
                    }
                    sources.append(source_info)
            
            if sources:
                with st.expander("📚 Retrieved Sources"):
                    for source in sources:
                        st.markdown(f"- **{source['title']}** - Relevance Score: {source['score']:.3f}")
                        if source['url']:
                            st.markdown(f"  🔗 [{source['url']}]({source['url']})")
            
            # Add assistant response to chat history
            usage_data = {}
            if "usage" in response and response["usage"] and isinstance(response["usage"], dict):
                usage_data = response["usage"]
            
            assistant_response_data = {
                "role": "assistant",
                "content": assistant_message,
                "timestamp": response_time,
                "usage": usage_data,
                "sources": sources
            }
            st.session_state.messages.append(assistant_response_data)
        else:
            st.error("Failed to get response from RAGEngine service")
    
    # Footer
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **RAG System Components:**
        - 🔍 Vector DB: Faiss
        - 📊 Embeddings: BGE-small-en-v1.5
        - 🤖 LLM: Microsoft Phi-4-Mini
        - 🎯 Knowledge: Sridher's Blog
        """)
    
    with col2:
        st.markdown("""
        **Infrastructure:**
        - ☁️ Platform: Azure AKS + KAITO
        - 🔥 GPU: H100 (Inference) + D8s_v6 (RAG)
        - 🚀 Framework: vLLM + RAGEngine
        - 🌐 API: OpenAI-compatible
        """)

if __name__ == "__main__":
    main()