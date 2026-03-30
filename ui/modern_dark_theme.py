"""
Modern Dark Theme stylesheet for Command Snippet Manager.

This module provides a comprehensive dark theme with modern styling
inspired by contemporary application designs.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtGui import QFontDatabase


class ModernDarkTheme:
    """Tactical HUD-inspired dark theme configuration and stylesheet."""

    # Color Palette
    COLORS = {
        # Core surfaces
        'background': '#050b0b',          # Deep tactical black-green
        'surface': '#0b1515',             # Panel background
        'surface_elevated': '#132121',    # Hover/raised panels

        # Typography
        'text_primary': '#d5f2df',        # Main readable text
        'text_secondary': '#8fb7a0',      # Secondary labels
        'text_muted': '#5d7b69',          # Muted metadata

        # Tactical accents
        'accent_blue': '#27d5b0',         # HUD cyan-green
        'accent_blue_hover': '#3deac4',   # Brighter hover
        'accent_green': '#8fdc6a',        # Success/positive
        'accent_orange': '#d4a64e',       # Warning/attention
        'accent_red': '#e05f5f',          # Error/delete
        'accent_purple': '#5aa0ff',       # Auxiliary accent

        # Structural UI tones
        'border': '#1c3530',              # Panel borders
        'border_focus': '#27d5b0',        # Focus glow color
        'selection': '#27d5b04d',         # Selection background
        'selection_border': '#27d5b0',    # Selection border
        'hover': '#27d5b022',             # Hover overlay

        # Status colors
        'success': '#8fdc6a',
        'warning': '#d4a64e',
        'error': '#e05f5f',
        'info': '#27d5b0',
    }

    @staticmethod
    def get_application_stylesheet():
        """Get the main application stylesheet."""
        return f"""
        /* Global Application Styles */
        QApplication {{
            background-color: {ModernDarkTheme.COLORS['background']};
            color: {ModernDarkTheme.COLORS['text_primary']};
            font-family: 'JetBrains Mono', 'Fira Code', 'Menlo', 'Monaco', monospace;
            font-size: 13px;
        }}

        /* Main Window */
        QMainWindow {{
            background-color: {ModernDarkTheme.COLORS['background']};
            color: {ModernDarkTheme.COLORS['text_primary']};
        }}

        /* Central Widget */
        QWidget {{
            background-color: {ModernDarkTheme.COLORS['background']};
            color: {ModernDarkTheme.COLORS['text_primary']};
        }}

        /* HUD surface texture for top-level containers */
        QWidget#hud_panel {{
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 {ModernDarkTheme.COLORS['surface']},
                stop: 1 {ModernDarkTheme.COLORS['background']}
            );
            border: 1px solid {ModernDarkTheme.COLORS['border']};
        }}

        /* Labels */
        QLabel {{
            color: {ModernDarkTheme.COLORS['text_primary']};
            font-weight: 500;
        }}

        QLabel[class="secondary"] {{
            color: {ModernDarkTheme.COLORS['text_secondary']};
            font-weight: 400;
        }}

        QLabel[class="muted"] {{
            color: {ModernDarkTheme.COLORS['text_muted']};
            font-weight: 400;
        }}

        /* Input Fields */
        QLineEdit {{
            background-color: {ModernDarkTheme.COLORS['surface']};
            border: 1px solid {ModernDarkTheme.COLORS['border']};
            border-radius: 6px;
            padding: 8px 12px;
            color: {ModernDarkTheme.COLORS['text_primary']};
            font-size: 13px;
            selection-background-color: {ModernDarkTheme.COLORS['selection']};
        }}

        QLineEdit:focus {{
            border-color: {ModernDarkTheme.COLORS['border_focus']};
            background-color: {ModernDarkTheme.COLORS['surface_elevated']};
        }}

        QLineEdit:hover {{
            background-color: {ModernDarkTheme.COLORS['surface_elevated']};
        }}

        /* Text Areas */
        QTextEdit {{
            background-color: {ModernDarkTheme.COLORS['surface']};
            border: 1px solid {ModernDarkTheme.COLORS['border']};
            border-radius: 6px;
            padding: 8px;
            color: {ModernDarkTheme.COLORS['text_primary']};
            font-family: 'Menlo', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Courier New', monospace;
            font-size: 12px;
            selection-background-color: {ModernDarkTheme.COLORS['selection']};
        }}

        QTextEdit:focus {{
            border-color: {ModernDarkTheme.COLORS['border_focus']};
            background-color: {ModernDarkTheme.COLORS['surface_elevated']};
        }}

        /* Command preview specific overrides to ensure selection is highly visible */
        QTextEdit#command_edit {{
            background-color: {ModernDarkTheme.COLORS['surface']};
            color: {ModernDarkTheme.COLORS['text_primary']};
            selection-background-color: #3399ff66; /* semi-transparent bright blue */
            selection-color: {ModernDarkTheme.COLORS['text_primary']};
        }}

        /* The internal viewport of QTextEdit can mask selection on some platforms; make it explicit */
        QTextEdit#command_edit QWidget {{
            background: transparent;
        }}

        /* Table Widget */
        QTableWidget {{
            background-color: {ModernDarkTheme.COLORS['background']};
            alternate-background-color: {ModernDarkTheme.COLORS['surface']};
            gridline-color: {ModernDarkTheme.COLORS['border']};
            border: none;
            outline: none;
        }}

        QTableWidget::item {{
            padding: 12px 8px;
            border: none;
            border-bottom: 1px solid {ModernDarkTheme.COLORS['border']};
            color: {ModernDarkTheme.COLORS['text_primary']};
            background-color: transparent;
        }}

        /* Selected rows - tactical HUD highlight */
        QTableWidget::item:selected:active {{
            background-color: {ModernDarkTheme.COLORS['selection']};
            color: {ModernDarkTheme.COLORS['text_primary']};
            border-left: 2px solid {ModernDarkTheme.COLORS['selection_border']};
        }}
        QTableWidget::item:selected:!active {{
            background-color: #1f3a33;
            color: {ModernDarkTheme.COLORS['text_primary']};
            border-left: 2px solid {ModernDarkTheme.COLORS['selection_border']};
        }}

        QTableWidget::item:hover {{
            background-color: {ModernDarkTheme.COLORS['hover']};
        }}

        /* Ensure description text doesn't change weight/color on hover */
        QTableWidget::item:hover, QTableWidget::item:selected {{
            color: {ModernDarkTheme.COLORS['text_primary']};
            font-weight: 400;
        }}

        /* Table Headers */
        QHeaderView::section {{
            background-color: {ModernDarkTheme.COLORS['surface']};
            color: {ModernDarkTheme.COLORS['text_secondary']};
            padding: 12px 8px;
            border: none;
            border-bottom: 2px solid {ModernDarkTheme.COLORS['border']};
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}

        QHeaderView::section:hover {{
            background-color: {ModernDarkTheme.COLORS['surface_elevated']};
        }}

        /* Scroll Bars */
        QScrollBar:vertical {{
            background-color: {ModernDarkTheme.COLORS['background']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {ModernDarkTheme.COLORS['border']};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {ModernDarkTheme.COLORS['text_muted']};
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            background-color: {ModernDarkTheme.COLORS['background']};
            height: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {ModernDarkTheme.COLORS['border']};
            border-radius: 6px;
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {ModernDarkTheme.COLORS['text_muted']};
        }}

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {ModernDarkTheme.COLORS['border']};
        }}

        QSplitter::handle:horizontal {{
            width: 2px;
        }}

        QSplitter::handle:vertical {{
            height: 2px;
        }}

        /* Menu Bar */
        QMenuBar {{
            background-color: {ModernDarkTheme.COLORS['surface']};
            color: {ModernDarkTheme.COLORS['text_primary']};
            border-bottom: 1px solid {ModernDarkTheme.COLORS['border']};
            padding: 4px;
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QMenuBar::item:hover {{
            background-color: {ModernDarkTheme.COLORS['hover']};
        }}

        QMenuBar::item:pressed {{
            background-color: {ModernDarkTheme.COLORS['selection']};
        }}

        /* Menu */
        QMenu {{
            background-color: {ModernDarkTheme.COLORS['surface']};
            color: {ModernDarkTheme.COLORS['text_primary']};
            border: 1px solid {ModernDarkTheme.COLORS['border']};
            border-radius: 6px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 8px 12px;
            border-radius: 4px;
        }}

        QMenu::item:hover {{
            background-color: {ModernDarkTheme.COLORS['hover']};
        }}

        QMenu::item:selected {{
            background-color: {ModernDarkTheme.COLORS['selection']};
        }}

        /* Strengthen menu item focus/hover to use the same border focus color */
        QMenu::item:focus, QMenu::item:pressed, QMenu::item:selected:active {{
            background-color: {ModernDarkTheme.COLORS['selection']};
            border: 1px solid {ModernDarkTheme.COLORS['border_focus']};
        }}

        /* Toolbar */
        QToolBar {{
            background-color: {ModernDarkTheme.COLORS['surface']};
            border: none;
            border-bottom: 1px solid {ModernDarkTheme.COLORS['border']};
            spacing: 4px;
            padding: 4px;
        }}

        QToolBar QToolButton {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 6px;
            color: {ModernDarkTheme.COLORS['text_primary']};
        }}

        QToolBar QToolButton:hover {{
            background-color: {ModernDarkTheme.COLORS['hover']};
        }}

        QToolBar QToolButton:pressed {{
            background-color: {ModernDarkTheme.COLORS['selection']};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {ModernDarkTheme.COLORS['surface']};
            color: {ModernDarkTheme.COLORS['text_secondary']};
            border-top: 1px solid {ModernDarkTheme.COLORS['border']};
            padding: 4px;
        }}
        """

    @staticmethod
    def get_button_styles():
        """Get button-specific styles."""
        return {
            'primary': f"""
                QPushButton {{
                    background-color: {ModernDarkTheme.COLORS['surface']};
                    color: {ModernDarkTheme.COLORS['accent_blue']};
                    border: 1px solid {ModernDarkTheme.COLORS['accent_blue']};
                    border-radius: 2px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {ModernDarkTheme.COLORS['surface_elevated']};
                    color: {ModernDarkTheme.COLORS['accent_blue_hover']};
                    border-color: {ModernDarkTheme.COLORS['accent_blue_hover']};
                }}
                QPushButton:pressed {{
                    background-color: #0d1f1d;
                }}
                QPushButton:disabled {{
                    background-color: {ModernDarkTheme.COLORS['border']};
                    color: {ModernDarkTheme.COLORS['text_muted']};
                    border-color: {ModernDarkTheme.COLORS['border']};
                }}
            """,

            'success': f"""
                QPushButton {{
                    background-color: {ModernDarkTheme.COLORS['surface']};
                    color: {ModernDarkTheme.COLORS['accent_green']};
                    border: 1px solid {ModernDarkTheme.COLORS['accent_green']};
                    border-radius: 2px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {ModernDarkTheme.COLORS['surface_elevated']};
                    border-color: #a6ee86;
                }}
                QPushButton:pressed {{
                    background-color: #142218;
                }}
                QPushButton:disabled {{
                    background-color: {ModernDarkTheme.COLORS['border']};
                    color: {ModernDarkTheme.COLORS['text_muted']};
                    border-color: {ModernDarkTheme.COLORS['border']};
                }}
            """,

            'danger': f"""
                QPushButton {{
                    background-color: {ModernDarkTheme.COLORS['surface']};
                    color: {ModernDarkTheme.COLORS['accent_red']};
                    border: 1px solid {ModernDarkTheme.COLORS['accent_red']};
                    border-radius: 2px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {ModernDarkTheme.COLORS['surface_elevated']};
                    border-color: #f27d7d;
                }}
                QPushButton:pressed {{
                    background-color: #231515;
                }}
                QPushButton:disabled {{
                    background-color: {ModernDarkTheme.COLORS['border']};
                    color: {ModernDarkTheme.COLORS['text_muted']};
                    border-color: {ModernDarkTheme.COLORS['border']};
                }}
            """,

            'secondary': f"""
                QPushButton {{
                    background-color: {ModernDarkTheme.COLORS['surface']};
                    color: {ModernDarkTheme.COLORS['text_secondary']};
                    border: 1px solid {ModernDarkTheme.COLORS['border']};
                    border-radius: 2px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {ModernDarkTheme.COLORS['surface_elevated']};
                    color: {ModernDarkTheme.COLORS['text_primary']};
                    border-color: {ModernDarkTheme.COLORS['accent_blue']};
                }}
                QPushButton:pressed {{
                    background-color: {ModernDarkTheme.COLORS['selection']};
                }}
                QPushButton:disabled {{
                    background-color: {ModernDarkTheme.COLORS['background']};
                    color: {ModernDarkTheme.COLORS['text_muted']};
                    border-color: {ModernDarkTheme.COLORS['border']};
                }}
            """
        }

    @staticmethod
    def get_dialog_styles():
        """Get dialog-specific styles."""
        return f"""
        /* Dialog Windows */
        QDialog {{
            background-color: {ModernDarkTheme.COLORS['background']};
            color: {ModernDarkTheme.COLORS['text_primary']};
        }}

        /* Dialog Button Box */
        QDialogButtonBox {{
            background-color: transparent;
        }}

        QDialogButtonBox QPushButton {{
            min-width: 80px;
            margin: 0 4px;
        }}

        /* Message Box */
        QMessageBox {{
            background-color: {ModernDarkTheme.COLORS['surface']};
            color: {ModernDarkTheme.COLORS['text_primary']};
        }}

        QMessageBox QPushButton {{
            min-width: 80px;
            padding: 6px 12px;
        }}

        /* Dialog-specific input selection overrides (higher specificity) */
        QLineEdit#name_edit, QLineEdit#tags_edit {{
            selection-background-color: {ModernDarkTheme.COLORS['accent_blue']};
            selection-color: {ModernDarkTheme.COLORS['text_primary']};
        }}
        QTextEdit#description_edit, QTextEdit#command_edit {{
            selection-background-color: {ModernDarkTheme.COLORS['accent_blue']};
            selection-color: {ModernDarkTheme.COLORS['text_primary']};
        }}

        /* Search bar specific selection rules to ensure visibility */
        QLineEdit#search_edit {{
            selection-background-color: #3399ff66;
            selection-color: {ModernDarkTheme.COLORS['text_primary']};
        }}
        QLineEdit#search_edit QWidget {{
            background: transparent;
        }}
        /* Make focus border for dialog inputs more visible and consistent */
        QLineEdit#name_edit:focus, QLineEdit#tags_edit:focus,
        QTextEdit#description_edit:focus, QTextEdit#command_edit:focus {{
            border: 2px solid {ModernDarkTheme.COLORS['border_focus']};
            background-color: {ModernDarkTheme.COLORS['surface_elevated']};
        }}

        /* Ensure QTextEdit internal viewport is transparent so borders are visible */
        QTextEdit#description_edit QWidget, QTextEdit#command_edit QWidget {{
            background: transparent;
        }}

        /* Increase specificity for selection and focus so it applies uniformly */
        QDialog QLineEdit, QDialog QTextEdit {{
            selection-background-color: {ModernDarkTheme.COLORS['selection']};
            selection-color: {ModernDarkTheme.COLORS['text_primary']};
        }}

        /* Property-based focused selectors for deterministic visuals */
        QLineEdit[focused="true"], QTextEdit[focused="true"] {{
            border: 2px solid {ModernDarkTheme.COLORS['border_focus']};
            background-color: {ModernDarkTheme.COLORS['surface_elevated']};
        }}
        """

    @staticmethod
    def create_tag_badge_style(color: str):
        """Create a badge style for tags."""
        # Use theme primary text color for label text to ensure contrast on dark backgrounds
        text_col = ModernDarkTheme.COLORS['text_primary']
        return f"""
            QLabel {{
                background-color: {color}33; /* subtle translucent fill */
                color: {text_col};
                border: 1px solid {color}66;
                border-radius: 8px;
                padding: 2px 8px;
                font-size: 12px;
                font-weight: 500;
                margin: 2px 0px;
                min-height: 18px;
                min-width: 28px;
                max-width: 160px;
            }}
        """

    # Ordered preference list for monospace code display.
    MONOSPACE_FONT_CANDIDATES = [
        'JetBrains Mono',
        'Fira Code',
        'Cascadia Code',
        'Menlo',
        'Monaco',
        'Roboto Mono',
        'Courier New',
        'Courier',
    ]

    @staticmethod
    def resolve_monospace_font(size: int = 12) -> QFont:
        """
        Return a QFont set to the first available monospace family.

        Qt's QFont constructor does not accept CSS-style comma-separated
        fallback lists.  Passing 'SF Mono, Monaco, ...' as a family name
        causes a Qt warning and a 100+ ms font-alias-population delay.
        This helper picks the first installed family from the preference
        list and falls back to the system fixed-pitch font.
        """
        available = set(QFontDatabase.families())
        for family in ModernDarkTheme.MONOSPACE_FONT_CANDIDATES:
            if family in available:
                return QFont(family, size)
        # Hard fallback: system fixed-pitch font
        font = QFont()
        font.setFixedPitch(True)
        font.setPointSize(size)
        return font

    @staticmethod
    def get_tag_colors():
        """Get predefined colors for tag badges."""
        return [
            '#27d5b0',
            '#8fdc6a',
            '#d4a64e',
            '#5aa0ff',
            '#41c9f4',
            '#4abf9f',
            '#b8d66b',
            '#6bc7a6',
            '#b4c973',
            '#89d3ba',
            '#cfb86f',
            '#6eaad8',
            '#70c98f',
            '#9ac1a2',
            '#d6be8f',
        ]