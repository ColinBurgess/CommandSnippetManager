"""
Modern Dark Theme stylesheet for Command Snippet Manager.

This module provides a comprehensive dark theme with modern styling
inspired by contemporary application designs.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor


class ModernDarkTheme:
    """Modern dark theme configuration and stylesheet."""

    # Color Palette
    COLORS = {
        # Primary colors
        'background': '#1a1a1a',          # Main background
        'surface': '#2d2d2d',             # Cards, panels
        'surface_elevated': '#3a3a3a',    # Hover states

        # Text colors
        'text_primary': '#ffffff',        # Main text
        'text_secondary': '#b0b0b0',      # Secondary text
        'text_muted': '#808080',          # Muted text

        # Accent colors
        'accent_blue': '#007acc',         # Primary accent
        'accent_blue_hover': '#1e88e5',   # Blue hover
        'accent_green': '#4caf50',        # Success/positive
        'accent_orange': '#ff9800',       # Warning/info
        'accent_red': '#f44336',          # Error/delete
        'accent_purple': '#9c27b0',       # Special

        # UI elements
        'border': '#404040',              # Borders
        'border_focus': '#007acc',        # Focused borders
        'selection': '#007acc80',         # Selection background (more visible)
        'selection_border': '#007acc',    # Selection border
        'hover': '#007acc1a',             # Hover background

        # Status colors
        'success': '#4caf50',
        'warning': '#ff9800',
        'error': '#f44336',
        'info': '#2196f3',
    }

    @staticmethod
    def get_application_stylesheet():
        """Get the main application stylesheet."""
        return f"""
        /* Global Application Styles */
        QApplication {{
            background-color: {ModernDarkTheme.COLORS['background']};
            color: {ModernDarkTheme.COLORS['text_primary']};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
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
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
            font-size: 12px;
            selection-background-color: {ModernDarkTheme.COLORS['selection']};
        }}

        QTextEdit:focus {{
            border-color: {ModernDarkTheme.COLORS['border_focus']};
            background-color: {ModernDarkTheme.COLORS['surface_elevated']};
        }}

        /* Table Widget */
        QTableWidget {{
            background-color: {ModernDarkTheme.COLORS['background']};
            alternate-background-color: {ModernDarkTheme.COLORS['surface']};
            gridline-color: {ModernDarkTheme.COLORS['border']};
            border: none;
            selection-background-color: {ModernDarkTheme.COLORS['selection']};
            selection-color: {ModernDarkTheme.COLORS['text_primary']};
            outline: none;
        }}

        QTableWidget::item {{
            padding: 12px 8px;
            border: none;
            border-bottom: 1px solid {ModernDarkTheme.COLORS['border']};
            color: {ModernDarkTheme.COLORS['text_primary']};
            background-color: transparent;
        }}

        QTableWidget::item:selected {{
            background-color: {ModernDarkTheme.COLORS['selection']};
            color: {ModernDarkTheme.COLORS['text_primary']};
            border-left: 3px solid {ModernDarkTheme.COLORS['selection_border']};
        }}

        QTableWidget::item:hover {{
            background-color: {ModernDarkTheme.COLORS['hover']};
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
                    background-color: {ModernDarkTheme.COLORS['accent_blue']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {ModernDarkTheme.COLORS['accent_blue_hover']};
                }}
                QPushButton:pressed {{
                    background-color: #0f5d9e;
                }}
                QPushButton:disabled {{
                    background-color: {ModernDarkTheme.COLORS['border']};
                    color: {ModernDarkTheme.COLORS['text_muted']};
                }}
            """,

            'success': f"""
                QPushButton {{
                    background-color: {ModernDarkTheme.COLORS['accent_green']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: #66bb6a;
                }}
                QPushButton:pressed {{
                    background-color: #388e3c;
                }}
                QPushButton:disabled {{
                    background-color: {ModernDarkTheme.COLORS['border']};
                    color: {ModernDarkTheme.COLORS['text_muted']};
                }}
            """,

            'danger': f"""
                QPushButton {{
                    background-color: {ModernDarkTheme.COLORS['accent_red']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: #e57373;
                }}
                QPushButton:pressed {{
                    background-color: #d32f2f;
                }}
                QPushButton:disabled {{
                    background-color: {ModernDarkTheme.COLORS['border']};
                    color: {ModernDarkTheme.COLORS['text_muted']};
                }}
            """,

            'secondary': f"""
                QPushButton {{
                    background-color: {ModernDarkTheme.COLORS['surface']};
                    color: {ModernDarkTheme.COLORS['text_primary']};
                    border: 1px solid {ModernDarkTheme.COLORS['border']};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {ModernDarkTheme.COLORS['surface_elevated']};
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
        """

    @staticmethod
    def create_tag_badge_style(color: str):
        """Create a badge style for tags."""
        return f"""
            QLabel {{
                background-color: {color}33;
                color: {color};
                border: 1px solid {color}66;
                border-radius: 12px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: 500;
                margin: 1px;
            }}
        """

    @staticmethod
    def get_tag_colors():
        """Get predefined colors for tag badges."""
        return [
            ModernDarkTheme.COLORS['accent_blue'],
            ModernDarkTheme.COLORS['accent_green'],
            ModernDarkTheme.COLORS['accent_orange'],
            ModernDarkTheme.COLORS['accent_purple'],
            ModernDarkTheme.COLORS['info'],
            '#e91e63',  # Pink
            '#9c27b0',  # Purple
            '#673ab7',  # Deep Purple
            '#3f51b5',  # Indigo
            '#00bcd4',  # Cyan
            '#009688',  # Teal
            '#8bc34a',  # Light Green
            '#cddc39',  # Lime
            '#ffc107',  # Amber
            '#ff5722',  # Deep Orange
        ]