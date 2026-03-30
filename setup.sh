#!/usr/bin/env bash

# Setup script for Command Snippet Manager
# This script helps set up the virtual environment and install dependencies

set -e

echo "🚀 Setting up Command Snippet Manager..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Pick environment directory:
# - Reuse existing venv if present for backward compatibility
# - Otherwise use .venv as default
if [ -d "venv" ]; then
    VENV_DIR="venv"
elif [ -d ".venv" ]; then
    VENV_DIR=".venv"
else
    VENV_DIR=".venv"
    echo "📦 Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment: source $VENV_DIR/bin/activate"
echo "2. Run the application: python main.py"
echo ""
echo "Or use the run script: ./run.sh"
