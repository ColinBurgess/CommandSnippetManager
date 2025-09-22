"""
Main entry point for the Command Snippet Management Application.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from utils.logger import get_logger

logger = get_logger(__name__)

from config import DB_PATH, APP_NAME
from db.database import Database
from core.snippet_manager import SnippetManager
from ui.main_window import MainWindow


def main():
    """Main application entry point."""
    logger.info("Starting Command Snippet Manager application")

    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    logger.debug("Application name set to: %s", APP_NAME)

    # Set application style for better macOS integration
    app.setStyle('Fusion')
    logger.debug("Application style set to Fusion")

    try:
        # Initialize database
        logger.info("Initializing database at: %s", DB_PATH)
        database = Database(DB_PATH)
        database.connect()
        # Initialize database schema
        database.create_tables()
        logger.info("Database initialization completed")

        # Initialize snippet manager
        logger.debug("Initializing snippet manager")
        snippet_manager = SnippetManager(database)

        # Create and show main window
        logger.debug("Creating main window")
        main_window = MainWindow(snippet_manager)
        main_window.show()
        logger.info("Application window displayed")

        # Start the Qt event loop
        logger.debug("Starting Qt event loop")
        exit_code = app.exec()
        logger.info("Application event loop ended with code: %d", exit_code)

        # Clean up
        logger.debug("Cleaning up resources")
        database.close()
        logger.info("Application shutdown complete")

        return exit_code

    except Exception as e:
        # Show error dialog if initialization fails
        error_msg = f"Failed to initialize application:\n\n{str(e)}"
        logger.critical("Application initialization failed: %s", str(e), exc_info=True)

        # Try to show QMessageBox, fallback to print if that fails
        try:
            QMessageBox.critical(None, "Application Error", error_msg)
        except Exception as dialog_error:
            logger.error("Failed to show error dialog: %s", str(dialog_error))
            print(f"CRITICAL ERROR: {error_msg}")

        return 1


if __name__ == "__main__":
    sys.exit(main())
