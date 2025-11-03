"""
Backup and restore functionality for the Command Snippet Management Application.
"""

import json
import sqlite3
import shutil
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from db.models import Snippet
from utils.logger import get_logger

logger = get_logger(__name__)

def export_snippets_to_json(db_connection: sqlite3.Connection) -> str:
    """
    Export all snippets from the database to JSON format.

    Args:
        db_connection: Active database connection

    Returns:
        JSON string containing all snippets
    """
    cursor = db_connection.cursor()
    cursor.row_factory = sqlite3.Row

    try:
        cursor.execute("""
            SELECT id, name, description, command_text, tags,
                   last_used, created_at
            FROM snippets
            ORDER BY created_at
        """)
        rows = cursor.fetchall()

        snippets = []
        for row in rows:
            snippet_dict = {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'command_text': row['command_text'],
                'tags': row['tags'],
                'last_used': row['last_used'],
                'created_at': row['created_at']
            }
            snippets.append(snippet_dict)

        export_data = {
            'version': 1,
            'exported_at': datetime.now().isoformat(),
            'snippets': snippets
        }

        return json.dumps(export_data, indent=2)

    except Exception as e:
        logger.error("Failed to export snippets: %s", str(e))
        raise Exception(f"Failed to export snippets: {e}")

def import_snippets_from_json(db_connection: sqlite3.Connection, json_data: str,
                            replace_existing: bool = False) -> Dict[str, Any]:
    """
    Import snippets from JSON format into the database.

    Args:
        db_connection: Active database connection
        json_data: JSON string containing snippets
        replace_existing: If True, clear existing snippets before import

    Returns:
        Dictionary with import statistics
    """
    cursor = db_connection.cursor()

    try:
        data = json.loads(json_data)

        if 'version' not in data or 'snippets' not in data:
            raise ValueError("Invalid backup format")

        stats = {
            'total': len(data['snippets']),
            'imported': 0,
            'skipped': 0,
            'failed': 0
        }

        if replace_existing:
            logger.info("Clearing existing snippets before import")
            cursor.execute("DELETE FROM snippets")

        for snippet_data in data['snippets']:
            try:
                # Remove ID to let SQLite auto-generate new ones
                snippet_data.pop('id', None)

                cursor.execute("""
                    INSERT INTO snippets
                    (name, description, command_text, tags, last_used, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    snippet_data['name'],
                    snippet_data['description'],
                    snippet_data['command_text'],
                    snippet_data['tags'],
                    snippet_data['last_used'],
                    snippet_data['created_at']
                ))
                stats['imported'] += 1

            except Exception as e:
                logger.error("Failed to import snippet %s: %s",
                           snippet_data.get('name', 'unknown'), str(e))
                stats['failed'] += 1

        db_connection.commit()
        logger.info("Import completed: %s", stats)
        return stats

    except Exception as e:
        db_connection.rollback()
        logger.error("Import failed: %s", str(e))
        raise Exception(f"Failed to import snippets: {e}")


def backup_database(db_path: str, backup_dir: str = None) -> str:
    """
    Create a backup copy of the SQLite database with timestamp.

    Args:
        db_path: Path to the current database file (snippets.db)
        backup_dir: Directory to store backup (default: data/ directory)

    Returns:
        Path to the created backup file

    Raises:
        Exception: If backup fails
    """
    try:
        # Determine backup directory
        if backup_dir is None:
            backup_dir = os.path.dirname(db_path) or 'data'

        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)

        # Generate backup filename with timestamp and microseconds
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        db_name = Path(db_path).stem
        backup_filename = f"{db_name}_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)        # Copy database file
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")

        shutil.copy2(db_path, backup_path)
        logger.info("Database backup created: %s", backup_path)

        return backup_path

    except Exception as e:
        logger.error("Backup failed: %s", str(e))
        raise Exception(f"Failed to create database backup: {e}")


def restore_database(backup_path: str, db_path: str, keep_backup: bool = True) -> bool:
    """
    Restore database from a backup file.

    Args:
        backup_path: Path to the backup file
        db_path: Path to restore the database to (current DB)
        keep_backup: If True, keep the backup file after restore

    Returns:
        True if restore successful

    Raises:
        Exception: If restore fails
    """
    try:
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Create a safety backup of current DB before restore
        if os.path.exists(db_path):
            safety_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safety_path = f"{db_path}.pre_restore_{safety_timestamp}"
            shutil.copy2(db_path, safety_path)
            logger.info("Safety backup created: %s", safety_path)

        # Restore from backup
        shutil.copy2(backup_path, db_path)
        logger.info("Database restored from backup: %s", backup_path)

        if not keep_backup:
            os.remove(backup_path)
            logger.info("Backup file removed: %s", backup_path)

        return True

    except Exception as e:
        logger.error("Restore failed: %s", str(e))
        raise Exception(f"Failed to restore database: {e}")


def cleanup_old_backups(backup_dir: str, keep_count: int = 5) -> int:
    """
    Clean up old backup files, keeping only the most recent ones.

    Args:
        backup_dir: Directory containing backup files
        keep_count: Number of most recent backups to keep

    Returns:
        Number of backups deleted

    Raises:
        Exception: If cleanup fails
    """
    try:
        if not os.path.exists(backup_dir):
            logger.warning("Backup directory not found: %s", backup_dir)
            return 0

        # Find all backup files (ending with _backup_*.db)
        backup_files = []
        for file in os.listdir(backup_dir):
            if '_backup_' in file and file.endswith('.db'):
                file_path = os.path.join(backup_dir, file)
                backup_files.append({
                    'path': file_path,
                    'mtime': os.path.getmtime(file_path),
                    'name': file
                })

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x['mtime'], reverse=True)

        # Remove old backups
        deleted_count = 0
        for backup in backup_files[keep_count:]:
            try:
                os.remove(backup['path'])
                logger.info("Deleted old backup: %s", backup['name'])
                deleted_count += 1
            except Exception as e:
                logger.error("Failed to delete backup %s: %s", backup['name'], str(e))

        logger.info("Cleanup completed: %d backups deleted", deleted_count)
        return deleted_count

    except Exception as e:
        logger.error("Backup cleanup failed: %s", str(e))
        raise Exception(f"Failed to cleanup old backups: {e}")


def list_backups(backup_dir: str) -> List[Dict[str, Any]]:
    """
    List all available backups with metadata.

    Args:
        backup_dir: Directory containing backup files

    Returns:
        List of dictionaries with backup info (path, name, size, created_time)
    """
    try:
        backups = []

        if not os.path.exists(backup_dir):
            logger.warning("Backup directory not found: %s", backup_dir)
            return backups

        for file in os.listdir(backup_dir):
            if '_backup_' in file and file.endswith('.db'):
                file_path = os.path.join(backup_dir, file)
                try:
                    stats = os.stat(file_path)
                    backup_info = {
                        'name': file,
                        'path': file_path,
                        'size_bytes': stats.st_size,
                        'size_mb': stats.st_size / (1024 * 1024),
                        'created': datetime.fromtimestamp(stats.st_mtime).isoformat()
                    }
                    backups.append(backup_info)
                except Exception as e:
                    logger.error("Failed to get info for backup %s: %s", file, str(e))

        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups

    except Exception as e:
        logger.error("Failed to list backups: %s", str(e))


# ========================================
# AUTO-SNAPSHOT FUNCTIONS
# ========================================

def create_snapshot_before(db_path: str, operation: str, snippet_name: str) -> Dict[str, str]:
    """
    Create a BEFORE snapshot of the database before an operation.

    Args:
        db_path: Path to the snippets database
        operation: Operation type ('add', 'update', 'delete')
        snippet_name: Name of the snippet being modified

    Returns:
        Dictionary with snapshot info (backup_path, snapshot_id, timestamp)
    """
    try:
        # Create auto-snapshot directory if needed
        auto_snapshot_dir = os.path.dirname(db_path)
        auto_snapshot_parent = os.path.join(os.path.dirname(auto_snapshot_dir), 'backups', 'auto')

        # Generate unique snapshot ID with microseconds
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S_%f')
        snapshot_dir = os.path.join(auto_snapshot_parent, timestamp)

        os.makedirs(snapshot_dir, exist_ok=True)

        # Create before backup
        before_db_path = os.path.join(snapshot_dir, 'before.db')
        shutil.copy2(db_path, before_db_path)

        # Create metadata JSON
        metadata = {
            'snapshot_id': timestamp,
            'operation': operation,
            'snippet_name': snippet_name,
            'before_timestamp': now.isoformat(),
            'after_timestamp': None,
            'status': 'in-progress'
        }

        metadata_path = os.path.join(snapshot_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(
            "Created BEFORE snapshot for %s operation on '%s': %s",
            operation, snippet_name, snapshot_dir
        )

        return {
            'backup_path': before_db_path,
            'snapshot_dir': snapshot_dir,
            'snapshot_id': timestamp
        }

    except Exception as e:
        logger.error(
            "Failed to create BEFORE snapshot for %s on '%s': %s",
            operation, snippet_name, str(e)
        )
        return {}


def create_snapshot_after(db_path: str, snapshot_id: str) -> Dict[str, str]:
    """
    Create an AFTER snapshot of the database after an operation completes.

    Args:
        db_path: Path to the snippets database
        snapshot_id: Snapshot ID from create_snapshot_before()

    Returns:
        Dictionary with snapshot info (backup_path, snapshot_dir)
    """
    try:
        # Locate the snapshot directory
        auto_snapshot_parent = os.path.join(os.path.dirname(os.path.dirname(db_path)), 'backups', 'auto')
        snapshot_dir = os.path.join(auto_snapshot_parent, snapshot_id)

        if not os.path.exists(snapshot_dir):
            logger.error("Snapshot directory not found: %s", snapshot_dir)
            return {}

        # Create after backup
        after_db_path = os.path.join(snapshot_dir, 'after.db')
        shutil.copy2(db_path, after_db_path)

        # Update metadata JSON
        metadata_path = os.path.join(snapshot_dir, 'metadata.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        metadata['after_timestamp'] = datetime.now().isoformat()
        metadata['status'] = 'completed'

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info("Created AFTER snapshot: %s", snapshot_dir)

        return {
            'backup_path': after_db_path,
            'snapshot_dir': snapshot_dir
        }

    except Exception as e:
        logger.error("Failed to create AFTER snapshot for %s: %s", snapshot_id, str(e))
        return {}


def list_snapshots(db_path: str, limit: int = 10) -> List[Dict]:
    """
    List recent auto-snapshots with their metadata.

    Args:
        db_path: Path to the snippets database
        limit: Maximum number of snapshots to return

    Returns:
        List of dictionaries with snapshot metadata
    """
    try:
        auto_snapshot_parent = os.path.join(os.path.dirname(os.path.dirname(db_path)), 'backups', 'auto')
        snapshots = []

        if not os.path.exists(auto_snapshot_parent):
            logger.warning("Auto-snapshot directory not found: %s", auto_snapshot_parent)
            return snapshots

        # Get all snapshot directories
        snapshot_dirs = sorted(
            os.listdir(auto_snapshot_parent),
            reverse=True
        )

        for snapshot_id in snapshot_dirs[:limit]:
            snapshot_dir = os.path.join(auto_snapshot_parent, snapshot_id)
            metadata_path = os.path.join(snapshot_dir, 'metadata.json')

            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)

                    # Get file sizes
                    before_size = 0
                    after_size = 0
                    before_path = os.path.join(snapshot_dir, 'before.db')
                    after_path = os.path.join(snapshot_dir, 'after.db')

                    if os.path.exists(before_path):
                        before_size = os.path.getsize(before_path)
                    if os.path.exists(after_path):
                        after_size = os.path.getsize(after_path)

                    snapshot_info = {
                        'snapshot_id': snapshot_id,
                        'snapshot_dir': snapshot_dir,
                        'operation': metadata.get('operation', 'unknown'),
                        'snippet_name': metadata.get('snippet_name', 'unknown'),
                        'before_timestamp': metadata.get('before_timestamp', ''),
                        'after_timestamp': metadata.get('after_timestamp', ''),
                        'status': metadata.get('status', 'unknown'),
                        'before_size_mb': before_size / (1024 * 1024),
                        'after_size_mb': after_size / (1024 * 1024)
                    }
                    snapshots.append(snapshot_info)

                except Exception as e:
                    logger.error("Failed to read metadata for snapshot %s: %s", snapshot_id, str(e))

        return snapshots

    except Exception as e:
        logger.error("Failed to list snapshots: %s", str(e))
        return []


def cleanup_old_snapshots(db_path: str, keep_count: int = 5) -> int:
    """
    Remove old auto-snapshots, keeping only the most recent N.

    Args:
        db_path: Path to the snippets database
        keep_count: Number of recent snapshots to keep

    Returns:
        Number of snapshots deleted
    """
    try:
        auto_snapshot_parent = os.path.join(os.path.dirname(os.path.dirname(db_path)), 'backups', 'auto')

        if not os.path.exists(auto_snapshot_parent):
            logger.warning("Auto-snapshot directory not found: %s", auto_snapshot_parent)
            return 0

        # Get all snapshot directories sorted by time (newest first)
        snapshot_dirs = sorted(
            os.listdir(auto_snapshot_parent),
            reverse=True
        )

        deleted_count = 0

        # Delete snapshots beyond the keep_count
        for snapshot_id in snapshot_dirs[keep_count:]:
            snapshot_dir = os.path.join(auto_snapshot_parent, snapshot_id)
            try:
                shutil.rmtree(snapshot_dir)
                logger.info("Deleted old snapshot: %s", snapshot_id)
                deleted_count += 1
            except Exception as e:
                logger.error("Failed to delete snapshot %s: %s", snapshot_id, str(e))

        if deleted_count > 0:
            logger.info("Cleaned up %d old snapshots, keeping %d most recent", deleted_count, keep_count)

        return deleted_count

    except Exception as e:
        logger.error("Failed to cleanup old snapshots: %s", str(e))
        return 0


def restore_from_snapshot(db_path: str, snapshot_id: str, use_before: bool = True) -> bool:
    """
    Restore the database from a specific snapshot.

    Args:
        db_path: Path to the snippets database
        snapshot_id: Snapshot ID to restore from
        use_before: If True, restore from 'before' snapshot; if False, restore from 'after'

    Returns:
        True if restore successful, False otherwise
    """
    try:
        auto_snapshot_parent = os.path.join(os.path.dirname(os.path.dirname(db_path)), 'backups', 'auto')
        snapshot_dir = os.path.join(auto_snapshot_parent, snapshot_id)

        if not os.path.exists(snapshot_dir):
            logger.error("Snapshot directory not found: %s", snapshot_dir)
            return False

        # Choose which snapshot to restore from
        snapshot_file = 'before.db' if use_before else 'after.db'
        snapshot_db_path = os.path.join(snapshot_dir, snapshot_file)

        if not os.path.exists(snapshot_db_path):
            logger.error("Snapshot file not found: %s", snapshot_db_path)
            return False

        # Create a safety backup of current database
        safety_backup_dir = os.path.dirname(db_path)
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S_%f')
        safety_backup_path = os.path.join(
            safety_backup_dir,
            'backups',
            'manual',
            f'safety_before_restore_{timestamp}_backup.db'
        )

        os.makedirs(os.path.dirname(safety_backup_path), exist_ok=True)
        shutil.copy2(db_path, safety_backup_path)

        # Restore from snapshot
        shutil.copy2(snapshot_db_path, db_path)

        logger.info(
            "Restored database from snapshot %s (%s). Safety backup: %s",
            snapshot_id, snapshot_file, safety_backup_path
        )

        return True

    except Exception as e:
        logger.error("Failed to restore from snapshot %s: %s", snapshot_id, str(e))
        return False
        return []

