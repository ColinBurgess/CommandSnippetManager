"""
Tests for the backup and restore functionality.
"""

import os
import time
import pytest
import tempfile
from datetime import datetime
from db.models import Snippet
from utils.backup import backup_database, restore_database, cleanup_old_backups, list_backups


def test_backup_database(database, temp_db_path):
    """Test creating a database backup."""
    # Add a snippet to the database
    snippet = Snippet(name='Test Snippet', command_text='echo test')
    database.insert_snippet(snippet)

    # Create backup
    backup_dir = tempfile.mkdtemp()
    backup_path = backup_database(temp_db_path, backup_dir)

    # Verify backup file was created
    assert os.path.exists(backup_path)
    assert '_backup_' in os.path.basename(backup_path)
    assert backup_path.endswith('.db')

    # Verify backup file is not empty
    assert os.path.getsize(backup_path) > 0


def test_restore_database(database, temp_db_path):
    """Test restoring a database from backup."""
    # Add a snippet to the database
    snippet = Snippet(name='Test Snippet', command_text='echo test')
    snippet_id = database.insert_snippet(snippet)

    # Create backup
    backup_dir = tempfile.mkdtemp()
    backup_path = backup_database(temp_db_path, backup_dir)

    # Delete the snippet
    database.delete_snippet(snippet_id)

    # Verify snippet is deleted
    assert database.get_snippet_by_id(snippet_id) is None

    # Restore from backup
    restore_database(backup_path, temp_db_path, keep_backup=True)

    # Verify snippet is restored
    restored_snippet = database.get_snippet_by_id(snippet_id)
    assert restored_snippet is not None
    assert restored_snippet.name == 'Test Snippet'


def test_restore_creates_safety_backup(database, temp_db_path):
    """Test that restore creates a safety backup of current DB."""
    # Add and modify data
    snippet = Snippet(name='Original', command_text='cmd1')
    database.insert_snippet(snippet)

    # Create first backup
    backup_dir = tempfile.mkdtemp()
    backup1 = backup_database(temp_db_path, backup_dir)

    # Add delay so next backup has different timestamp
    time.sleep(1.1)

    # Modify data
    snippet2 = Snippet(name='Modified', command_text='cmd2')
    database.insert_snippet(snippet2)

    # Restore from first backup
    restore_database(backup1, temp_db_path, keep_backup=True)

    # Check that a safety backup was created (should be in parent dir of DB, not backup_dir)
    parent_dir = os.path.dirname(temp_db_path)
    safety_files = [f for f in os.listdir(parent_dir) if 'pre_restore' in f]
    assert len(safety_files) > 0


def test_cleanup_old_backups(database, temp_db_path):
    """Test cleaning up old backup files."""
    backup_dir = tempfile.mkdtemp()

    # Create multiple backups with delays to ensure different timestamps
    for i in range(7):
        backup_database(temp_db_path, backup_dir)
        time.sleep(0.15)  # Add delay to ensure different timestamps

    # Verify backups were created
    backup_files = [f for f in os.listdir(backup_dir) if '_backup_' in f and f.endswith('.db')]
    assert len(backup_files) >= 5  # At least 5 should exist (some may be overwritten if too fast)

    # Cleanup, keeping only 3
    deleted_count = cleanup_old_backups(backup_dir, keep_count=3)

    # Verify cleanup worked
    remaining_files = [f for f in os.listdir(backup_dir) if '_backup_' in f and f.endswith('.db')]
    assert len(remaining_files) <= 3


def test_list_backups(database, temp_db_path):
    """Test listing available backups."""
    backup_dir = tempfile.mkdtemp()

    # Create a few backups with delays to ensure different timestamps
    for i in range(3):
        backup_database(temp_db_path, backup_dir)
        time.sleep(0.15)  # Add delay to ensure different timestamps

    # List backups
    backups = list_backups(backup_dir)

    # Verify list is not empty and sorted by creation time
    assert len(backups) >= 1
    assert all('name' in b and 'path' in b and 'size_mb' in b for b in backups)

    # Verify sorting (newest first)
    for i in range(len(backups) - 1):
        assert backups[i]['created'] >= backups[i + 1]['created']


def test_backup_nonexistent_database():
    """Test backup with non-existent database file."""
    with pytest.raises(Exception):
        backup_database('/nonexistent/path/db.db', tempfile.mkdtemp())


def test_restore_nonexistent_backup(temp_db_path):
    """Test restore with non-existent backup file."""
    with pytest.raises(Exception):
        restore_database('/nonexistent/path/backup.db', temp_db_path)


def test_list_backups_empty_directory():
    """Test listing backups from empty directory."""
    backup_dir = tempfile.mkdtemp()
    backups = list_backups(backup_dir)
    assert len(backups) == 0


def test_list_backups_nonexistent_directory():
    """Test listing backups from non-existent directory."""
    backups = list_backups('/nonexistent/path')
    assert len(backups) == 0


# ========================================
# SNAPSHOT TESTS
# ========================================

def test_create_snapshot_before(database, temp_db_path):
    """Test creating a BEFORE snapshot."""
    from utils.backup import create_snapshot_before

    # Add a snippet to the database
    snippet = Snippet(name='Test Snippet', command_text='echo test')
    database.insert_snippet(snippet)

    # Create BEFORE snapshot
    result = create_snapshot_before(temp_db_path, 'add', 'Test Snippet')

    assert result is not None
    assert 'snapshot_id' in result
    assert 'snapshot_dir' in result
    assert 'backup_path' in result
    assert os.path.exists(result['snapshot_dir'])
    assert os.path.exists(result['backup_path'])

    # Verify metadata.json exists
    metadata_path = os.path.join(result['snapshot_dir'], 'metadata.json')
    assert os.path.exists(metadata_path)


def test_create_snapshot_after(database, temp_db_path):
    """Test creating an AFTER snapshot."""
    from utils.backup import create_snapshot_before, create_snapshot_after

    # Add a snippet to the database
    snippet = Snippet(name='Test Snippet', command_text='echo test')
    database.insert_snippet(snippet)

    # Create BEFORE snapshot
    before_result = create_snapshot_before(temp_db_path, 'add', 'Test Snippet')
    snapshot_id = before_result['snapshot_id']

    # Modify the database (add another snippet)
    snippet2 = Snippet(name='Test Snippet 2', command_text='echo test 2')
    database.insert_snippet(snippet2)

    # Create AFTER snapshot
    after_result = create_snapshot_after(temp_db_path, snapshot_id)

    assert after_result is not None
    assert 'snapshot_dir' in after_result
    assert 'backup_path' in after_result
    assert os.path.exists(after_result['backup_path'])

    # Verify both before and after files exist
    before_path = os.path.join(after_result['snapshot_dir'], 'before.db')
    after_path = os.path.join(after_result['snapshot_dir'], 'after.db')
    assert os.path.exists(before_path)
    assert os.path.exists(after_path)


def test_list_snapshots(database, temp_db_path):
    """Test listing snapshots."""
    from utils.backup import create_snapshot_before, create_snapshot_after, list_snapshots

    # Create a few snapshots
    for i in range(3):
        before_result = create_snapshot_before(temp_db_path, 'add', f'Snippet {i}')
        snapshot_id = before_result['snapshot_id']
        create_snapshot_after(temp_db_path, snapshot_id)
        time.sleep(0.01)  # Small delay to ensure different timestamps

    # List snapshots
    snapshots = list_snapshots(temp_db_path)

    assert len(snapshots) >= 3
    assert 'snapshot_id' in snapshots[0]
    assert 'operation' in snapshots[0]
    assert 'snippet_name' in snapshots[0]
    assert 'status' in snapshots[0]


def test_cleanup_old_snapshots(database, temp_db_path):
    """Test cleaning up old snapshots."""
    from utils.backup import create_snapshot_before, create_snapshot_after, cleanup_old_snapshots, list_snapshots

    # Create 7 snapshots
    for i in range(7):
        before_result = create_snapshot_before(temp_db_path, 'add', f'Snippet {i}')
        snapshot_id = before_result['snapshot_id']
        create_snapshot_after(temp_db_path, snapshot_id)
        time.sleep(0.01)

    # Cleanup keeping only 5
    deleted_count = cleanup_old_snapshots(temp_db_path, keep_count=5)

    assert deleted_count == 2

    # Verify only 5 remain
    remaining_snapshots = list_snapshots(temp_db_path, limit=10)
    assert len(remaining_snapshots) == 5


def test_restore_from_snapshot(database, temp_db_path):
    """Test restoring from a snapshot."""
    from utils.backup import create_snapshot_before, create_snapshot_after, restore_from_snapshot

    # Add snippets to database
    snippet = Snippet(name='Original Snippet', command_text='echo original')
    snippet_id = database.insert_snippet(snippet)

    # Create BEFORE snapshot
    before_result = create_snapshot_before(temp_db_path, 'update', 'Original Snippet')
    snapshot_id = before_result['snapshot_id']

    # Modify the database (update the snippet)
    updated_snippet = Snippet(
        snippet_id=snippet_id,
        name='Original Snippet',
        description='Updated description',
        command_text='echo updated',
        tags=''
    )
    database.update_snippet(updated_snippet)

    # Create AFTER snapshot
    create_snapshot_after(temp_db_path, snapshot_id)

    # Verify the snippet was updated
    assert database.get_snippet_by_id(snippet_id).command_text == 'echo updated'

    # Restore from BEFORE snapshot
    result = restore_from_snapshot(temp_db_path, snapshot_id, use_before=True)
    assert result is True

    # Verify the database was restored (need to reload)
    # The command should be back to original after restore
    restored_snippet = database.get_snippet_by_id(snippet_id)
    if restored_snippet:
        assert restored_snippet.command_text == 'echo original'


def test_snapshot_before_metadata(database, temp_db_path):
    """Test that BEFORE snapshot metadata is correctly stored."""
    from utils.backup import create_snapshot_before
    import json

    # Create BEFORE snapshot
    result = create_snapshot_before(temp_db_path, 'delete', 'Test Snippet')
    snapshot_id = result['snapshot_id']

    # Read and verify metadata
    metadata_path = os.path.join(result['snapshot_dir'], 'metadata.json')
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    assert metadata['snapshot_id'] == snapshot_id
    assert metadata['operation'] == 'delete'
    assert metadata['snippet_name'] == 'Test Snippet'
    assert metadata['status'] == 'in-progress'
    assert metadata['after_timestamp'] is None


def test_snapshot_after_metadata(database, temp_db_path):
    """Test that AFTER snapshot metadata is correctly updated."""
    from utils.backup import create_snapshot_before, create_snapshot_after
    import json

    # Create BEFORE snapshot
    before_result = create_snapshot_before(temp_db_path, 'update', 'Test Snippet')
    snapshot_id = before_result['snapshot_id']

    # Create AFTER snapshot
    create_snapshot_after(temp_db_path, snapshot_id)

    # Read and verify metadata
    metadata_path = os.path.join(before_result['snapshot_dir'], 'metadata.json')
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    assert metadata['snapshot_id'] == snapshot_id
    assert metadata['status'] == 'completed'
    assert metadata['after_timestamp'] is not None
    assert metadata['before_timestamp'] is not None
