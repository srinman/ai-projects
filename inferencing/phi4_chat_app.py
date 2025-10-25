#!/usr/bin/env python3
"""
Simple Chat Application for KAITO Phi-4-Mini Inference
Connects to KAITO workspace via port-forwarding
"""

import requests
import json
import streamlit as st
import time
from datetime import datetime
import os

# Configuration
KAITO_API_URL = "http://localhost:8080/v1/chat/completions"
MODEL_NAME = "phi-4-mini-instruct"

def call_kaito_inference(messages, max_tokens=500, temperature=0.7):
    """
    Call the KAITO inference API
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            KAITO_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to KAITO service. Make sure port-forwarding is active!")
        st.code("kubectl port-forward svc/workspace-phi-4-mini-h100 8080:80")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The model might be loading.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"🔥 Request failed: {str(e)}")
        return None

def check_service_health():
    """
    Check if the KAITO service is accessible
    """
    try:
        # Try to get model info
        health_url = "http://localhost:8080/v1/models"
        response = requests.get(health_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    st.set_page_config(
        page_title="KAITO Phi-4-Mini Chat",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 KAITO Phi-4-Mini Chat Interface")
    st.markdown("### Powered by Microsoft Phi-4-Mini on Azure H100 GPU")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Service status check
        if check_service_health():
            st.success("✅ KAITO Service Connected")
        else:
            st.error("❌ KAITO Service Disconnected")
            st.markdown("**Setup port-forwarding:**")
            st.code("kubectl port-forward svc/workspace-phi-4-mini-h100 8080:80")
        
        st.divider()
        
        # Model parameters
        max_tokens = st.slider("Max Tokens", 50, 1000, 500)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        st.divider()
        
        # System prompt
        system_prompt = st.text_area(
            "System Prompt",
            value="You are a helpful AI assistant that provides clear and concise answers.",
            height=100
        )
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "timestamp" in message:
                    st.caption(f"🕐 {message['timestamp']}")
    
    # Chat input
    if prompt := st.chat_input("Ask Phi-4-Mini anything..."):
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"🕐 {timestamp}")
        
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
            with st.spinner("🤔 Phi-4-Mini is thinking..."):
                response = call_kaito_inference(
                    messages=api_messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            
            if response and "choices" in response:
                assistant_message = response["choices"][0]["message"]["content"]
                st.markdown(assistant_message)
                
                # Show response metadata
                if "usage" in response:
                    usage = response["usage"]
                    response_time = datetime.now().strftime("%H:%M:%S")
                    st.caption(f"🕐 {response_time} | 📊 Tokens: {usage.get('total_tokens', 'N/A')} | ⚡ Prompt: {usage.get('prompt_tokens', 'N/A')} | 🎯 Completion: {usage.get('completion_tokens', 'N/A')}")
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "timestamp": response_time
                })
            else:
                st.error("Failed to get response from KAITO service")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **About this demo:**
    - Model: Microsoft Phi-4-Mini Instruct
    - Infrastructure: Azure AKS + KAITO + H100 GPU
    - Framework: vLLM for high-performance inference
    - API: OpenAI-compatible endpoints
    """)

if __name__ == "__main__":
    main()