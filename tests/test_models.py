"""
Tests for the data models of the Command Snippet Management Application.
"""

from datetime import datetime
from db.models import Snippet


def test_snippet_creation():
    """Test basic snippet creation with required fields."""
    snippet = Snippet(
        name='Test Snippet',
        command_text='echo "test"'
    )
    assert snippet.name == 'Test Snippet'
    assert snippet.command_text == 'echo "test"'
    assert snippet.description == ''
    assert snippet.tags == ''
    assert isinstance(snippet.last_used, datetime)
    assert isinstance(snippet.created_at, datetime)


def test_snippet_creation_with_all_fields():
    """Test snippet creation with all fields."""
    now = datetime.now()
    snippet = Snippet(
        snippet_id=1,
        name='Test Snippet',
        description='Test Description',
        command_text='echo "test"',
        tags='test, example',
        last_used=now,
        created_at=now
    )
    assert snippet.id == 1
    assert snippet.name == 'Test Snippet'
    assert snippet.description == 'Test Description'
    assert snippet.command_text == 'echo "test"'
    assert snippet.tags == 'test, example'
    assert snippet.last_used == now
    assert snippet.created_at == now


def test_snippet_to_dict():
    """Test conversion of snippet to dictionary."""
    now = datetime.now()
    snippet = Snippet(
        snippet_id=1,
        name='Test Snippet',
        description='Test Description',
        command_text='echo "test"',
        tags='test, example',
        last_used=now,
        created_at=now
    )
    data = snippet.to_dict()
    assert data['id'] == 1
    assert data['name'] == 'Test Snippet'
    assert data['description'] == 'Test Description'
    assert data['command_text'] == 'echo "test"'
    assert data['tags'] == 'test, example'
    assert data['last_used'] == now.isoformat()
    assert data['created_at'] == now.isoformat()


def test_snippet_from_dict():
    """Test creation of snippet from dictionary."""
    now = datetime.now()
    data = {
        'id': 1,
        'name': 'Test Snippet',
        'description': 'Test Description',
        'command_text': 'echo "test"',
        'tags': 'test, example',
        'last_used': now.isoformat(),
        'created_at': now.isoformat()
    }
    snippet = Snippet.from_dict(data)
    assert snippet.id == 1
    assert snippet.name == 'Test Snippet'
    assert snippet.description == 'Test Description'
    assert snippet.command_text == 'echo "test"'
    assert snippet.tags == 'test, example'
    assert snippet.last_used.isoformat() == now.isoformat()
    assert snippet.created_at.isoformat() == now.isoformat()


def test_get_tags_list():
    """Test getting tags as a list."""
    snippet = Snippet(
        name='Test Snippet',
        command_text='echo "test"',
        tags='test, example, unit-test'
    )
    tags = snippet.get_tags_list()
    assert isinstance(tags, list)
    assert len(tags) == 3
    assert 'test' in tags
    assert 'example' in tags
    assert 'unit-test' in tags


def test_get_tags_list_empty():
    """Test getting tags list when tags are empty."""
    snippet = Snippet(
        name='Test Snippet',
        command_text='echo "test"'
    )
    tags = snippet.get_tags_list()
    assert isinstance(tags, list)
    assert len(tags) == 0


def test_get_tags_list_whitespace():
    """Test getting tags list with whitespace."""
    snippet = Snippet(
        name='Test Snippet',
        command_text='echo "test"',
        tags='  test  ,  example  '
    )
    tags = snippet.get_tags_list()
    assert len(tags) == 2
    assert tags == ['test', 'example']


def test_string_representation():
    """Test string representation of snippet."""
    snippet = Snippet(
        snippet_id=1,
        name='Test Snippet',
        command_text='echo "test"'
    )
    assert str(snippet) == "Snippet(id=1, name='Test Snippet')"
    assert 'Test Snippet' in repr(snippet)
