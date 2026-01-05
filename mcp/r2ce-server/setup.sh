#!/bin/bash
# Setup script for R2CE MCP Server

set -e

echo "=== Setting up R2CE MCP Server ==="
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To use the MCP server:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the server: python server.py"
echo ""
echo "Or configure it in your MCP client (Cursor/Claude) to run:"
echo "  $(pwd)/venv/bin/python $(pwd)/server.py"

