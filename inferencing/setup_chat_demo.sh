#!/bin/bash

# KAITO Phi-4-Mini Chat Demo Setup Script
# This script sets up port-forwarding and launches the chat application

set -e

echo "🚀 KAITO Phi-4-Mini Chat Demo Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if workspace exists and is ready
print_status "Checking KAITO workspace status..."
if ! kubectl get workspace workspace-phi-4-mini-h100 &> /dev/null; then
    print_error "Workspace 'workspace-phi-4-mini-h100' not found!"
    print_status "Please create the workspace first:"
    echo ""
    echo "kubectl apply -f - << EOF"
    echo "apiVersion: kaito.sh/v1beta1"
    echo "kind: Workspace"
    echo "metadata:"
    echo "  name: workspace-phi-4-mini-h100"
    echo "resource:"
    echo "  instanceType: \"Standard_NC40ads_H100_v5\""
    echo "  labelSelector:"
    echo "    matchLabels:"
    echo "      apps: phi-4-h100"
    echo "inference:"
    echo "  preset:"
    echo "    name: phi-4-mini-instruct"
    echo "EOF"
    exit 1
fi

# Check workspace status
WORKSPACE_STATUS=$(kubectl get workspace workspace-phi-4-mini-h100 -o jsonpath='{.status.conditions[?(@.type=="WorkspaceSucceeded")].status}' 2>/dev/null || echo "Unknown")

if [ "$WORKSPACE_STATUS" != "True" ]; then
    print_warning "Workspace is not ready yet. Current status:"
    kubectl get workspace workspace-phi-4-mini-h100
    echo ""
    print_status "Waiting for workspace to be ready..."
    kubectl wait --for=condition=WorkspaceSucceeded workspace/workspace-phi-4-mini-h100 --timeout=600s
fi

print_success "Workspace is ready!"

# Check if service exists
if ! kubectl get svc workspace-phi-4-mini-h100 &> /dev/null; then
    print_error "Service 'workspace-phi-4-mini-h100' not found!"
    exit 1
fi

# Get service cluster IP
CLUSTER_IP=$(kubectl get svc workspace-phi-4-mini-h100 -o jsonpath='{.spec.clusterIP}')
print_status "Service ClusterIP: $CLUSTER_IP"

# Check if port 8080 is already in use
if lsof -i :8080 &> /dev/null; then
    print_warning "Port 8080 is already in use. Checking if it's our port-forward..."
    
    # Try to test the existing connection
    if curl -s http://localhost:8080/v1/models &> /dev/null; then
        print_success "Port-forwarding is already active and working!"
        SKIP_PORT_FORWARD=true
    else
        print_warning "Port 8080 is occupied by another process. Trying port 8081..."
        LOCAL_PORT=8081
    fi
else
    LOCAL_PORT=8080
fi

# Set up port forwarding if not already active
if [ "$SKIP_PORT_FORWARD" != "true" ]; then
    print_status "Setting up port-forwarding on port ${LOCAL_PORT:-8080}..."
    
    # Kill any existing port-forward processes for this service
    pkill -f "kubectl.*port-forward.*workspace-phi-4-mini-h100" || true
    sleep 2
    
    # Start port-forwarding in background
    kubectl port-forward svc/workspace-phi-4-mini-h100 ${LOCAL_PORT:-8080}:80 &
    PORT_FORWARD_PID=$!
    
    # Wait a moment for port-forward to establish
    sleep 3
    
    # Test the connection
    if curl -s http://localhost:${LOCAL_PORT:-8080}/v1/models &> /dev/null; then
        print_success "Port-forwarding established successfully!"
    else
        print_error "Port-forwarding failed to establish connection"
        kill $PORT_FORWARD_PID 2>/dev/null || true
        exit 1
    fi
fi

# Update the Python script if using non-default port
if [ "${LOCAL_PORT}" != "8080" ] && [ "${LOCAL_PORT}" != "" ]; then
    print_status "Updating chat applications to use port ${LOCAL_PORT}..."
    sed -i.bak "s/localhost:8080/localhost:${LOCAL_PORT}/g" phi4_chat_app.py phi4_chat_cli.py
fi

echo ""
print_success "Setup complete! You can now:"
echo ""
echo "1. 🌐 Run the Streamlit web interface:"
echo "   streamlit run phi4_chat_app.py"
echo ""
echo "2. 💻 Run the CLI chat interface:"
echo "   python3 phi4_chat_cli.py"
echo ""
echo "3. 🧪 Test the API directly:"
echo "   curl -X POST http://localhost:${LOCAL_PORT:-8080}/v1/chat/completions \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"model\": \"phi-4-mini-instruct\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello!\"}]}'"
echo ""

if [ "$SKIP_PORT_FORWARD" != "true" ]; then
    echo "📋 Port-forward PID: $PORT_FORWARD_PID"
    echo "   To stop: kill $PORT_FORWARD_PID"
    echo ""
    
    # Setup cleanup trap
    cleanup() {
        print_status "Cleaning up port-forward..."
        kill $PORT_FORWARD_PID 2>/dev/null || true
        exit 0
    }
    
    trap cleanup EXIT INT TERM
    
    print_status "Port-forwarding is running. Press Ctrl+C to stop."
    wait $PORT_FORWARD_PID
fi