"""
Dialog for creating and editing command snippets.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from db.models import Snippet
from typing import Optional, Dict


class SnippetDialog(QDialog):
    """
    Dialog window for creating new snippets or editing existing ones.
    """

    def __init__(self, parent=None, snippet: Optional[Snippet] = None):
        """
        Initialize the snippet dialog.

        Args:
            parent: Parent widget
            snippet: Existing snippet to edit (None for new snippet)
        """
        super().__init__(parent)
        self.snippet = snippet
        self.is_editing = snippet is not None

        self._setup_ui()
        self._populate_fields()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the user interface elements."""
        # Set dialog properties
        title = "Edit Snippet" if self.is_editing else "New Snippet"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(600, 400)

        # Main layout
        layout = QVBoxLayout(self)

        # Form layout for input fields
        form_layout = QFormLayout()

        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a short, descriptive name...")
        form_layout.addRow("Name *:", self.name_edit)

        # Description field
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter a longer description of what this command does...")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)

        # Command text field
        self.command_edit = QTextEdit()
        self.command_edit.setPlaceholderText("Enter the command to execute...")
        self.command_edit.setMinimumHeight(120)
        form_layout.addRow("Command *:", self.command_edit)

        # Tags field
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Enter comma-separated tags (e.g., aws, docker, ssh)...")
        form_layout.addRow("Tags:", self.tags_edit)

        layout.addLayout(form_layout)

        # Add some spacing
        layout.addStretch()

        # Required fields note
        required_label = QLabel("* Required fields")
        required_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(required_label)

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(self.button_box)

        # Set focus to name field
        self.name_edit.setFocus()

    def _populate_fields(self):
        """Populate form fields if editing an existing snippet."""
        if self.snippet:
            self.name_edit.setText(self.snippet.name)
            self.description_edit.setPlainText(self.snippet.description)
            self.command_edit.setPlainText(self.snippet.command_text)
            self.tags_edit.setText(self.snippet.tags)

    def _connect_signals(self):
        """Connect signals to their corresponding slots."""
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)

        # Enable/disable save button based on required fields
        self.name_edit.textChanged.connect(self._validate_input)
        self.command_edit.textChanged.connect(self._validate_input)

        # Initial validation
        self._validate_input()

    def _validate_input(self):
        """Validate input and enable/disable save button accordingly."""
        name_valid = bool(self.name_edit.text().strip())
        command_valid = bool(self.command_edit.toPlainText().strip())

        save_button = self.button_box.button(QDialogButtonBox.StandardButton.Save)
        save_button.setEnabled(name_valid and command_valid)

    def _on_save(self):
        """Handle save button click with validation."""
        if self.validate_input():
            self.accept()

    def validate_input(self) -> bool:
        """
        Validate the input data.

        Returns:
            True if all required fields are valid, False otherwise
        """
        name = self.name_edit.text().strip()
        command_text = self.command_edit.toPlainText().strip()

        if not name:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Snippet name is required and cannot be empty."
            )
            self.name_edit.setFocus()
            return False

        if not command_text:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Command text is required and cannot be empty."
            )
            self.command_edit.setFocus()
            return False

        # Check for reasonable name length
        if len(name) > 100:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Snippet name is too long. Please keep it under 100 characters."
            )
            self.name_edit.setFocus()
            return False

        return True

    def get_snippet_data(self) -> Dict[str, str]:
        """
        Get the snippet data from the form fields.

        Returns:
            Dictionary containing the snippet data
        """
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'command_text': self.command_edit.toPlainText().strip(),
            'tags': self.tags_edit.text().strip()
        }

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Allow Ctrl+Enter to save
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if self.validate_input():
                self.accept()
        else:
            super().keyPressEvent(event)
