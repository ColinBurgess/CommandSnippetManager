"""
Tests for the business logic layer of the Command Snippet Management Application.
"""

import pytest
from datetime import datetime
from db.models import Snippet


def test_add_snippet(snippet_manager, sample_snippet_data):
    """Test adding a new snippet."""
    snippet_id = snippet_manager.add_snippet(**sample_snippet_data)
    assert snippet_id > 0

    # Verify the snippet was added
    snippet = snippet_manager.get_snippet_details(snippet_id)
    assert snippet.name == sample_snippet_data['name']
    assert snippet.description == sample_snippet_data['description']
    assert snippet.command_text == sample_snippet_data['command_text']
    assert snippet.tags == sample_snippet_data['tags']


def test_add_snippet_empty_name(snippet_manager):
    """Test adding a snippet with empty name."""
    with pytest.raises(ValueError, match="Snippet name cannot be empty"):
        snippet_manager.add_snippet(
            name='',
            description='Test',
            command_text='echo test',
            tags='test'
        )


def test_add_snippet_empty_command(snippet_manager):
    """Test adding a snippet with empty command."""
    with pytest.raises(ValueError, match="Command text cannot be empty"):
        snippet_manager.add_snippet(
            name='Test',
            description='Test',
            command_text='',
            tags='test'
        )


def test_add_duplicate_name_snippet(snippet_manager):
    """Test adding snippets with duplicate names."""
    # Add first snippet
    snippet1_id = snippet_manager.add_snippet(
        name='Same Name',
        description='First snippet',
        command_text='cmd1',
        tags='test'
    )

    # Add second snippet with same name but allow_duplicate_names=True (default)
    snippet2_id = snippet_manager.add_snippet(
        name='Same Name',
        description='Second snippet',
        command_text='cmd2',
        tags='test'
    )
    assert snippet2_id != snippet1_id

    # Try to add third snippet with same name but allow_duplicate_names=False
    with pytest.raises(ValueError, match="A snippet with the name 'Same Name' already exists"):
        snippet_manager.add_snippet(
            name='Same Name',
            description='Third snippet',
            command_text='cmd3',
            tags='test',
            allow_duplicate_names=False
        )


def test_get_all_snippets(snippet_manager):
    """Test retrieving all snippets."""
    # Add multiple snippets
    snippets_data = [
        {'name': 'Test 1', 'description': 'First', 'command_text': 'cmd1', 'tags': 'test'},
        {'name': 'Test 2', 'description': 'Second', 'command_text': 'cmd2', 'tags': 'test'},
        {'name': 'Test 3', 'description': 'Third', 'command_text': 'cmd3', 'tags': 'test'}
    ]
    for data in snippets_data:
        snippet_manager.add_snippet(**data)

    # Retrieve all snippets
    snippets = snippet_manager.get_all_snippets()
    assert len(snippets) == 3
    assert all(isinstance(s, Snippet) for s in snippets)


def test_find_snippets(snippet_manager):
    """Test searching for snippets."""
    # Add test snippets
    snippet_manager.add_snippet(
        name='Python Script',
        description='A Python script',
        command_text='python script.py',
        tags='python, script'
    )
    snippet_manager.add_snippet(
        name='Git Command',
        description='A Git command',
        command_text='git commit',
        tags='git, vcs'
    )

    # Search by term
    python_results = snippet_manager.find_snippets('python')
    assert len(python_results) == 1
    assert python_results[0].name == 'Python Script'

    # Search by tags
    git_results = snippet_manager.find_snippets(tags_filter='git')
    assert len(git_results) == 1
    assert git_results[0].name == 'Git Command'


def test_update_snippet(snippet_manager, sample_snippet_data):
    """Test updating a snippet."""
    # Add initial snippet
    snippet_id = snippet_manager.add_snippet(**sample_snippet_data)

    # Update the snippet
    updated = snippet_manager.update_snippet(
        snippet_id=snippet_id,
        name='Updated Name',
        description='Updated description',
        command_text='updated command',
        tags='updated, tags'
    )
    assert updated is True

    # Verify the update
    snippet = snippet_manager.get_snippet_details(snippet_id)
    assert snippet.name == 'Updated Name'
    assert snippet.description == 'Updated description'
    assert snippet.command_text == 'updated command'
    assert snippet.tags == 'updated, tags'


def test_update_nonexistent_snippet(snippet_manager):
    """Test updating a snippet that doesn't exist."""
    with pytest.raises(ValueError, match="Snippet with ID 999 not found"):
        snippet_manager.update_snippet(
            snippet_id=999,
            name='Test',
            description='Test',
            command_text='test',
            tags='test'
        )


def test_delete_snippet(snippet_manager, sample_snippet_data):
    """Test deleting a snippet."""
    # Add a snippet
    snippet_id = snippet_manager.add_snippet(**sample_snippet_data)

    # Delete the snippet
    success = snippet_manager.delete_snippet(snippet_id)
    assert success is True

    # Verify the deletion
    snippet = snippet_manager.get_snippet_details(snippet_id)
    assert snippet is None


def test_get_snippet_count(snippet_manager):
    """Test getting the total number of snippets."""
    # Initial count should be 0
    assert snippet_manager.get_snippet_count() == 0

    # Add some snippets
    for i in range(3):
        snippet_manager.add_snippet(
            name=f'Test {i}',
            description=f'Test description {i}',
            command_text=f'cmd{i}',
            tags='test'
        )

    # Check updated count
    assert snippet_manager.get_snippet_count() == 3


def test_get_tags_list(snippet_manager):
    """Test getting list of all unique tags."""
    # Add snippets with various tags
    snippet_manager.add_snippet(
        name='Test 1',
        description='Test',
        command_text='cmd1',
        tags='python, script'
    )
    snippet_manager.add_snippet(
        name='Test 2',
        description='Test',
        command_text='cmd2',
        tags='python, test'
    )

    # Get unique tags
    tags = snippet_manager.get_tags_list()
    assert len(tags) == 3
    assert set(tags) == {'python', 'script', 'test'}


def test_record_usage(snippet_manager, sample_snippet_data):
    """Test recording snippet usage."""
    # Add a snippet
    snippet_id = snippet_manager.add_snippet(**sample_snippet_data)

    # Get initial last_used time
    initial_snippet = snippet_manager.get_snippet_details(snippet_id)
    initial_time = initial_snippet.last_used

    # Wait a moment to ensure timestamp will be different
    import time
    time.sleep(0.1)

    # Record usage
    success = snippet_manager.record_usage(snippet_id)
    assert success is True

    # Verify the update
    updated_snippet = snippet_manager.get_snippet_details(snippet_id)
    assert updated_snippet.last_used > initial_time
