#!/bin/bash

# FloatChat Data Explorer Launcher
# This script activates the virtual environment and launches the macOS-inspired glassmorphism dashboard

# Kill any existing research_dashboard processes
echo "🛑 Stopping any existing FloatChat servers..."
pkill -f research_dashboard 2>/dev/null || true
echo "✅ Cleared previous instances"
echo ""

echo "🚀 Launching FloatChat ARGO Data Explorer..."
echo "🌊 Advanced Oceanographic Data Visualization Platform with Glassmorphism UI"
echo ""

echo "📋 Access URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💻 Local Computer:"
echo "   • http://localhost:8053"
echo "   • http://127.0.0.1:8053"
echo ""

# Get network IP address (macOS compatible)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    NETWORK_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
else
    # Linux
    NETWORK_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "")
fi

if [ -n "$NETWORK_IP" ]; then
    echo "📡 Local Network (other devices on same WiFi):"
    echo "   • http://$NETWORK_IP:8053"
    echo ""
    echo "📱 Share this link with colleagues: http://$NETWORK_IP:8053"
else
    echo "📡 Network access: Check your IP with 'ifconfig' (macOS) or 'hostname -I' (Linux)"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚡ Features Ready:"
echo "   • 🗺️ Interactive ARGO Float Map with Glass Controls"
echo "   • 🔍 Smart Search & AI Chat with Tab Highlighting"
echo "   • 📊 Real-time Oceanographic Analysis & New Analysis Tab"
echo "   • 🎨 macOS Glassmorphism UI with Smooth Animations"
echo "   • 🤖 LLM-Powered Ocean Science Research Assistant"
echo ""
echo "⏳ Starting server... (Press Ctrl+C to stop)"
echo ""

# Activate virtual environment
source venv/bin/activate

# Launch the dashboard with python3
python3 dash_frontend/research_dashboard.py
