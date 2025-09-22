#!/usr/bin/env bash

# Run script for Command Snippet Manager
# This script activates the virtual environment and runs the application

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the application
echo "🚀 Starting Command Snippet Manager..."
python main.py
