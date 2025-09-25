"""
Main application window for the Command Snippet Management Application.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QPushButton, QMessageBox, QStatusBar,
    QHeaderView, QAbstractItemView, QSplitter, QTextEdit, QLabel,
    QFrame, QToolBar, QSizePolicy, QApplication, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction, QIcon, QColor
from datetime import datetime
from typing import Optional
import re
import logging

from core.snippet_manager import SnippetManager
from ui.modern_dark_theme import ModernDarkTheme
from ui.snippet_dialog import SnippetDialog
from ui.backup_dialog import BackupDialog
from ui.modern_dark_theme import ModernDarkTheme
from ui.modern_widgets import TagBadgeWidget, ModernFrame, ModernSeparator, SnippetCard
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

        # Apply modern dark theme
        self._apply_theme()

        self._setup_ui()
        self._connect_signals()
        self.load_snippets()

    def _apply_theme(self):
        """Apply the modern dark theme to the application."""
        # Set application stylesheet
        try:
            # On macOS the system may use a native menu bar that ignores Qt stylesheets.
            # Disable native menu bar so Qt can style menus consistently across platforms.
            try:
                QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeMenuBar, True)
                logging.debug("MainWindow: disabled native menu bar to allow Qt styling")
            except Exception:
                logging.debug("MainWindow: could not disable native menu bar (platform may ignore)")
            app = QApplication.instance()
            app_styles = ModernDarkTheme.get_application_stylesheet()
            app.setStyleSheet(app_styles)
            logging.debug("MainWindow: applied application stylesheet length=%d", len(app_styles))

            # Apply additional dialog styles
            dialog_styles = ModernDarkTheme.get_dialog_styles()
            current_stylesheet = app.styleSheet() or ""
            app.setStyleSheet(current_stylesheet + dialog_styles)
            logging.debug("MainWindow: appended dialog stylesheet length=%d, total length now=%d",
                          len(dialog_styles), len(app.styleSheet() or ""))
        except Exception as e:
            logging.exception("MainWindow: failed to apply theme: %s", e)

    def _setup_ui(self):
        """Set up the user interface."""
        # Window properties
        self.setWindowTitle("Command Snippet Manager")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 800)

        # The application provides toolbar/buttons for all actions.
        # Do not create the in-window menu bar to keep the UI minimal.
        # (Keep _create_menu_bar available for future use.)
        try:
            mb = self.menuBar()
            try:
                mb.setNativeMenuBar(False)
            except Exception:
                pass
            mb.setVisible(False)
        except Exception:
            pass

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with optimized spacing
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)  # Reduced from 16
        main_layout.setContentsMargins(12, 4, 12, 4)  # Reduced margins

    # Toolbar is optional; actions are available via the main
    # action row (buttons) below the preview. Do not create the
    # in-window toolbar to keep the UI minimal and avoid duplicate
    # controls above the search box.
    # (The _create_toolbar method is kept for programmatic use.)

        # Hide the native menu bar (on macOS it appears at the top) because
        # toolbar actions provide the same functionality. This removes the
        # 'File' label and frees vertical space.
        try:
            mb = self.menuBar()
            try:
                mb.setNativeMenuBar(False)
            except Exception:
                pass
            mb.setVisible(False)
        except Exception:
            pass

        # Search section - compact and streamlined
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        # Small search icon/label
        search_label = QLabel("🔍")
        search_label.setFixedSize(24, 24)
        search_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_secondary']}; font-size: 16px;")

        # Compact search input
        self.search_edit = QLineEdit()
        # Allow targeting via stylesheet and ensure selection is visible
        self.search_edit.setObjectName('search_edit')
        self.search_edit.setPlaceholderText("Search snippets by name/description/command/tags — use '%' as wildcard, or separate tags with commas")
        self.search_edit.setFixedHeight(32)  # Reduced height
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ModernDarkTheme.COLORS['surface']};
                border: 1px solid {ModernDarkTheme.COLORS['border']};
                border-radius: 16px;
                padding: 0 12px;
                color: {ModernDarkTheme.COLORS['text_primary']};
                font-size: 13px;
                selection-background-color: #3399ff66; /* visible blue selection */
                selection-color: {ModernDarkTheme.COLORS['text_primary']};
            }}
            QLineEdit:focus {{
                border-color: {ModernDarkTheme.COLORS['border_focus']};
                background-color: {ModernDarkTheme.COLORS['surface_elevated']};
            }}
        """)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)

        main_layout.addLayout(search_layout)        # Create splitter for table and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Left side - snippet list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Snippets table with modern styling
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Added column for status indicator
        self.table.setHorizontalHeaderLabels(["", "Name", "Description", "Tags", "Last Used"])

        # Configure table for better row selection (styles centralized in theme)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)

        # Improve selection behavior and styling
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable editing
        self.table.setMouseTracking(True)  # Enable mouse tracking for better hover effects

        # Set column widths and behavior
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Status indicator
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Description - expandable (priority)
        # Make tags a fixed width so it cannot steal space from description
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Tags
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Last Used

        # Set status column width and description minimum
        self.table.setColumnWidth(0, 30)
        self.table.setColumnWidth(2, 500)  # Give description more room by default
        # Fix tags column width so badges cannot grow unbounded
        self.table.setColumnWidth(3, 180)

        # Fallback default row height to avoid visual jitter from embedded widgets
        try:
            self.table.verticalHeader().setDefaultSectionSize(36)
        except Exception:
            pass

        # Enable word wrap for better text display
        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.TextElideMode.ElideNone)  # Don't elide text

        # Add table to layout
        left_layout.addWidget(self.table)

        # Card list (hidden by default)
        self.card_list = QListWidget()
        self.card_list.setVisible(False)
        self.card_list.setSpacing(8)
        left_layout.addWidget(self.card_list)

        # Right side - command preview with modern styling
        right_widget = ModernFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(16, 16, 16, 16)

        # Preview header with icon
        preview_header = QHBoxLayout()
        preview_label = QLabel("⚡ Command Preview")
        preview_label.setFont(QFont("", 14, QFont.Weight.Bold))
        preview_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_primary']};")
        preview_header.addWidget(preview_label)
        preview_header.addStretch()
        right_layout.addLayout(preview_header)

        # Separator
        separator = ModernSeparator()
        right_layout.addWidget(separator)

        # Command text display
        self.command_preview = QTextEdit()
        # Give the preview a specific object name so stylesheet rules can target it
        self.command_preview.setObjectName('command_edit')
        self.command_preview.setReadOnly(True)
        self.command_preview.setFont(QFont("SF Mono, Monaco, Cascadia Code, Roboto Mono", 12))
        self.command_preview.setPlaceholderText("Select a snippet to preview its command...")
        self.command_preview.setMinimumHeight(200)
        # Ensure text selection is enabled even in read-only mode so users
        # can highlight text and see the selection clearly.
        try:
            self.command_preview.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        except Exception:
            # Fallback if flags API differs across PyQt versions
            pass
        right_layout.addWidget(self.command_preview)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 300])  # Initial sizes

        main_layout.addWidget(splitter)

        # Button layout with compact styling
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)  # Reduced top margin
        button_layout.setSpacing(8)  # Reduced spacing

        # Action buttons with modern styles
        self.new_button = QPushButton("✨ New Snippet")
        self.edit_button = QPushButton("✏️ Edit")
        self.delete_button = QPushButton("🗑️ Delete")
        self.copy_button = QPushButton("📋 Copy Command")
        self.execute_button = QPushButton("▶️ Execute")

        # Apply button styles
        button_styles = ModernDarkTheme.get_button_styles()
        self.new_button.setStyleSheet(button_styles['primary'])
        self.edit_button.setStyleSheet(button_styles['secondary'])
        self.delete_button.setStyleSheet(button_styles['danger'])
        self.copy_button.setStyleSheet(button_styles['success'])
        self.execute_button.setStyleSheet(button_styles['primary'])

        # Set button heights - more compact
        for button in [self.new_button, self.edit_button, self.delete_button,
                      self.copy_button, self.execute_button]:
            button.setMinimumHeight(30)  # Reduced from 36
            button.setFont(QFont("", 12, QFont.Weight.Medium))  # Slightly smaller font        # Initially disable buttons that require selection
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

        # Visible Card View toggle button in the main action row
        self.card_view_button = QPushButton("🗂️ Card View")
        self.card_view_button.setCheckable(True)
        self.card_view_button.setChecked(False)
        # Use same secondary button style as toolbar for visual parity
        try:
            self.card_view_button.setStyleSheet(button_styles['secondary'])
            self.card_view_button.setMinimumHeight(30)
            self.card_view_button.setFont(QFont("", 12, QFont.Weight.Medium))
        except Exception:
            pass
        button_layout.addWidget(self.card_view_button)

        # Keep the toolbar QAction and the visible button in sync so
        # toggling either updates the other and triggers the same view change
        try:
            if getattr(self, 'view_toggle_action', None):
                # initialize state
                self.card_view_button.setChecked(self.view_toggle_action.isChecked())
                # user toggles visible button -> toggle toolbar action (which already calls _on_toggle_view)
                self.card_view_button.toggled.connect(lambda checked: self.view_toggle_action.setChecked(checked))
                # toggling the toolbar action (from menu/shortcut) updates the visible button
                self.view_toggle_action.toggled.connect(lambda checked: self.card_view_button.setChecked(checked))
        except Exception:
            pass

        main_layout.addLayout(button_layout)  # Changed from addWidget(button_frame) to addLayout

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.show_status_message("Ready")

        # Apply final styling to status bar
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {ModernDarkTheme.COLORS['surface']};
                color: {ModernDarkTheme.COLORS['text_secondary']};
                border-top: 1px solid {ModernDarkTheme.COLORS['border']};
                padding: 6px 12px;
                font-size: 12px;
            }}
        """)

    def _create_menu_bar(self):
        """Create the application menu bar."""
        # Keep the method available for programmatic use, but do not
        # create the menu during normal startup as toolbar/buttons are
        # used instead for a more focused UI.
        logging.debug("MainWindow: _create_menu_bar called (menu creation is disabled by default)")

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

        # Toggle card/table view
        self.view_toggle_action = QAction("Card View", self)
        self.view_toggle_action.setCheckable(True)
        self.view_toggle_action.setStatusTip("Toggle card (list) view")
        self.view_toggle_action.toggled.connect(self._on_toggle_view)
        toolbar.addAction(self.view_toggle_action)

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

        # Ensure proper row selection when clicking on any cell
        self.table.itemClicked.connect(self._on_item_clicked)
        # Card list click
        try:
            self.card_list.itemClicked.connect(self._on_card_clicked)
        except Exception:
            pass

    def _on_item_clicked(self, item):
        """Handle cell clicks to ensure entire row is selected."""
        if item:
            row = item.row()
            self.table.selectRow(row)

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

    def _on_toggle_view(self, enabled: bool):
        """Toggle between table view and card list view."""
        self.table.setVisible(not enabled)
        self.card_list.setVisible(enabled)
        if enabled:
            # Populate cards when switching to card view
            self._populate_card_list()

    def _populate_card_list(self):
        """Populate the QListWidget with SnippetCard widgets."""
        try:
            self.card_list.clear()
            for snippet in self.current_snippets:
                item = QListWidgetItem()
                card = SnippetCard({
                    'name': snippet.name,
                    'description': snippet.description,
                    'tags': snippet.tags
                })
                item.setSizeHint(card.sizeHint())
                self.card_list.addItem(item)
                self.card_list.setItemWidget(item, card)
        except Exception as e:
            logging.exception("Failed to populate card list: %s", e)

    def _on_card_clicked(self, item: QListWidgetItem):
        """Handle clicks on card items by selecting the corresponding snippet."""
        try:
            row = self.card_list.row(item)
            if 0 <= row < len(self.current_snippets):
                snippet = self.current_snippets[row]
                # Select corresponding row in table for command preview and actions
                # Find and select the table row with matching snippet id
                for r in range(self.table.rowCount()):
                    it = self.table.item(r, 1)
                    if it and it.data(Qt.ItemDataRole.UserRole) == snippet.id:
                        self.table.selectRow(r)
                        self._update_command_preview()
                        break
        except Exception:
            pass

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
                # Let rows size to content; avoid forcing a static height which can cause clipping

                # Status indicator (empty for now, could be used for favorite/recent status)
                status_item = QTableWidgetItem("")
                self.table.setItem(row, 0, status_item)

                # Name with improved formatting
                name_item = QTableWidgetItem(snippet.name)
                name_item.setData(Qt.ItemDataRole.UserRole, snippet.id)  # Store ID
                name_item.setFont(QFont("", 13, QFont.Weight.Medium))
                self.table.setItem(row, 1, name_item)

                # Description - full text, multiline, no truncation
                # Sanitize description to remove problematic invisible
                # characters (zero-width spaces, soft hyphens) that can
                # cause words to appear incorrectly spaced in the table.
                raw_desc = snippet.description or ""
                sanitized_desc = re.sub(r"[\u200B\u200C\u200D\uFEFF\u00AD]",
                                        "", raw_desc)
                description_item = QTableWidgetItem(sanitized_desc)
                description_item.setFont(QFont("", 12))
                description_item.setForeground(QColor(ModernDarkTheme.COLORS['text_secondary']))
                # Enable text wrapping for this item
                description_item.setTextAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, 2, description_item)

                # Tags as modern badges
                if snippet.tags and snippet.tags.strip():
                    # Create a container widget for tag badges
                    tag_widget = TagBadgeWidget()
                    tag_widget.set_tags(snippet.tags)
                    self.table.setCellWidget(row, 3, tag_widget)
                else:
                    # Empty cell for no tags
                    # Use a small placeholder widget to keep row heights consistent
                    placeholder = QWidget()
                    placeholder.setFixedHeight(24)
                    self.table.setCellWidget(row, 3, placeholder)

                # Last Used with cleaner formatting
                if snippet.last_used:
                    # More human-readable date format without extra spacing
                    now = datetime.now()
                    diff = now - snippet.last_used

                    if diff.days == 0:
                        if diff.seconds < 3600:  # Less than 1 hour
                            last_used_str = f"{diff.seconds // 60}m ago"
                        else:  # Less than 1 day
                            last_used_str = f"{diff.seconds // 3600}h ago"
                    elif diff.days == 1:
                        last_used_str = "Yesterday"
                    elif diff.days < 7:
                        last_used_str = f"{diff.days}d ago"
                    else:
                        last_used_str = snippet.last_used.strftime("%b %d")
                else:
                    last_used_str = "Never"

                last_used_item = QTableWidgetItem(last_used_str)
                last_used_item.setFont(QFont("", 11))
                last_used_item.setForeground(QColor(ModernDarkTheme.COLORS['text_muted']))
                last_used_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align
                self.table.setItem(row, 4, last_used_item)

            # Update status
            count = len(snippets)
            if search_term:
                self.show_status_message(f"Found {count} snippet(s) matching '{search_term}'")
            else:
                self.show_status_message(f"Loaded {count} snippet(s)")

            # Adjust row heights to fit content
            # Resize rows then enforce a uniform minimum to avoid mixed heights
            self.table.resizeRowsToContents()
            try:
                self.table.verticalHeader().setDefaultSectionSize(36)
            except Exception:
                pass

            # If card view is active, update it as well
            try:
                if getattr(self, 'view_toggle_action', None) and self.view_toggle_action.isChecked():
                    self._populate_card_list()
            except Exception:
                pass

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load snippets: {e}")
            self.show_status_message("Error loading snippets")

    def filter_snippets(self):
        """Filter snippets based on search text."""
        # Preserve currently selected snippet (by id) so we can re-select it
        previous_selected_id = self.get_selected_snippet_id()

        raw = self.search_edit.text().strip()
        # Allow users to type '*' as a familiar wildcard; map it to SQL '%' wildcard
        if '*' in raw:
            search_text = raw.replace('*', '%')
        else:
            search_text = raw

        # Reload snippets according to the filter
        self.load_snippets(search_term=search_text)

        # If the previously selected snippet is still present in the filtered results,
        # re-select its row so the preview doesn't jump to the first item unexpectedly.
        try:
            if previous_selected_id is not None:
                for r in range(self.table.rowCount()):
                    it = self.table.item(r, 1)  # name column stores the userRole id
                    if it and it.data(Qt.ItemDataRole.UserRole) == previous_selected_id:
                        self.table.selectRow(r)
                        # Update preview explicitly
                        self._update_command_preview()
                        break
        except Exception:
            # Don't let selection rehydration break filtering; ignore failures
            pass

    def get_selected_snippet_id(self) -> Optional[int]:
        """
        Get the ID of the currently selected snippet.

        Returns:
            Snippet ID or None if no selection
        """
        current_row = self.table.currentRow()
        if current_row >= 0:
            name_item = self.table.item(current_row, 1)  # Name is now in column 1


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
                try:
                    dialog = SnippetDialog(self, snippet)
                except Exception as e:
                    import traceback, logging
                    logging.exception("Exception creating SnippetDialog")
                    raise
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
