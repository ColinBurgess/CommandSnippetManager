"""
Database operations for the Command Snippet Management Application.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple, Any
from .models import Snippet
from .migrations import DatabaseMigration
from utils.logger import get_logger

logger = get_logger(__name__)


class Database:
    """
    Handles all database operations for command snippets.
    """

    def __init__(self, db_path: str):
        """
        Initialize database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None

        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def connect(self) -> None:
        """Establish database connection and create cursor."""
        logger.debug("Attempting to connect to database at: %s", self.db_path)
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected to database")
        except sqlite3.Error as e:
            logger.error("Failed to connect to database: %s", str(e))
            raise Exception(f"Failed to connect to database: {e}")

    def close(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def create_tables(self) -> None:
        """Create the snippets table if it doesn't exist and run any pending migrations."""
        logger.debug("Initializing database schema")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            command_text TEXT NOT NULL,
            tags TEXT,
            last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """

        try:
            # Create initial table if it doesn't exist
            logger.info("Creating snippets table if not exists")
            self._execute_query(create_table_sql)
            self.connection.commit()

            # Run migrations
            logger.info("Checking and applying any pending migrations")
            migration = DatabaseMigration(self.connection)
            migration.ensure_latest_version()

            logger.info("Database schema initialization completed successfully")
        except Exception as e:
            logger.error("Failed to initialize database schema: %s", str(e))
            raise Exception(f"Failed to initialize database schema: {e}")

    def _execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetchone: bool = False,
        fetchall: bool = False
    ) -> Any:
        """
        Helper method for executing database queries with error handling.

        Args:
            query: SQL query string
            params: Query parameters tuple
            fetchone: Whether to fetch one result
            fetchall: Whether to fetch all results

        Returns:
            Query results or None
        """
        try:
            # Log query details at debug level
            if params:
                logger.debug("Executing query: %s with params: %s", query.strip(), params)
                self.cursor.execute(query, params)
            else:
                logger.debug("Executing query: %s", query.strip())
                self.cursor.execute(query)

            if fetchone:
                result = self.cursor.fetchone()
                logger.debug("Query returned single result: %s", result is not None)
                return result
            elif fetchall:
                results = self.cursor.fetchall()
                logger.debug("Query returned %d results", len(results))
                return results
            else:
                lastrowid = self.cursor.lastrowid
                logger.debug("Query affected row with ID: %d", lastrowid)
                return lastrowid

        except sqlite3.Error as e:
            logger.error("Database query failed: %s\nQuery: %s\nParams: %s",
                        str(e), query.strip(), params)
            raise Exception(f"Database query failed: {e}")

    def insert_snippet(self, snippet: Snippet) -> int:
        """
        Insert a new snippet into the database.

        Args:
            snippet: Snippet object to insert

        Returns:
            ID of the inserted snippet

        Note:
            Multiple snippets can now have the same name
        """
        logger.info("Inserting new snippet: %s", snippet.name)
        logger.debug("Snippet details: %s", snippet.to_dict())
        insert_sql = """
        INSERT INTO snippets (name, description, command_text, tags, last_used, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        params = (
            snippet.name,
            snippet.description,
            snippet.command_text,
            snippet.tags,
            snippet.last_used.isoformat(),
            snippet.created_at.isoformat()
        )

        try:
            snippet_id = self._execute_query(insert_sql, params)
            self.connection.commit()
            logger.info("Successfully inserted snippet with ID: %d", snippet_id)
            return snippet_id
        except Exception as e:
            logger.error("Failed to insert snippet '%s': %s", snippet.name, str(e))
            self.connection.rollback()
            raise Exception(f"Failed to insert snippet: {e}")

    def get_all_snippets(self) -> List[Snippet]:
        """
        Retrieve all snippets from the database, ordered by last_used DESC.

        Returns:
            List of Snippet objects
        """
        logger.debug("Retrieving all snippets from database at: %s", self.db_path)
        select_sql = """
        SELECT id, name, description, command_text, tags, last_used, created_at
        FROM snippets
        ORDER BY last_used DESC
        """

        try:
            rows = self._execute_query(select_sql, fetchall=True)
            snippets = []

            for row in rows:
                try:
                    snippet = Snippet(
                        snippet_id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        command_text=row['command_text'],
                        tags=row['tags'],
                        last_used=datetime.fromisoformat(row['last_used']) if row['last_used'] else None,
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                    )
                    snippets.append(snippet)
                except Exception as row_error:
                    logger.error("Failed to process snippet row: %s. Error: %s", row, str(row_error))

            logger.info("Retrieved %d snippets from database", len(snippets))
            if snippets:
                logger.debug("First snippet in list: %s", snippets[0].to_dict())
            return snippets

        except Exception as e:
            logger.error("Failed to retrieve snippets: %s", str(e))
            raise Exception(f"Failed to retrieve snippets: {e}")

    def get_snippet_by_id(self, snippet_id: int) -> Optional[Snippet]:
        """
        Retrieve a specific snippet by its ID.

        Args:
            snippet_id: ID of the snippet to retrieve

        Returns:
            Snippet object or None if not found
        """
        select_sql = """
        SELECT id, name, description, command_text, tags, last_used, created_at
        FROM snippets
        WHERE id = ?
        """

        try:
            row = self._execute_query(select_sql, (snippet_id,), fetchone=True)

            if row:
                return Snippet(
                    snippet_id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    command_text=row['command_text'],
                    tags=row['tags'],
                    last_used=datetime.fromisoformat(row['last_used']) if row['last_used'] else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )

            return None

        except Exception as e:
            raise Exception(f"Failed to retrieve snippet: {e}")

    def update_snippet(self, snippet: Snippet) -> bool:
        """
        Update an existing snippet in the database.

        Args:
            snippet: Snippet object with updated data

        Returns:
            True if successful, False otherwise
        """
        update_sql = """
        UPDATE snippets
        SET name = ?, description = ?, command_text = ?, tags = ?
        WHERE id = ?
        """

        params = (
            snippet.name,
            snippet.description,
            snippet.command_text,
            snippet.tags,
            snippet.id
        )

        try:
            self._execute_query(update_sql, params)
            self.connection.commit()
            return True

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to update snippet: {e}")

    def delete_snippet(self, snippet_id: int) -> bool:
        """
        Delete a snippet from the database.

        Args:
            snippet_id: ID of the snippet to delete

        Returns:
            True if successful, False otherwise
        """
        delete_sql = "DELETE FROM snippets WHERE id = ?"

        try:
            self._execute_query(delete_sql, (snippet_id,))
            self.connection.commit()
            return True

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to delete snippet: {e}")

    def search_snippets(self, query: str = "", tags_list: Optional[List[str]] = None) -> List[Snippet]:
        """
        Search for snippets based on query and tags.

        Args:
            query: Search term to match against name, description, and command_text
            tags_list: List of tags to filter by

        Returns:
            List of matching Snippet objects
        """
        base_sql = """
        SELECT id, name, description, command_text, tags, last_used, created_at
        FROM snippets
        WHERE 1=1
        """

        params = []

        # Add text search condition
        if query.strip():
            base_sql += """
            AND (
                name LIKE ? OR
                description LIKE ? OR
                command_text LIKE ? OR
                tags LIKE ?
            )
            """
            search_term = f"%{query.strip()}%"
            params.extend([search_term, search_term, search_term, search_term])

        # Add tags filter condition
        if tags_list:
            tag_conditions = []
            for tag in tags_list:
                if tag.strip():
                    tag_conditions.append("tags LIKE ?")
                    params.append(f"%{tag.strip()}%")

            if tag_conditions:
                base_sql += f" AND ({' OR '.join(tag_conditions)})"

        base_sql += " ORDER BY last_used DESC"

        try:
            rows = self._execute_query(base_sql, tuple(params), fetchall=True)
            snippets = []

            for row in rows:
                snippet = Snippet(
                    snippet_id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    command_text=row['command_text'],
                    tags=row['tags'],
                    last_used=datetime.fromisoformat(row['last_used']) if row['last_used'] else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                snippets.append(snippet)

            return snippets

        except Exception as e:
            raise Exception(f"Failed to search snippets: {e}")

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if a snippet with the given name already exists.

        Args:
            name: Name to check
            exclude_id: Optional ID to exclude from the check (useful for updates)

        Returns:
            True if the name exists, False otherwise
        """
        select_sql = "SELECT id FROM snippets WHERE name = ?"
        params = [name]

        if exclude_id is not None:
            select_sql += " AND id != ?"
            params.append(exclude_id)

        try:
            row = self._execute_query(select_sql, tuple(params), fetchone=True)
            return row is not None
        except Exception as e:
            raise Exception(f"Failed to check name existence: {e}")

    def update_last_used(self, snippet_id: int) -> bool:
        """
        Update the last_used timestamp for a snippet.

        Args:
            snippet_id: ID of the snippet to update

        Returns:
            True if successful, False otherwise
        """
        update_sql = "UPDATE snippets SET last_used = ? WHERE id = ?"

        try:
            self._execute_query(update_sql, (datetime.now().isoformat(), snippet_id))
            self.connection.commit()
            return True

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to update last_used: {e}")
