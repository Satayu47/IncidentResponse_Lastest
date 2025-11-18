#!/bin/bash
# OPA Server Setup Script for Linux/Mac
# This script sets up and starts the OPA server with policies

echo "=== OPA Server Setup ==="

# Check if Docker is running
echo -e "\n[1/4] Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo "✗ Docker is not running. Please start Docker first."
    exit 1
fi
echo "✓ Docker is running"

# Stop existing OPA container if running
echo -e "\n[2/4] Stopping existing OPA container (if any)..."
docker stop opa-server 2>/dev/null
docker rm opa-server 2>/dev/null

# Start OPA server
echo -e "\n[3/4] Starting OPA server..."
OPA_CONTAINER=$(docker run -d \
    --name opa-server \
    -p 8181:8181 \
    openpolicyagent/opa run --server --log-level=info)

if [ $? -eq 0 ]; then
    echo "✓ OPA server started (container: $OPA_CONTAINER)"
else
    echo "✗ Failed to start OPA server"
    exit 1
fi

# Wait for server to be ready
echo -e "\nWaiting for OPA server to be ready..."
sleep 3

# Load policies
echo -e "\n[4/4] Loading policies..."

POLICIES_DIR="$(dirname "$0")/../phase2_engine/policies"
if [ ! -d "$POLICIES_DIR" ]; then
    echo "✗ Policies directory not found: $POLICIES_DIR"
    exit 1
fi

# Load playbook policy
PLAYBOOK_POLICY="$POLICIES_DIR/playbook.rego"
if [ -f "$PLAYBOOK_POLICY" ]; then
    echo "  Loading playbook.rego..."
    curl -X PUT "http://localhost:8181/v1/policies/playbook" \
        --data-binary @"$PLAYBOOK_POLICY" \
        -H "Content-Type: text/plain" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ playbook.rego loaded"
    else
        echo "  ⚠ Could not load playbook.rego (server may need more time)"
    fi
fi

# Load incident policy
INCIDENT_POLICY="$POLICIES_DIR/incident.rego"
if [ -f "$INCIDENT_POLICY" ]; then
    echo "  Loading incident.rego..."
    curl -X PUT "http://localhost:8181/v1/policies/incident" \
        --data-binary @"$INCIDENT_POLICY" \
        -H "Content-Type: text/plain" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ incident.rego loaded"
    else
        echo "  ⚠ Could not load incident.rego (server may need more time)"
    fi
fi

# Test OPA server
echo -e "\n[5/5] Testing OPA server..."
if curl -s http://localhost:8181/health > /dev/null; then
    echo "✓ OPA server is healthy"
else
    echo "⚠ OPA server may not be fully ready yet"
fi

echo -e "\n=== Setup Complete ==="
echo "OPA Server URL: http://localhost:8181"
echo "Playbook Policy: http://localhost:8181/v1/data/playbook/allow"
echo "Incident Policy: http://localhost:8181/v1/data/incident/result"
echo -e "\nTo stop OPA: docker stop opa-server"
echo "To view logs: docker logs opa-server"

