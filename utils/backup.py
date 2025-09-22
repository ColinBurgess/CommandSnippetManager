"""
Backup and restore functionality for the Command Snippet Management Application.
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
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
