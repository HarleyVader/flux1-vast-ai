#!/bin/bash
# Auto-start script for Flux.1 server on Vast.ai

set -e

echo "=================================="
echo "Flux.1 Server Auto-Start Script"
echo "=================================="
echo

# Check for HF_TOKEN
if [ -z "$HF_TOKEN" ]; then
    echo "❌ ERROR: HF_TOKEN environment variable not set"
    echo
    echo "Please set your HuggingFace token:"
    echo "  export HF_TOKEN='your_token_here'"
    echo
    exit 1
fi

# Install dependencies if needed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt --quiet
fi

# Get public URL
PUBLIC_URL="http://${PUBLIC_IPADDR}:${VAST_TCP_PORT_6006}"

# Start server
echo "🚀 Starting Flux.1 server..."
nohup python3 server.py > server.log 2>&1 &
SERVER_PID=$!

echo "✅ Server started (PID: $SERVER_PID)"
echo

# Wait for server to be ready
echo "⏳ Waiting for server to load models..."
sleep 10

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Server is running!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "🔗 Public URL:"
    echo "   $PUBLIC_URL"
    echo
    echo "📡 API Endpoints:"
    echo "   Health:   $PUBLIC_URL/health"
    echo "   Generate: $PUBLIC_URL/generate"
    echo
    echo "📊 View logs:"
    echo "   tail -f server.log"
    echo
    echo "🛑 Stop server:"
    echo "   kill $SERVER_PID"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "❌ Server failed to start. Check server.log for errors."
    cat server.log
    exit 1
fi
