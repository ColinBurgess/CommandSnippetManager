"""
Custom widgets for modern UI components.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from ui.modern_dark_theme import ModernDarkTheme
import hashlib


class TagBadgeWidget(QWidget):
    """A widget that displays tags as modern badges."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        self.tag_colors = ModernDarkTheme.get_tag_colors()
        # Keep the badge container compact and with a fixed height so it
        # doesn't cause some rows to become taller than others.
        try:
            self.setFixedHeight(24)
        except Exception:
            pass
        try:
            from PyQt6.QtWidgets import QSizePolicy
            # Prefer not to expand horizontally; badges should size to content
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        except Exception:
            pass
        try:
            # Align badges to the left inside the cell
            self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        except Exception:
            pass

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
        # Do not add stretch inside table cells — keep natural sizing

    def _create_tag_badge(self, tag: str) -> QLabel:
        """Create a single tag badge."""
        badge = QLabel(tag)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Generate consistent color for tag
        color = self._get_tag_color(tag)

        # Apply badge styling using centralized theme helper
        badge.setStyleSheet(ModernDarkTheme.create_tag_badge_style(color))

        # Set font
        font = QFont()
        font.setPointSize(10)
        font.setWeight(QFont.Weight.Medium)
        badge.setFont(font)

        # Constrain badge height so it doesn't increase table row height and allow it to expand horizontally
        try:
            badge.setFixedHeight(20)
        except Exception:
            pass
        try:
            from PyQt6.QtWidgets import QSizePolicy
            badge.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            badge.setMinimumWidth(36)
            badge.setMaximumWidth(140)
        except Exception:
            pass

        # Elide text if too long to fit the badge
        try:
            from PyQt6.QtGui import QFontMetrics
            fm = QFontMetrics(font)
            elided = fm.elidedText(tag, Qt.TextElideMode.ElideRight, 120)
            badge.setText(elided)
        except Exception:
            pass

        return badge

    def _get_tag_color(self, tag: str) -> str:
        """Return a single, consistent color for all tags."""
        # Deterministic color selection based on tag hash for better variety
        try:
            h = int(hashlib.sha1(tag.encode('utf-8')).hexdigest(), 16)
            idx = h % len(self.tag_colors)
            return self.tag_colors[idx]
        except Exception:
            return ModernDarkTheme.COLORS['accent_blue']

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


class SnippetCard(QFrame):
    """A compact card view for displaying a single snippet."""

    def __init__(self, snippet: dict, parent=None):
        super().__init__(parent)
        self.snippet = snippet or {}
        self.setObjectName("snippetCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        title = QLabel(self.snippet.get('name', '<unnamed>'))
        title.setObjectName('cardTitle')
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)

        desc = QLabel(self.snippet.get('description', ''))
        desc.setObjectName('cardDescription')
        desc.setWordWrap(True)
        desc_font = desc.font()
        desc_font.setPointSize(11)
        desc.setFont(desc_font)
        desc.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_muted']};")

        tags_widget = TagBadgeWidget()
        tags_widget.set_tags(self.snippet.get('tags', ''))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(tags_widget)

        # Ensure compact height
        try:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
            self.setMinimumHeight(64)
        except Exception:
            pass
