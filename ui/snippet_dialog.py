"""
Dialog for creating and editing command snippets.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from db.models import Snippet
from ui.modern_dark_theme import ModernDarkTheme
from ui.modern_widgets import ModernFrame
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
        title = "✨ Edit Snippet" if self.is_editing else "✨ New Snippet"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(650, 500)

        # Main layout with improved spacing
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header_label = QLabel(title)
        header_label.setFont(QFont("", 18, QFont.Weight.Bold))
        header_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_primary']}; margin-bottom: 8px;")
        layout.addWidget(header_label)

        # Content frame
        content_frame = ModernFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Form layout for input fields
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(12)

        # Name field
        name_label = QLabel("Name *")
        name_label.setFont(QFont("", 12, QFont.Weight.Medium))
        name_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_primary']};")

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a short, descriptive name...")
        self.name_edit.setMinimumHeight(36)
        form_layout.addRow(name_label, self.name_edit)

        # Description field
        desc_label = QLabel("Description")
        desc_label.setFont(QFont("", 12, QFont.Weight.Medium))
        desc_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_primary']};")

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter a longer description of what this command does...")
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setMinimumHeight(80)
        form_layout.addRow(desc_label, self.description_edit)

        # Command text field
        command_label = QLabel("Command *")
        command_label.setFont(QFont("", 12, QFont.Weight.Medium))
        command_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_primary']};")

        self.command_edit = QTextEdit()
        self.command_edit.setPlaceholderText("Enter the command to execute...")
        self.command_edit.setMinimumHeight(140)
        self.command_edit.setFont(QFont("SF Mono, Monaco, Cascadia Code, Roboto Mono", 12))
        form_layout.addRow(command_label, self.command_edit)

        # Tags field
        tags_label = QLabel("Tags")
        tags_label.setFont(QFont("", 12, QFont.Weight.Medium))
        tags_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_primary']};")

        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Enter comma-separated tags (e.g., aws, docker, ssh)...")
        self.tags_edit.setMinimumHeight(36)
        form_layout.addRow(tags_label, self.tags_edit)

        content_layout.addLayout(form_layout)
        layout.addWidget(content_frame)

        # Required fields note
        required_label = QLabel("* Required fields")
        required_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_muted']}; font-style: italic; font-size: 11px;")
        layout.addWidget(required_label)

        # Dialog buttons with modern styling
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )

        # Apply modern button styles
        button_styles = ModernDarkTheme.get_button_styles()
        save_button = self.button_box.button(QDialogButtonBox.StandardButton.Save)
        cancel_button = self.button_box.button(QDialogButtonBox.StandardButton.Cancel)

        if save_button:
            save_button.setStyleSheet(button_styles['primary'])
            save_button.setMinimumHeight(36)
            save_button.setText("💾 Save")

        if cancel_button:
            cancel_button.setStyleSheet(button_styles['secondary'])
            cancel_button.setMinimumHeight(36)
            cancel_button.setText("❌ Cancel")

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
