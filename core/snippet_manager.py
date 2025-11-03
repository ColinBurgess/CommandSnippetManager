"""
Business logic layer for managing command snippets.
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from db.database import Database
from db.models import Snippet
from utils.backup import backup_database, restore_database, cleanup_old_backups, list_backups
from utils.logger import get_logger

logger = get_logger(__name__)


class SnippetManager:
    """
    Manages snippet operations and orchestrates UI and database interactions.
    """

    def __init__(self, database: Database):
        """
        Initialize the snippet manager with a database instance.

        Args:
            database: Database instance for data operations
        """
        self.db = database

    def add_snippet(self, name: str, description: str, command_text: str, tags: str, allow_duplicate_names: bool = True) -> int:
        """
        Create and add a new snippet to the database.

        Args:
            name: Short, descriptive name for the snippet
            description: Longer description of the snippet's purpose
            command_text: The actual command to execute
            tags: Comma-separated tags for categorization
            allow_duplicate_names: If False, raises an error if the name already exists

        Returns:
            ID of the created snippet

        Raises:
            ValueError: If snippet name or command is empty, or if name already exists and allow_duplicate_names is False
            Exception: If snippet creation fails
        """
        if not name.strip():
            raise ValueError("Snippet name cannot be empty")

        if not command_text.strip():
            raise ValueError("Command text cannot be empty")

        if not allow_duplicate_names and self.db.name_exists(name.strip()):
            raise ValueError(f"A snippet with the name '{name}' already exists")

        snippet = Snippet(
            name=name.strip(),
            description=description.strip(),
            command_text=command_text.strip(),
            tags=tags.strip()
        )

        try:
            # Create BEFORE snapshot
            snapshot_info = self.create_snapshot_before('add', name.strip())
            snapshot_id = snapshot_info.get('snapshot_id', '')

            # Add the snippet
            snippet_id = self.db.insert_snippet(snippet)

            # Create AFTER snapshot
            if snapshot_id:
                self.create_snapshot_after(snapshot_id)

            # Cleanup old snapshots
            self.cleanup_old_snapshots(keep_count=5)

            return snippet_id
        except Exception as e:
            raise Exception(f"Failed to add snippet: {e}")

    def get_all_snippets(self) -> List[Snippet]:
        """
        Retrieve all snippets from the database.

        Returns:
            List of all Snippet objects, ordered by last_used DESC
        """
        try:
            return self.db.get_all_snippets()
        except Exception as e:
            raise Exception(f"Failed to retrieve snippets: {e}")

    def find_snippets(self, search_term: str = "", tags_filter: str = "") -> List[Snippet]:
        """
        Search for snippets based on search term and tags.

        Args:
            search_term: Text to search for in name, description, and command
            tags_filter: Comma-separated tags to filter by

        Returns:
            List of matching Snippet objects
        """
        try:
            # Parse tags filter into a list
            tags_list = None
            if tags_filter.strip():
                tags_list = [tag.strip() for tag in tags_filter.split(',') if tag.strip()]

            return self.db.search_snippets(search_term, tags_list)
        except Exception as e:
            raise Exception(f"Failed to search snippets: {e}")

    def update_snippet(self, snippet_id: int, name: str, description: str,
                      command_text: str, tags: str) -> bool:
        """
        Update an existing snippet with new data.

        Args:
            snippet_id: ID of the snippet to update
            name: Updated name
            description: Updated description
            command_text: Updated command text
            tags: Updated tags

        Returns:
            True if successful

        Raises:
            Exception: If update fails
        """
        if not name.strip():
            raise ValueError("Snippet name cannot be empty")

        if not command_text.strip():
            raise ValueError("Command text cannot be empty")

        # Get existing snippet to preserve timestamps
        existing_snippet = self.db.get_snippet_by_id(snippet_id)
        if not existing_snippet:
            raise ValueError(f"Snippet with ID {snippet_id} not found")

        # Create updated snippet object
        updated_snippet = Snippet(
            snippet_id=snippet_id,
            name=name.strip(),
            description=description.strip(),
            command_text=command_text.strip(),
            tags=tags.strip(),
            last_used=existing_snippet.last_used,
            created_at=existing_snippet.created_at
        )

        try:
            # Create BEFORE snapshot
            snapshot_info = self.create_snapshot_before('update', name.strip())
            snapshot_id = snapshot_info.get('snapshot_id', '')

            # Update the snippet
            result = self.db.update_snippet(updated_snippet)

            # Create AFTER snapshot
            if snapshot_id:
                self.create_snapshot_after(snapshot_id)

            # Cleanup old snapshots
            self.cleanup_old_snapshots(keep_count=5)

            return result
        except Exception as e:
            raise Exception(f"Failed to update snippet: {e}")

    def delete_snippet(self, snippet_id: int) -> bool:
        """
        Delete a snippet from the database.

        Args:
            snippet_id: ID of the snippet to delete

        Returns:
            True if successful

        Raises:
            Exception: If deletion fails
        """
        try:
            # Get snippet name for snapshot
            snippet = self.db.get_snippet_by_id(snippet_id)
            snippet_name = snippet.name if snippet else f"snippet_{snippet_id}"

            # Create BEFORE snapshot
            snapshot_info = self.create_snapshot_before('delete', snippet_name)
            snapshot_id = snapshot_info.get('snapshot_id', '')

            # Delete the snippet
            result = self.db.delete_snippet(snippet_id)

            # Create AFTER snapshot
            if snapshot_id:
                self.create_snapshot_after(snapshot_id)

            # Cleanup old snapshots
            self.cleanup_old_snapshots(keep_count=5)

            return result
        except Exception as e:
            raise Exception(f"Failed to delete snippet: {e}")

    def get_snippet_details(self, snippet_id: int) -> Optional[Snippet]:
        """
        Get detailed information for a specific snippet.

        Args:
            snippet_id: ID of the snippet to retrieve

        Returns:
            Snippet object or None if not found
        """
        try:
            return self.db.get_snippet_by_id(snippet_id)
        except Exception as e:
            raise Exception(f"Failed to get snippet details: {e}")

    def record_usage(self, snippet_id: int) -> bool:
        """
        Record that a snippet was used by updating its last_used timestamp.

        Args:
            snippet_id: ID of the snippet that was used

        Returns:
            True if successful
        """
        try:
            return self.db.update_last_used(snippet_id)
        except Exception as e:
            raise Exception(f"Failed to record snippet usage: {e}")

    def get_snippet_count(self) -> int:
        """
        Get the total number of snippets in the database.

        Returns:
            Number of snippets
        """
        try:
            snippets = self.db.get_all_snippets()
            return len(snippets)
        except Exception as e:
            raise Exception(f"Failed to get snippet count: {e}")

    def get_tags_list(self) -> List[str]:
        """
        Get a list of all unique tags used across all snippets.

        Returns:
            Sorted list of unique tags
        """
        try:
            snippets = self.db.get_all_snippets()
            all_tags = set()

            for snippet in snippets:
                tags = snippet.get_tags_list()
                all_tags.update(tags)

            return sorted(list(all_tags))
        except Exception as e:
            raise Exception(f"Failed to get tags list: {e}")

    def create_backup(self, backup_dir: str = None) -> str:
        """
        Create a backup of the database.

        Args:
            backup_dir: Directory to store backup (default: data/ directory)

        Returns:
            Path to the created backup file

        Raises:
            Exception: If backup fails
        """
        try:
            db_path = self.db.db_path
            backup_path = backup_database(db_path, backup_dir)
            logger.info("Backup created: %s", backup_path)
            return backup_path
        except Exception as e:
            logger.error("Failed to create backup: %s", str(e))
            raise

    def restore_from_backup(self, backup_path: str, keep_backup: bool = True) -> bool:
        """
        Restore database from a backup file.

        Args:
            backup_path: Path to the backup file
            keep_backup: If True, keep the backup file after restore

        Returns:
            True if restore successful

        Raises:
            Exception: If restore fails
        """
        try:
            db_path = self.db.db_path
            success = restore_database(backup_path, db_path, keep_backup)
            logger.info("Database restored from backup: %s", backup_path)
            return success
        except Exception as e:
            logger.error("Failed to restore from backup: %s", str(e))
            raise

    def cleanup_old_backups(self, backup_dir: str = None, keep_count: int = 5) -> int:
        """
        Clean up old backup files, keeping only the most recent ones.

        Args:
            backup_dir: Directory containing backup files (default: data/ directory)
            keep_count: Number of most recent backups to keep

        Returns:
            Number of backups deleted

        Raises:
            Exception: If cleanup fails
        """
        try:
            if backup_dir is None:
                db_dir = self.db.db_path
                backup_dir = os.path.dirname(db_dir) or 'data'

            deleted_count = cleanup_old_backups(backup_dir, keep_count)
            logger.info("Cleanup completed: %d backups deleted", deleted_count)
            return deleted_count
        except Exception as e:
            logger.error("Failed to cleanup old backups: %s", str(e))
            raise

    def list_available_backups(self, backup_dir: str = None) -> List[Dict[str, Any]]:
        """
        List all available database backups with metadata.

        Args:
            backup_dir: Directory containing backup files (default: data/ directory)

        Returns:
            List of dictionaries with backup info (path, name, size, created_time)
        """
        try:
            if backup_dir is None:
                db_dir = self.db.db_path
                backup_dir = os.path.dirname(db_dir) or 'data'

            backups = list_backups(backup_dir)
            return backups
        except Exception as e:
            logger.error("Failed to list backups: %s", str(e))
            return []

    # ========================================
    # AUTO-SNAPSHOT METHODS
    # ========================================

    def create_snapshot_before(self, operation: str, snippet_name: str) -> Dict[str, str]:
        """
        Create a BEFORE snapshot before an operation on a snippet.

        Args:
            operation: Operation type ('add', 'update', 'delete')
            snippet_name: Name of the snippet being modified

        Returns:
            Dictionary with snapshot info (backup_path, snapshot_id, snapshot_dir)
        """
        try:
            from utils.backup import create_snapshot_before
            result = create_snapshot_before(self.db.db_path, operation, snippet_name)
            return result
        except Exception as e:
            logger.error("Failed to create BEFORE snapshot: %s", str(e))
            return {}

    def create_snapshot_after(self, snapshot_id: str) -> Dict[str, str]:
        """
        Create an AFTER snapshot after an operation completes.

        Args:
            snapshot_id: Snapshot ID from create_snapshot_before()

        Returns:
            Dictionary with snapshot info (backup_path, snapshot_dir)
        """
        try:
            from utils.backup import create_snapshot_after
            result = create_snapshot_after(self.db.db_path, snapshot_id)
            return result
        except Exception as e:
            logger.error("Failed to create AFTER snapshot: %s", str(e))
            return {}

    def list_recent_snapshots(self, limit: int = 10) -> List[Dict]:
        """
        List recent auto-snapshots with their metadata.

        Args:
            limit: Maximum number of snapshots to return

        Returns:
            List of dictionaries with snapshot metadata
        """
        try:
            from utils.backup import list_snapshots
            snapshots = list_snapshots(self.db.db_path, limit)
            return snapshots
        except Exception as e:
            logger.error("Failed to list snapshots: %s", str(e))
            return []

    def cleanup_old_snapshots(self, keep_count: int = 5) -> int:
        """
        Remove old auto-snapshots, keeping only the most recent N.

        Args:
            keep_count: Number of recent snapshots to keep

        Returns:
            Number of snapshots deleted
        """
        try:
            from utils.backup import cleanup_old_snapshots
            deleted_count = cleanup_old_snapshots(self.db.db_path, keep_count)
            logger.info("Snapshot cleanup completed: %d old snapshots deleted", deleted_count)
            return deleted_count
        except Exception as e:
            logger.error("Failed to cleanup old snapshots: %s", str(e))
            return 0

    def restore_from_snapshot(self, snapshot_id: str, use_before: bool = True) -> bool:
        """
        Restore the database from a specific snapshot.

        Args:
            snapshot_id: Snapshot ID to restore from
            use_before: If True, restore from 'before' snapshot; if False, restore from 'after'

        Returns:
            True if restore successful, False otherwise
        """
        try:
            from utils.backup import restore_from_snapshot
            result = restore_from_snapshot(self.db.db_path, snapshot_id, use_before)
            if result:
                logger.info("Database restored from snapshot %s", snapshot_id)
            return result
        except Exception as e:
            logger.error("Failed to restore from snapshot: %s", str(e))
            return False

