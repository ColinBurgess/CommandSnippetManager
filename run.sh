#!/usr/bin/env bash

# Run script for Command Snippet Manager
# This script activates the virtual environment and runs the application

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use the virtual environment python directly
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"

# Check if the virtual environment python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment Python not found at $VENV_PYTHON"
    exit 1
fi

# Run the application using virtual environment python directly
echo "🚀 Starting Command Snippet Manager..."
"$VENV_PYTHON" main.py
