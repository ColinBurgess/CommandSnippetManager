"""
Backup and restore dialog for the Command Snippet Management Application.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QFileDialog, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt
from utils.backup import export_snippets_to_json, import_snippets_from_json
from utils.logger import get_logger

logger = get_logger(__name__)

class BackupDialog(QDialog):
    """Dialog for backup and restore operations."""

    def __init__(self, db_connection, parent=None):
        """Initialize the backup dialog."""
        super().__init__(parent)
        self.db_connection = db_connection
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Backup and Restore")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Export section
        export_group = QVBoxLayout()
        export_label = QLabel("Export Snippets:")
        export_label.setStyleSheet("font-weight: bold;")
        export_button = QPushButton("Export to JSON")
        export_button.clicked.connect(self.export_snippets)
        export_group.addWidget(export_label)
        export_group.addWidget(export_button)

        # Import section
        import_group = QVBoxLayout()
        import_label = QLabel("Import Snippets:")
        import_label.setStyleSheet("font-weight: bold;")

        self.replace_checkbox = QCheckBox("Replace existing snippets")
        self.replace_checkbox.setToolTip(
            "If checked, all existing snippets will be removed before import"
        )

        import_button = QPushButton("Import from JSON")
        import_button.clicked.connect(self.import_snippets)

        import_group.addWidget(import_label)
        import_group.addWidget(self.replace_checkbox)
        import_group.addWidget(import_button)

        # Add sections to main layout
        layout.addLayout(export_group)
        layout.addSpacing(20)
        layout.addLayout(import_group)
        layout.addSpacing(20)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def export_snippets(self):
        """Export snippets to a JSON file."""
        try:
            # Get save file location
            filename = f"snippets_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Snippets Backup",
                filename,
                "JSON Files (*.json)"
            )

            if not file_path:
                return

            # Export data
            json_data = export_snippets_to_json(self.db_connection)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)

            logger.info("Successfully exported snippets to %s", file_path)
            QMessageBox.information(
                self,
                "Export Successful",
                f"Snippets were successfully exported to:\n{file_path}"
            )

        except Exception as e:
            logger.error("Export failed: %s", str(e))
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export snippets:\n{str(e)}"
            )

    def import_snippets(self):
        """Import snippets from a JSON file."""
        try:
            # Get file to import
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Snippets Backup",
                "",
                "JSON Files (*.json)"
            )

            if not file_path:
                return

            # Confirm if replacing existing
            if self.replace_checkbox.isChecked():
                reply = QMessageBox.warning(
                    self,
                    "Confirm Replace",
                    "This will delete all existing snippets. Continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            # Read and import data
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = f.read()

            stats = import_snippets_from_json(
                self.db_connection,
                json_data,
                self.replace_checkbox.isChecked()
            )

            logger.info("Import completed: %s", stats)
            QMessageBox.information(
                self,
                "Import Successful",
                f"Import completed:\n"
                f"- Total snippets: {stats['total']}\n"
                f"- Imported: {stats['imported']}\n"
                f"- Failed: {stats['failed']}\n"
                f"- Skipped: {stats['skipped']}"
            )

        except Exception as e:
            logger.error("Import failed: %s", str(e))
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import snippets:\n{str(e)}"
            )
