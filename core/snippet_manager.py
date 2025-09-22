"""
Business logic layer for managing command snippets.
"""

from typing import List, Optional
from datetime import datetime
from db.database import Database
from db.models import Snippet


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
            snippet_id = self.db.insert_snippet(snippet)
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
            return self.db.update_snippet(updated_snippet)
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
            return self.db.delete_snippet(snippet_id)
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
