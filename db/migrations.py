"""
Database migration management for the Command Snippet Management Application.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseMigration:
    """Handles database schema migrations."""

    def __init__(self, connection: sqlite3.Connection):
        """
        Initialize migration manager.

        Args:
            connection: Active database connection
        """
        self.connection = connection
        self.cursor = connection.cursor()

    def _create_version_table(self) -> None:
        """Create the schema_version table if it doesn't exist."""
        create_version_table = """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        )
        """
        self.cursor.execute(create_version_table)
        self.connection.commit()

    def get_current_version(self) -> int:
        """Get the current schema version."""
        self._create_version_table()
        try:
            self.cursor.execute("SELECT MAX(version) FROM schema_version")
            version = self.cursor.fetchone()[0]
            return version if version is not None else 0
        except sqlite3.Error as e:
            logger.error("Failed to get schema version: %s", str(e))
            return 0

    def _backup_table(self, table_name: str) -> None:
        """
        Create a backup of a table.

        Args:
            table_name: Name of the table to backup
        """
        backup_name = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info("Creating backup of table %s as %s", table_name, backup_name)
        self.cursor.execute(f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}")
        self.connection.commit()

    def migrate_to_version_1(self) -> None:
        """
        Migrate database to version 1:
        - Remove UNIQUE constraint from name column
        - Preserve all existing data
        """
        logger.info("Starting migration to version 1")

        try:
            # Check if we need to migrate
            self.cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='snippets'")
            current_schema = self.cursor.fetchone()[0]

            if 'UNIQUE' in current_schema:
                logger.info("Found UNIQUE constraint, performing migration")

                # Backup current table
                self._backup_table('snippets')

                # Create new table without UNIQUE constraint
                self.cursor.execute("""
                CREATE TABLE snippets_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    command_text TEXT NOT NULL,
                    tags TEXT,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)

                # Copy data
                self.cursor.execute("INSERT INTO snippets_new SELECT * FROM snippets")

                # Drop old table and rename new one
                self.cursor.execute("DROP TABLE snippets")
                self.cursor.execute("ALTER TABLE snippets_new RENAME TO snippets")

                # Update schema version
                self.cursor.execute(
                    "INSERT INTO schema_version (version, description) VALUES (?, ?)",
                    (1, "Remove UNIQUE constraint from name column")
                )

                self.connection.commit()
                logger.info("Migration to version 1 completed successfully")
            else:
                logger.info("UNIQUE constraint not found, no migration needed")
                # Still record this version if it's not recorded
                if self.get_current_version() < 1:
                    self.cursor.execute(
                        "INSERT INTO schema_version (version, description) VALUES (?, ?)",
                        (1, "Schema already at version 1")
                    )
                    self.connection.commit()

        except Exception as e:
            logger.error("Migration failed: %s", str(e))
            self.connection.rollback()
            raise

    def ensure_latest_version(self) -> None:
        """
        Ensure the database is at the latest version.
        Add new migration methods here as needed.
        """
        current_version = self.get_current_version()
        logger.info("Current database version: %d", current_version)

        if current_version < 1:
            self.migrate_to_version_1()

        # Add future migrations here
        # if current_version < 2:
        #     self.migrate_to_version_2()
