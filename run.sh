#!/usr/bin/env bash

# Run script for Command Snippet Manager
# This script activates the virtual environment and runs the application

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolve virtual environment directory (.venv preferred, fallback to venv)
if [ -d "$SCRIPT_DIR/.venv" ]; then
    VENV_DIR="$SCRIPT_DIR/.venv"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    VENV_DIR="$SCRIPT_DIR/venv"
else
    echo "❌ Virtual environment not found (.venv or venv). Please run setup.sh first."
    exit 1
fi

# Use the virtual environment python directly
VENV_PYTHON="$VENV_DIR/bin/python"

# Check if the virtual environment python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment Python not found at $VENV_PYTHON"
    exit 1
fi

# Run the application using virtual environment python directly
echo "🚀 Starting Command Snippet Manager..."
"$VENV_PYTHON" main.py
