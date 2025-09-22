"""
Custom widgets for modern UI components.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.modern_dark_theme import ModernDarkTheme
import hashlib


class TagBadgeWidget(QWidget):
    """A widget that displays tags as modern badges."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        self.tag_colors = ModernDarkTheme.get_tag_colors()

    def set_tags(self, tags_string: str):
        """Set the tags to display as badges."""
        # Clear existing tags
        self.clear_tags()

        if not tags_string or not tags_string.strip():
            return

        # Split tags and create badges
        tags = [tag.strip() for tag in tags_string.split(',') if tag.strip()]

        for tag in tags:
            badge = self._create_tag_badge(tag)
            self.layout.addWidget(badge)

        # Add stretch to push badges to the left
        self.layout.addStretch()

    def _create_tag_badge(self, tag: str) -> QLabel:
        """Create a single tag badge."""
        badge = QLabel(tag)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Generate consistent color for tag
        color = self._get_tag_color(tag)

        # Apply badge styling
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {color}33;
                color: {color};
                border: 1px solid {color}66;
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 500;
                margin: 1px;
            }}
        """)

        # Set font
        font = QFont()
        font.setPointSize(10)
        font.setWeight(QFont.Weight.Medium)
        badge.setFont(font)

        return badge

    def _get_tag_color(self, tag: str) -> str:
        """Get a consistent color for a tag based on its content."""
        # Use hash to get consistent color for the same tag
        hash_value = hashlib.md5(tag.encode()).hexdigest()
        color_index = int(hash_value[:2], 16) % len(self.tag_colors)
        return self.tag_colors[color_index]

    def clear_tags(self):
        """Clear all tag badges."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class ModernFrame(QFrame):
    """A modern styled frame widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernDarkTheme.COLORS['surface']};
                border: 1px solid {ModernDarkTheme.COLORS['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)


class ModernSeparator(QFrame):
    """A modern separator line."""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent)
        if orientation == Qt.Orientation.Horizontal:
            self.setFrameShape(QFrame.Shape.HLine)
            self.setFixedHeight(1)
        else:
            self.setFrameShape(QFrame.Shape.VLine)
            self.setFixedWidth(1)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernDarkTheme.COLORS['border']};
                border: none;
            }}
        """)


class StatusIndicator(QLabel):
    """A modern status indicator widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(8, 8)
        self.setStyleSheet(f"""
            QLabel {{
                border-radius: 4px;
                background-color: {ModernDarkTheme.COLORS['text_muted']};
            }}
        """)

    def set_status(self, status: str):
        """Set the status and update color."""
        colors = {
            'success': ModernDarkTheme.COLORS['success'],
            'warning': ModernDarkTheme.COLORS['warning'],
            'error': ModernDarkTheme.COLORS['error'],
            'info': ModernDarkTheme.COLORS['info'],
            'default': ModernDarkTheme.COLORS['text_muted']
        }

        color = colors.get(status, colors['default'])
        self.setStyleSheet(f"""
            QLabel {{
                border-radius: 4px;
                background-color: {color};
            }}
        """)


class SearchHighlight:
    """Utility class for highlighting search terms in text."""

    @staticmethod
    def highlight_text(text: str, search_term: str) -> str:
        """Highlight search terms in HTML format."""
        if not search_term or not text:
            return text

        # Simple highlighting - could be enhanced with regex for better matching
        highlighted = text.replace(
            search_term,
            f'<span style="background-color: {ModernDarkTheme.COLORS["warning"]}33; '
            f'color: {ModernDarkTheme.COLORS["warning"]}; font-weight: bold;">{search_term}</span>'
        )
        return highlighted