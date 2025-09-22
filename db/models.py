"""
Data models for the Command Snippet Management Application.
"""

from datetime import datetime
from typing import Optional


class Snippet:
    """
    Represents a command snippet with all its metadata.
    """

    def __init__(
        self,
        name: str,
        command_text: str,
        description: str = "",
        tags: str = "",
        snippet_id: Optional[int] = None,
        last_used: Optional[datetime] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a Snippet object.

        Args:
            name: Short, descriptive name for the snippet
            command_text: The actual command to execute
            description: Longer description of the snippet's purpose
            tags: Comma-separated tags for categorization
            snippet_id: Unique identifier (set by database)
            last_used: Timestamp of last usage
            created_at: Timestamp of creation
        """
        self.id = snippet_id
        self.name = name
        self.description = description
        self.command_text = command_text
        self.tags = tags
        self.last_used = last_used or datetime.now()
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """
        Convert the snippet to a dictionary representation.

        Returns:
            Dictionary containing all snippet attributes
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'command_text': self.command_text,
            'tags': self.tags,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Snippet':
        """
        Create a Snippet object from a dictionary.

        Args:
            data: Dictionary containing snippet data

        Returns:
            New Snippet instance
        """
        return cls(
            snippet_id=data.get('id'),
            name=data['name'],
            description=data.get('description', ''),
            command_text=data['command_text'],
            tags=data.get('tags', ''),
            last_used=datetime.fromisoformat(data['last_used']) if data.get('last_used') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )

    def get_tags_list(self) -> list:
        """
        Get tags as a list, splitting by comma and trimming whitespace.

        Returns:
            List of tag strings
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def __str__(self) -> str:
        """String representation of the snippet."""
        return f"Snippet(id={self.id}, name='{self.name}')"

    def __repr__(self) -> str:
        """Detailed string representation of the snippet."""
        return (f"Snippet(id={self.id}, name='{self.name}', "
                f"description='{self.description[:50]}...', "
                f"tags='{self.tags}')")
