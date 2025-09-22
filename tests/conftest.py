"""
Test configuration and fixtures for the Command Snippet Management Application.
"""

import os
import tempfile
import pytest
from db.database import Database
from core.snippet_manager import SnippetManager


@pytest.fixture
def temp_db_path():
    """Create a temporary database file for testing."""
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.unlink(path)


@pytest.fixture
def database(temp_db_path):
    """Create a test database instance."""
    db = Database(temp_db_path)
    db.connect()
    db.create_tables()
    yield db
    db.close()


@pytest.fixture
def snippet_manager(database):
    """Create a test snippet manager instance."""
    return SnippetManager(database)


@pytest.fixture
def sample_snippet_data():
    """Return sample data for creating a snippet."""
    return {
        'name': 'Test Snippet',
        'description': 'A test snippet for unit testing',
        'command_text': 'echo "test command"',
        'tags': 'test, unit-test'
    }
