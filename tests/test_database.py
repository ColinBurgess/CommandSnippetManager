"""
Tests for the database operations of the Command Snippet Management Application.
"""

import pytest
from datetime import datetime
from db.models import Snippet


def test_database_connection(database):
    """Test database connection and table creation."""
    assert database.connection is not None
    assert database.cursor is not None


def test_insert_snippet(database, sample_snippet_data):
    """Test inserting a snippet into the database."""
    snippet = Snippet(**sample_snippet_data)
    snippet_id = database.insert_snippet(snippet)
    assert snippet_id > 0

    # Verify the snippet was inserted
    retrieved = database.get_snippet_by_id(snippet_id)
    assert retrieved is not None
    assert retrieved.name == sample_snippet_data['name']
    assert retrieved.description == sample_snippet_data['description']
    assert retrieved.command_text == sample_snippet_data['command_text']
    assert retrieved.tags == sample_snippet_data['tags']


def test_insert_duplicate_name_snippets(database):
    """Test inserting multiple snippets with the same name."""
    snippet1 = Snippet(name='Same Name', command_text='cmd1')
    snippet2 = Snippet(name='Same Name', command_text='cmd2')

    id1 = database.insert_snippet(snippet1)
    id2 = database.insert_snippet(snippet2)

    assert id1 != id2

    # Verify both snippets were saved
    s1 = database.get_snippet_by_id(id1)
    s2 = database.get_snippet_by_id(id2)
    assert s1.command_text == 'cmd1'
    assert s2.command_text == 'cmd2'


def test_get_all_snippets(database):
    """Test retrieving all snippets."""
    # Insert multiple snippets
    snippets = [
        Snippet(name='Test 1', command_text='cmd1'),
        Snippet(name='Test 2', command_text='cmd2'),
        Snippet(name='Test 3', command_text='cmd3')
    ]
    for snippet in snippets:
        database.insert_snippet(snippet)

    # Retrieve all snippets
    retrieved = database.get_all_snippets()
    assert len(retrieved) == 3
    assert all(isinstance(s, Snippet) for s in retrieved)


def test_get_snippet_by_id(database, sample_snippet_data):
    """Test retrieving a specific snippet by ID."""
    snippet = Snippet(**sample_snippet_data)
    snippet_id = database.insert_snippet(snippet)

    retrieved = database.get_snippet_by_id(snippet_id)
    assert retrieved is not None
    assert retrieved.id == snippet_id
    assert retrieved.name == sample_snippet_data['name']


def test_get_nonexistent_snippet(database):
    """Test retrieving a snippet that doesn't exist."""
    retrieved = database.get_snippet_by_id(999)
    assert retrieved is None


def test_update_snippet(database, sample_snippet_data):
    """Test updating an existing snippet."""
    # Insert initial snippet
    snippet = Snippet(**sample_snippet_data)
    snippet_id = database.insert_snippet(snippet)

    # Update the snippet
    updated_snippet = Snippet(
        snippet_id=snippet_id,
        name='Updated Name',
        description='Updated description',
        command_text='updated command',
        tags='updated, tags'
    )
    success = database.update_snippet(updated_snippet)
    assert success is True

    # Verify the update
    retrieved = database.get_snippet_by_id(snippet_id)
    assert retrieved.name == 'Updated Name'
    assert retrieved.description == 'Updated description'
    assert retrieved.command_text == 'updated command'
    assert retrieved.tags == 'updated, tags'


def test_delete_snippet(database, sample_snippet_data):
    """Test deleting a snippet."""
    # Insert a snippet
    snippet = Snippet(**sample_snippet_data)
    snippet_id = database.insert_snippet(snippet)

    # Delete the snippet
    success = database.delete_snippet(snippet_id)
    assert success is True

    # Verify the deletion
    retrieved = database.get_snippet_by_id(snippet_id)
    assert retrieved is None


def test_delete_nonexistent_snippet(database):
    """Test deleting a snippet that doesn't exist."""
    success = database.delete_snippet(999)
    assert success is True  # SQLite doesn't error on deleting non-existent rows


def test_search_snippets(database):
    """Test searching for snippets."""
    # Insert test snippets
    snippets = [
        Snippet(name='Test Python', command_text='python script.py', tags='python, script'),
        Snippet(name='Test Git', command_text='git commit', tags='git, vcs'),
        Snippet(name='Python Debug', command_text='python -m pdb', tags='python, debug')
    ]
    for snippet in snippets:
        database.insert_snippet(snippet)

    # Search by term
    python_results = database.search_snippets('python')
    assert len(python_results) == 2

    # Search by tag
    git_results = database.search_snippets(tags_list=['git'])
    assert len(git_results) == 1
    assert git_results[0].name == 'Test Git'


def test_name_exists(database):
    """Test checking if a snippet name exists."""
    snippet = Snippet(name='Unique Name', command_text='test')
    snippet_id = database.insert_snippet(snippet)

    # Check existing name
    assert database.name_exists('Unique Name') is True

    # Check non-existent name
    assert database.name_exists('Non-existent Name') is False

    # Check with exclude_id
    assert database.name_exists('Unique Name', exclude_id=snippet_id) is False


def test_update_last_used(database, sample_snippet_data):
    """Test updating the last_used timestamp."""
    # Insert a snippet
    snippet = Snippet(**sample_snippet_data)
    snippet_id = database.insert_snippet(snippet)

    # Get initial last_used time
    initial = database.get_snippet_by_id(snippet_id).last_used

    # Wait a moment to ensure timestamp will be different
    import time
    time.sleep(0.1)

    # Update last_used
    success = database.update_last_used(snippet_id)
    assert success is True

    # Verify the update
    updated = database.get_snippet_by_id(snippet_id).last_used
    assert updated > initial
