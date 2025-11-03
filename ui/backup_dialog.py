"""
Backup and restore dialog for the Command Snippet Management Application.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QFileDialog, QMessageBox, QCheckBox, QTabWidget, QWidget,
                            QListWidget, QListWidgetItem, QScrollArea)
from PyQt6.QtCore import Qt
from utils.backup import export_snippets_to_json, import_snippets_from_json
from utils.logger import get_logger

logger = get_logger(__name__)

class BackupDialog(QDialog):
    """Dialog for backup and restore operations."""

    def __init__(self, db_connection, snippet_manager=None, parent=None):
        """Initialize the backup dialog."""
        super().__init__(parent)
        self.db_connection = db_connection
        self.snippet_manager = snippet_manager
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Backup and Restore")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Create tabs: Database Backup and JSON Export/Import
        tabs = QTabWidget()

        # Tab 1: Database Backup/Restore
        db_tab = QWidget()
        db_layout = QVBoxLayout(db_tab)

        db_label = QLabel("Database Backup & Restore")
        db_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        db_layout.addWidget(db_label)

        db_info = QLabel(
            "Create a complete backup of your database or restore from a previous backup.\n"
            "Backups are timestamped and stored in the data/ directory."
        )
        db_info.setWordWrap(True)
        db_info.setStyleSheet("color: #999; font-size: 11px; margin: 10px 0;")
        db_layout.addWidget(db_info)

        # Create backup button
        create_backup_button = QPushButton("💾 Create Backup Now")
        create_backup_button.clicked.connect(self.create_database_backup)
        db_layout.addWidget(create_backup_button)

        # Restore backup button
        restore_backup_button = QPushButton("📥 Restore from Backup")
        restore_backup_button.clicked.connect(self.restore_database_backup)
        db_layout.addWidget(restore_backup_button)

        # List backups button
        list_backups_button = QPushButton("📋 List Available Backups")
        list_backups_button.clicked.connect(self.list_backups)
        db_layout.addWidget(list_backups_button)

        db_layout.addSpacing(20)
        tabs.addTab(db_tab, "Database Backup")

        # Tab 2: JSON Export/Import
        json_tab = QWidget()
        json_layout = QVBoxLayout(json_tab)

        json_label = QLabel("Export/Import Snippets as JSON")
        json_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        json_layout.addWidget(json_label)

        json_info = QLabel(
            "Export snippets to a portable JSON file or import from a JSON file.\n"
            "Useful for sharing or migrating snippets."
        )
        json_info.setWordWrap(True)
        json_info.setStyleSheet("color: #999; font-size: 11px; margin: 10px 0;")
        json_layout.addWidget(json_info)

        # Export section
        export_group = QVBoxLayout()
        export_label = QLabel("Export Snippets to JSON:")
        export_label.setStyleSheet("font-weight: bold;")
        export_button = QPushButton("📤 Export to JSON")
        export_button.clicked.connect(self.export_snippets)
        export_group.addWidget(export_label)
        export_group.addWidget(export_button)

        # Import section
        import_group = QVBoxLayout()
        import_label = QLabel("Import Snippets from JSON:")
        import_label.setStyleSheet("font-weight: bold;")

        self.replace_checkbox = QCheckBox("Replace existing snippets")
        self.replace_checkbox.setToolTip(
            "If checked, all existing snippets will be removed before import"
        )

        import_button = QPushButton("📥 Import from JSON")
        import_button.clicked.connect(self.import_snippets)

        import_group.addWidget(import_label)
        import_group.addWidget(self.replace_checkbox)
        import_group.addWidget(import_button)

        json_layout.addLayout(export_group)
        json_layout.addSpacing(15)
        json_layout.addLayout(import_group)
        json_layout.addStretch()

        tabs.addTab(json_tab, "JSON Export/Import")

        # Tab 3: Change Snapshots
        snapshots_tab = QWidget()
        snapshots_layout = QVBoxLayout(snapshots_tab)

        snapshots_label = QLabel("Change Snapshots")
        snapshots_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        snapshots_layout.addWidget(snapshots_label)

        snapshots_info = QLabel(
            "Automatic before/after snapshots are created when you add, update, or delete snippets.\n"
            "Select a snapshot below to view details or restore from a previous state."
        )
        snapshots_info.setWordWrap(True)
        snapshots_info.setStyleSheet("color: #999; font-size: 11px; margin: 10px 0;")
        snapshots_layout.addWidget(snapshots_info)

        # Snapshots list
        self.snapshots_list = QListWidget()
        self.snapshots_list.itemSelectionChanged.connect(self.on_snapshot_selected)
        snapshots_layout.addWidget(self.snapshots_list)

        # Snapshot details
        self.snapshot_details = QLabel("Select a snapshot to view details")
        self.snapshot_details.setWordWrap(True)
        self.snapshot_details.setStyleSheet("color: #666; font-size: 10px; padding: 10px; background-color: #f5f5f5;")
        snapshots_layout.addWidget(self.snapshot_details)

        # Snapshot action buttons
        snapshot_buttons_layout = QHBoxLayout()

        restore_snapshot_button = QPushButton("📥 Restore from This Snapshot")
        restore_snapshot_button.clicked.connect(self.restore_from_snapshot)
        snapshot_buttons_layout.addWidget(restore_snapshot_button)

        refresh_snapshots_button = QPushButton("🔄 Refresh List")
        refresh_snapshots_button.clicked.connect(self.load_snapshots)
        snapshot_buttons_layout.addWidget(refresh_snapshots_button)

        snapshots_layout.addLayout(snapshot_buttons_layout)

        tabs.addTab(snapshots_tab, "Change Snapshots")

        layout.addWidget(tabs)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def create_database_backup(self):
        """Create a backup of the database."""
        try:
            if not self.snippet_manager:
                QMessageBox.warning(self, "Error", "Snippet manager not available")
                return

            backup_path = self.snippet_manager.create_backup()
            file_size_mb = os.path.getsize(backup_path) / (1024 * 1024)

            QMessageBox.information(
                self,
                "Backup Created",
                f"Database backup successfully created:\n\n"
                f"Location: {backup_path}\n"
                f"Size: {file_size_mb:.2f} MB\n\n"
                f"You can restore from this backup at any time."
            )
            logger.info("Database backup created: %s", backup_path)

        except Exception as e:
            logger.error("Failed to create database backup: %s", str(e))
            QMessageBox.critical(
                self,
                "Backup Failed",
                f"Failed to create database backup:\n{str(e)}"
            )

    def restore_database_backup(self):
        """Restore database from a backup file."""
        try:
            if not self.snippet_manager:
                QMessageBox.warning(self, "Error", "Snippet manager not available")
                return

            # Get backup file
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Database Backup to Restore",
                "",
                "Database Files (*.db);;All Files (*)"
            )

            if not file_path:
                return

            # Confirm restore (data will be overwritten)
            reply = QMessageBox.warning(
                self,
                "Confirm Restore",
                f"This will restore your database from the selected backup.\n\n"
                f"File: {os.path.basename(file_path)}\n\n"
                f"Your current database will be backed up before restore.\n"
                f"Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

            # Restore
            self.snippet_manager.restore_from_backup(file_path, keep_backup=True)

            QMessageBox.information(
                self,
                "Restore Successful",
                f"Database successfully restored from backup.\n\n"
                f"The window will now refresh to show the restored data."
            )
            logger.info("Database restored from: %s", file_path)

        except Exception as e:
            logger.error("Failed to restore database: %s", str(e))
            QMessageBox.critical(
                self,
                "Restore Failed",
                f"Failed to restore database:\n{str(e)}"
            )

    def list_backups(self):
        """List available backups."""
        try:
            if not self.snippet_manager:
                QMessageBox.warning(self, "Error", "Snippet manager not available")
                return

            backups = self.snippet_manager.list_available_backups()

            if not backups:
                QMessageBox.information(
                    self,
                    "No Backups",
                    "No backup files found in the data/ directory."
                )
                return

            # Format backup list
            backup_list = "Available backups:\n\n"
            for i, backup in enumerate(backups, 1):
                backup_list += f"{i}. {backup['name']}\n"
                backup_list += f"   Created: {backup['created']}\n"
                backup_list += f"   Size: {backup['size_mb']:.2f} MB\n\n"

            QMessageBox.information(
                self,
                "Available Backups",
                backup_list
            )
            logger.info("Listed %d backups", len(backups))

        except Exception as e:
            logger.error("Failed to list backups: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to list backups:\n{str(e)}"
            )

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

    def load_snapshots(self):
        """Load the list of available snapshots."""
        try:
            if not self.snippet_manager:
                QMessageBox.warning(self, "Error", "Snippet manager not available")
                return

            self.snapshots_list.clear()
            snapshots = self.snippet_manager.list_recent_snapshots(limit=20)

            if not snapshots:
                item = QListWidgetItem("No snapshots available yet")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.snapshots_list.addItem(item)
                return

            for snapshot in snapshots:
                operation = snapshot.get('operation', 'unknown').upper()
                snippet_name = snapshot.get('snippet_name', 'unknown')
                status = snapshot.get('status', 'unknown')
                timestamp = snapshot.get('before_timestamp', '').split('T')[0]  # Extract date

                display_text = f"[{operation}] {snippet_name} - {timestamp}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, snapshot)
                self.snapshots_list.addItem(item)

            logger.info("Loaded %d snapshots", len(snapshots))

        except Exception as e:
            logger.error("Failed to load snapshots: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load snapshots:\n{str(e)}"
            )

    def on_snapshot_selected(self):
        """Handle snapshot selection."""
        try:
            current_item = self.snapshots_list.currentItem()
            if not current_item:
                self.snapshot_details.setText("Select a snapshot to view details")
                return

            snapshot = current_item.data(Qt.ItemDataRole.UserRole)
            if not snapshot:
                return

            # Format snapshot details
            operation = snapshot.get('operation', 'unknown').upper()
            snippet_name = snapshot.get('snippet_name', 'unknown')
            before_time = snapshot.get('before_timestamp', 'unknown')
            after_time = snapshot.get('after_timestamp', 'unknown')
            status = snapshot.get('status', 'unknown')
            before_size = snapshot.get('before_size_mb', 0)
            after_size = snapshot.get('after_size_mb', 0)

            details = (
                f"<b>Snapshot Details:</b><br>"
                f"<b>Operation:</b> {operation}<br>"
                f"<b>Snippet:</b> {snippet_name}<br>"
                f"<b>Status:</b> {status.upper()}<br>"
                f"<b>Before Time:</b> {before_time}<br>"
                f"<b>After Time:</b> {after_time}<br>"
                f"<b>Before Size:</b> {before_size:.2f} MB<br>"
                f"<b>After Size:</b> {after_size:.2f} MB"
            )

            self.snapshot_details.setText(details)

        except Exception as e:
            logger.error("Error displaying snapshot details: %s", str(e))
            self.snapshot_details.setText("Error loading snapshot details")

    def restore_from_snapshot(self):
        """Restore database from selected snapshot."""
        try:
            current_item = self.snapshots_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Error", "Please select a snapshot to restore from")
                return

            snapshot = current_item.data(Qt.ItemDataRole.UserRole)
            if not snapshot:
                return

            snapshot_id = snapshot.get('snapshot_id', '')
            operation = snapshot.get('operation', 'unknown')
            snippet_name = snapshot.get('snippet_name', 'unknown')

            # Confirm restore
            reply = QMessageBox.question(
                self,
                "Confirm Restore from Snapshot",
                f"This will restore your database from this snapshot:\n\n"
                f"Operation: {operation.upper()}\n"
                f"Snippet: {snippet_name}\n"
                f"Time: {snapshot.get('before_timestamp', 'unknown')}\n\n"
                f"Your current database will be backed up before restore.\n"
                f"Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

            # Restore from BEFORE snapshot
            if not self.snippet_manager:
                QMessageBox.warning(self, "Error", "Snippet manager not available")
                return

            success = self.snippet_manager.restore_from_snapshot(snapshot_id, use_before=True)

            if success:
                QMessageBox.information(
                    self,
                    "Restore Successful",
                    "Database successfully restored from snapshot.\n\n"
                    "The window will now refresh to show the restored data."
                )
                logger.info("Database restored from snapshot %s", snapshot_id)
            else:
                QMessageBox.critical(
                    self,
                    "Restore Failed",
                    "Failed to restore from snapshot"
                )

        except Exception as e:
            logger.error("Failed to restore from snapshot: %s", str(e))
            QMessageBox.critical(
                self,
                "Restore Failed",
                f"Failed to restore from snapshot:\n{str(e)}"
            )

    def showEvent(self, event):
        """Load snapshots when the dialog is shown."""
        super().showEvent(event)
        # Load snapshots if we have a snippet manager
        if self.snippet_manager:
            self.load_snapshots()
