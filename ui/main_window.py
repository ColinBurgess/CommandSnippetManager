"""
Main application window for the Command Snippet Management Application.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QPushButton, QMessageBox, QStatusBar,
    QHeaderView, QAbstractItemView, QSplitter, QTextEdit, QLabel,
    QFrame, QToolBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction, QIcon
from datetime import datetime
from typing import Optional

from core.snippet_manager import SnippetManager
from ui.snippet_dialog import SnippetDialog
from ui.backup_dialog import BackupDialog
from utils import copy_to_clipboard, execute_in_terminal_macos
from db.models import Snippet


class MainWindow(QMainWindow):
    """
    Main application window containing the snippet list and controls.
    """

    def __init__(self, snippet_manager: SnippetManager):
        """
        Initialize the main window.

        Args:
            snippet_manager: SnippetManager instance for data operations
        """
        super().__init__()
        self.snippet_manager = snippet_manager
        self.current_snippets = []

        self._setup_ui()
        self._connect_signals()
        self.load_snippets()

    def _setup_ui(self):
        """Set up the user interface."""
        # Window properties
        self.setWindowTitle("Command Snippet Manager")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 800)

        # Create menu bar
        self._create_menu_bar()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create toolbar
        self._create_toolbar()

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search snippets by name, description, command, or tags...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        main_layout.addLayout(search_layout)

        # Create splitter for table and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - snippet list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Snippets table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Description", "Tags", "Last Used"])

        # Configure table
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Description
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Tags
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Last Used

        left_layout.addWidget(self.table)

        # Right side - command preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Preview header
        preview_label = QLabel("Command Preview")
        preview_label.setFont(QFont("", 12, QFont.Weight.Bold))
        right_layout.addWidget(preview_label)

        # Command text display
        self.command_preview = QTextEdit()
        self.command_preview.setReadOnly(True)
        self.command_preview.setFont(QFont("Courier", 10))
        self.command_preview.setPlaceholderText("Select a snippet to preview its command...")
        right_layout.addWidget(self.command_preview)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 300])  # Initial sizes

        main_layout.addWidget(splitter)

        # Button layout
        button_layout = QHBoxLayout()

        # Action buttons
        self.new_button = QPushButton("New Snippet")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.copy_button = QPushButton("Copy Command")
        self.execute_button = QPushButton("Execute")

        # Style buttons
        self.new_button.setDefault(True)
        self.copy_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        self.execute_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
        self.delete_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")

        # Initially disable buttons that require selection
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.execute_button.setEnabled(False)

        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.execute_button)

        main_layout.addLayout(button_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.show_status_message("Ready")

    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # Backup submenu
        backup_menu = file_menu.addMenu("Backup")

        backup_action = QAction("Backup/Restore...", self)
        backup_action.setStatusTip("Export or import snippets")
        backup_action.triggered.connect(self.show_backup_dialog)
        backup_menu.addAction(backup_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def show_backup_dialog(self):
        """Show the backup/restore dialog."""
        dialog = BackupDialog(self.snippet_manager.db.connection, self)
        dialog.exec()
        # Refresh snippets after backup/restore
        self.load_snippets()

    def _create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.load_snippets)
        toolbar.addAction(refresh_action)

        toolbar.addSeparator()

        # Quick actions
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_snippet)
        toolbar.addAction(new_action)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_command)
        toolbar.addAction(copy_action)

        execute_action = QAction("Execute", self)
        execute_action.setShortcut("Ctrl+E")
        execute_action.triggered.connect(self.execute_command)
        toolbar.addAction(execute_action)

    def _connect_signals(self):
        """Connect signals to their corresponding slots."""
        # Search functionality
        self.search_edit.textChanged.connect(self.filter_snippets)

        # Button clicks
        self.new_button.clicked.connect(self.on_new_snippet)
        self.edit_button.clicked.connect(self.on_edit_snippet)
        self.delete_button.clicked.connect(self.on_delete_snippet)
        self.copy_button.clicked.connect(self.copy_command)
        self.execute_button.clicked.connect(self.execute_command)

        # Table selection changes
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_edit_snippet)

    def _on_selection_changed(self):
        """Handle table selection changes."""
        has_selection = bool(self.get_selected_snippet_id())

        # Enable/disable buttons based on selection
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.copy_button.setEnabled(has_selection)
        self.execute_button.setEnabled(has_selection)

        # Update command preview
        self._update_command_preview()

    def _update_command_preview(self):
        """Update the command preview panel."""
        snippet_id = self.get_selected_snippet_id()
        if snippet_id:
            try:
                snippet = self.snippet_manager.get_snippet_details(snippet_id)
                if snippet:
                    self.command_preview.setPlainText(snippet.command_text)
                else:
                    self.command_preview.clear()
            except Exception as e:
                self.command_preview.setPlainText(f"Error loading command: {e}")
        else:
            self.command_preview.clear()

    def load_snippets(self, search_term: str = "", tags_filter: str = ""):
        """
        Load and display snippets in the table.

        Args:
            search_term: Search term to filter snippets
            tags_filter: Tags to filter by
        """
        try:
            # Get snippets from manager
            if search_term or tags_filter:
                snippets = self.snippet_manager.find_snippets(search_term, tags_filter)
            else:
                snippets = self.snippet_manager.get_all_snippets()

            self.current_snippets = snippets

            # Clear and populate table
            self.table.setRowCount(len(snippets))

            for row, snippet in enumerate(snippets):
                # Name
                name_item = QTableWidgetItem(snippet.name)
                name_item.setData(Qt.ItemDataRole.UserRole, snippet.id)  # Store ID
                self.table.setItem(row, 0, name_item)

                # Description
                description = snippet.description[:100] + "..." if len(snippet.description) > 100 else snippet.description
                self.table.setItem(row, 1, QTableWidgetItem(description))

                # Tags
                self.table.setItem(row, 2, QTableWidgetItem(snippet.tags))

                # Last Used
                if snippet.last_used:
                    last_used_str = snippet.last_used.strftime("%Y-%m-%d %H:%M")
                else:
                    last_used_str = "Never"
                self.table.setItem(row, 3, QTableWidgetItem(last_used_str))

            # Update status
            count = len(snippets)
            if search_term:
                self.show_status_message(f"Found {count} snippet(s) matching '{search_term}'")
            else:
                self.show_status_message(f"Loaded {count} snippet(s)")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load snippets: {e}")
            self.show_status_message("Error loading snippets")

    def filter_snippets(self):
        """Filter snippets based on search text."""
        search_text = self.search_edit.text().strip()
        self.load_snippets(search_term=search_text)

    def get_selected_snippet_id(self) -> Optional[int]:
        """
        Get the ID of the currently selected snippet.

        Returns:
            Snippet ID or None if no selection
        """
        current_row = self.table.currentRow()
        if current_row >= 0:
            name_item = self.table.item(current_row, 0)
            if name_item:
                return name_item.data(Qt.ItemDataRole.UserRole)
        return None

    def on_new_snippet(self):
        """Handle new snippet button click."""
        dialog = SnippetDialog(self)
        if dialog.exec() == SnippetDialog.DialogCode.Accepted:
            data = dialog.get_snippet_data()
            try:
                self.snippet_manager.add_snippet(
                    data['name'],
                    data['description'],
                    data['command_text'],
                    data['tags']
                )
                self.load_snippets()
                self.show_status_message(f"Snippet '{data['name']}' created successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create snippet: {e}")

    def on_edit_snippet(self):
        """Handle edit snippet button click."""
        snippet_id = self.get_selected_snippet_id()
        if not snippet_id:
            return

        try:
            snippet = self.snippet_manager.get_snippet_details(snippet_id)
            if snippet:
                dialog = SnippetDialog(self, snippet)
                if dialog.exec() == SnippetDialog.DialogCode.Accepted:
                    data = dialog.get_snippet_data()
                    self.snippet_manager.update_snippet(
                        snippet_id,
                        data['name'],
                        data['description'],
                        data['command_text'],
                        data['tags']
                    )
                    self.load_snippets()
                    self.show_status_message(f"Snippet '{data['name']}' updated successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit snippet: {e}")

    def on_delete_snippet(self):
        """Handle delete snippet button click."""
        snippet_id = self.get_selected_snippet_id()
        if not snippet_id:
            return

        try:
            snippet = self.snippet_manager.get_snippet_details(snippet_id)
            if snippet:
                reply = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    f"Are you sure you want to delete the snippet '{snippet.name}'?\n\nThis action cannot be undone.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.snippet_manager.delete_snippet(snippet_id)
                    self.load_snippets()
                    self.show_status_message(f"Snippet '{snippet.name}' deleted successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete snippet: {e}")

    def copy_command(self):
        """Copy the selected snippet's command to clipboard."""
        snippet_id = self.get_selected_snippet_id()
        if not snippet_id:
            return

        try:
            snippet = self.snippet_manager.get_snippet_details(snippet_id)
            if snippet:
                copy_to_clipboard(snippet.command_text)
                self.snippet_manager.record_usage(snippet_id)
                self.load_snippets()  # Refresh to update last_used
                self.show_status_message(f"Command copied to clipboard: {snippet.name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy command: {e}")

    def execute_command(self):
        """Execute the selected snippet's command."""
        snippet_id = self.get_selected_snippet_id()
        if not snippet_id:
            return

        try:
            snippet = self.snippet_manager.get_snippet_details(snippet_id)
            if snippet:
                # Confirm execution
                reply = QMessageBox.question(
                    self,
                    "Confirm Execution",
                    f"Execute command '{snippet.name}'?\n\nCommand:\n{snippet.command_text}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # Execute command in terminal
                    success, stdout, stderr = execute_in_terminal_macos(snippet.command_text)

                    if success:
                        self.snippet_manager.record_usage(snippet_id)
                        self.load_snippets()  # Refresh to update last_used
                        self.show_status_message(f"Command executed: {snippet.name}")
                    else:
                        QMessageBox.warning(
                            self,
                            "Execution Error",
                            f"Failed to execute command:\n{stderr}"
                        )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute command: {e}")

    def show_status_message(self, message: str, timeout: int = 3000):
        """
        Show a message in the status bar.

        Args:
            message: Message to display
            timeout: Timeout in milliseconds (0 for permanent)
        """
        self.status_bar.showMessage(message, timeout)
