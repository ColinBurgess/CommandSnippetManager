"""
Configuration settings for the Command Snippet Management Application.
"""

import os

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "snippets.db")

# Application configuration
APP_NAME = "Command Snippet Manager"
APP_VERSION = "1.0.0"
