"""
Dialog for creating and editing command snippets.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from db.models import Snippet
from ui.modern_dark_theme import ModernDarkTheme
from ui.modern_widgets import ModernFrame
from typing import Optional, Dict
import logging
import os
from datetime import datetime

# Module logger
logger = logging.getLogger(__name__)


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
        try:
            super().__init__(parent)
            self.snippet = snippet
            self.is_editing = snippet is not None

            self._setup_ui()
            self._populate_fields()
            self._connect_signals()
            logging.debug("SnippetDialog: initialized UI, connecting focus logger")
            # Selection styling and any advanced focus visuals are handled
            # centrally in `ModernDarkTheme`. Avoid applying dialog-scoped
            # palettes or graphical effects here to keep the dialog simple.
            try:
                app = QApplication.instance()
                if app:
                    app.focusChanged.connect(self._on_focus_changed)
                    logging.debug("SnippetDialog: connected to QApplication.focusChanged")
            except Exception as e:
                logging.exception("SnippetDialog: failed to connect focusChanged: %s", e)
            # Run initial diagnostics on all editable fields
            try:
                logging.debug("SnippetDialog: running initial diagnostics for inputs")
                try:
                    self._diagnose(self.name_edit, 'name_edit_init')
                except Exception:
                    logging.exception("SnippetDialog: diagnose name_edit failed")
                try:
                    self._diagnose(self.description_edit, 'description_edit_init')
                except Exception:
                    logging.exception("SnippetDialog: diagnose description_edit failed")
                try:
                    self._diagnose(self.command_edit, 'command_edit_init')
                except Exception:
                    logging.exception("SnippetDialog: diagnose command_edit failed")
                try:
                    self._diagnose(self.tags_edit, 'tags_edit_init')
                except Exception:
                    logging.exception("SnippetDialog: diagnose tags_edit failed")
            except Exception:
                logging.exception("SnippetDialog: initial diagnostics failed")
        except Exception:
            logging.exception("Failed to initialize SnippetDialog")
            raise

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
        self.name_edit.setObjectName('name_edit')
        self.name_edit.setAutoFillBackground(True)
        self.name_edit.setPlaceholderText("Enter a short, descriptive name...")
        self.name_edit.setMinimumHeight(36)
        try:
            self.name_edit.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            logging.debug("SnippetDialog: name_edit WA_MacShowFocusRect disabled")
        except Exception:
            logging.exception("SnippetDialog: failed to set WA_MacShowFocusRect on name_edit")
        form_layout.addRow(name_label, self.name_edit)

        # Description field
        desc_label = QLabel("Description")
        desc_label.setFont(QFont("", 12, QFont.Weight.Medium))
        desc_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_primary']};")

        self.description_edit = QTextEdit()
        self.description_edit.setObjectName('description_edit')
        self.description_edit.setAutoFillBackground(True)
        self.description_edit.setPlaceholderText("Enter a longer description of what this command does...")
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setMinimumHeight(80)
        self.description_edit.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        try:
            self.description_edit.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            logging.debug("SnippetDialog: description_edit WA_MacShowFocusRect disabled")
            # also ensure the viewport does not show native focus
            try:
                self.description_edit.viewport().setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
                logging.debug("SnippetDialog: description_edit.viewport WA_MacShowFocusRect disabled")
            except Exception as e:
                logging.exception("SnippetDialog: failed to set WA_MacShowFocusRect on description_edit.viewport: %s", e)
        except Exception:
            logging.exception("SnippetDialog: failed to set WA_MacShowFocusRect on description_edit: %s", exc_info=True)
        form_layout.addRow(desc_label, self.description_edit)

        # Command text field
        command_label = QLabel("Command *")
        command_label.setFont(QFont("", 12, QFont.Weight.Medium))
        command_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_primary']};")

        self.command_edit = QTextEdit()
        self.command_edit.setObjectName('command_edit')
        self.command_edit.setAutoFillBackground(True)
        self.command_edit.setPlaceholderText("Enter the command to execute...")
        self.command_edit.setMinimumHeight(140)
        self.command_edit.setFont(QFont("SF Mono, Monaco, Cascadia Code, Roboto Mono", 12))
        self.command_edit.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        try:
            self.command_edit.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            logging.debug("SnippetDialog: command_edit WA_MacShowFocusRect disabled")
            try:
                self.command_edit.viewport().setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
                logging.debug("SnippetDialog: command_edit.viewport WA_MacShowFocusRect disabled")
            except Exception as e:
                logging.exception("SnippetDialog: failed to set WA_MacShowFocusRect on command_edit.viewport: %s", e)
        except Exception:
            logging.exception("SnippetDialog: failed to set WA_MacShowFocusRect on command_edit: %s", exc_info=True)
        form_layout.addRow(command_label, self.command_edit)

        # Apply strict inline style to QTextEdit so focus border matches QLineEdit
        try:
            fq = ModernDarkTheme.COLORS
            textarea_style = f"""
                QTextEdit#description_edit, QTextEdit#command_edit {{
                    background-color: {fq['surface']};
                    border: 1px solid {fq['border']};
                    border-radius: 6px;
                    padding: 8px;
                    color: {fq['text_primary']};
                }}
                QTextEdit#description_edit:focus, QTextEdit#command_edit:focus {{
                    border: 2px solid {fq['border_focus']};
                    background-color: {fq['surface_elevated']};
                }}
                QTextEdit#description_edit QWidget, QTextEdit#command_edit QWidget {{
                    background: transparent;
                }}
            """
            current = self.styleSheet() or ""
            self.setStyleSheet(current + textarea_style)
        except Exception:
            pass

        # Tags field
        tags_label = QLabel("Tags")
        tags_label.setFont(QFont("", 12, QFont.Weight.Medium))
        tags_label.setStyleSheet(f"color: {ModernDarkTheme.COLORS['text_primary']};")

        self.tags_edit = QLineEdit()
        self.tags_edit.setObjectName('tags_edit')
        self.tags_edit.setAutoFillBackground(True)
        self.tags_edit.setPlaceholderText("Enter comma-separated tags (e.g., aws, docker, ssh)...")
        self.tags_edit.setMinimumHeight(36)
        try:
            self.tags_edit.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
            logging.debug("SnippetDialog: tags_edit WA_MacShowFocusRect disabled")
        except Exception:
            logging.exception("SnippetDialog: failed to set WA_MacShowFocusRect on tags_edit")
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

        # Storage for original inline styles when we apply programmatic focus styling
        try:
            self._orig_inline_styles = {}
        except Exception:
            self._orig_inline_styles = {}

        # Install event filter to capture focus and click events for diagnostics
        class _InputEventFilter(QObject):
            def __init__(self, parent=None, targets=None):
                super().__init__(parent)
                self._targets = set(targets or [])

            def _safe_name(self, obj):
                try:
                    if hasattr(obj, 'objectName'):
                        return obj.objectName()
                except Exception:
                    pass
                try:
                    return type(obj).__name__
                except Exception:
                    return '<unknown>'

            def eventFilter(self, obj, event):
                try:
                    et = event.type()
                    ev_name = None
                    if et == QEvent.Type.FocusIn:
                        ev_name = 'FocusIn'
                    elif et == QEvent.Type.FocusOut:
                        ev_name = 'FocusOut'
                    elif et == QEvent.Type.MouseButtonPress:
                        ev_name = 'MouseButtonPress'
                    if ev_name:
                        nm = self._safe_name(obj)
                        logger.info("SnippetDialog.event: %s on %s", ev_name, nm)
                        # Also append to a persistent log file for user inspection
                        try:
                            proj_root = os.path.dirname(os.path.dirname(__file__))
                            lf = os.path.join(proj_root, 'logs', 'interaction_events.log')
                            with open(lf, 'a', encoding='utf-8') as fh:
                                fh.write(f"{datetime.utcnow().isoformat()}Z\t{ev_name}\t{nm}\n")
                        except Exception:
                            logger.exception("SnippetDialog: failed to write interaction event to file")
                        # If focus changed, set a property so CSS can show a deterministic focus style
                        try:
                            if ev_name in ('FocusIn', 'FocusOut'):
                                focused_val = (ev_name == 'FocusIn')
                                # Set property on the object itself
                                try:
                                    obj.setProperty('focused', focused_val)
                                except Exception:
                                    pass
                                # Also attempt to set the property on the parent (covers QTextEdit.viewport and similar)
                                try:
                                    parent = None
                                    if hasattr(obj, 'parent'):
                                        try:
                                            parent = obj.parent()
                                        except Exception:
                                            parent = getattr(obj, 'parent', lambda: None)()
                                    if parent is not None:
                                        try:
                                            parent.setProperty('focused', focused_val)
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                                # force style update on both
                                try:
                                    for tgt in (obj, parent):
                                        if tgt is None:
                                            continue
                                        try:
                                            tgt.style().unpolish(tgt)
                                            tgt.style().polish(tgt)
                                            tgt.update()
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                                # Apply or remove inline focus stylesheet to guarantee visuals
                                try:
                                    dlg = self.parent()
                                    if dlg is not None:
                                        try:
                                            # Determine the real input widget to style.
                                            real_tgt = None
                                            # If the event is on the widget itself (QLineEdit/QTextEdit), use it
                                            try:
                                                from PyQt6.QtWidgets import QLineEdit, QTextEdit
                                                if isinstance(obj, (QLineEdit, QTextEdit)):
                                                    real_tgt = obj
                                                else:
                                                    # If event is on a viewport child, prefer its parent if it's a text input
                                                    p = None
                                                    try:
                                                        p = obj.parent()
                                                    except Exception:
                                                        p = getattr(obj, 'parent', lambda: None)()
                                                    if isinstance(p, (QLineEdit, QTextEdit)):
                                                        real_tgt = p
                                            except Exception:
                                                real_tgt = None

                                            # Only apply styling to recognized input widgets
                                            if real_tgt is not None:
                                                if focused_val:
                                                    if hasattr(dlg, '_apply_inline_focus_style'):
                                                        dlg._apply_inline_focus_style(real_tgt)
                                                else:
                                                    if hasattr(dlg, '_remove_inline_focus_style'):
                                                        dlg._remove_inline_focus_style(real_tgt)
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                        except Exception:
                            logger.exception("SnippetDialog: failed to set focused property")
                except Exception:
                    logger.exception("SnippetDialog.eventFilter error")
                return False

        try:
            targets = [self.name_edit, self.description_edit, self.command_edit, self.tags_edit]
            self._input_event_filter = _InputEventFilter(parent=self, targets=targets)
            # Install on each widget and their viewports (for QTextEdit)
            for w in targets:
                try:
                    w.installEventFilter(self._input_event_filter)
                except Exception:
                    logger.exception("SnippetDialog: failed to install eventFilter on %s", getattr(w, 'objectName', lambda: '')())
                # also install on viewport for QTextEdit
                try:
                    if hasattr(w, 'viewport'):
                        w.viewport().installEventFilter(self._input_event_filter)
                except Exception:
                    logger.exception("SnippetDialog: failed to install eventFilter on viewport for %s", getattr(w, 'objectName', lambda: '')())
            # Also install on the dialog itself to capture child events as a fallback
            try:
                self.installEventFilter(self._input_event_filter)
            except Exception:
                logger.exception("SnippetDialog: failed to install eventFilter on dialog")
        except Exception:
            logging.exception("SnippetDialog: failed to create/install input event filter")

        # Dialog relies on centralized theme for input visuals; avoid
        # injecting additional unified styles here.
        # Log current dialog stylesheet length for debugging
        try:
            ss = (self.styleSheet() or "")
            logging.debug("SnippetDialog: current combined stylesheet length=%d", len(ss))
        except Exception:
            logging.exception("SnippetDialog: failed to read stylesheet for logging")
    def _apply_inline_focus_style(self, widget):
        """Apply an inline stylesheet to `widget` to guarantee focus visuals."""
        try:
            if widget is None:
                return
            key = id(widget)
            # Save original inline style if not already saved
            if key not in self._orig_inline_styles:
                try:
                    self._orig_inline_styles[key] = widget.styleSheet() or ''
                except Exception:
                    self._orig_inline_styles[key] = ''

            fq = ModernDarkTheme.COLORS
            inline = f"border: 2px solid {fq['border_focus']}; background-color: {fq['surface_elevated']};"
            # Merge with existing inline style if present
            try:
                widget.setStyleSheet(inline)
            except Exception:
                logging.exception("SnippetDialog: failed to set inline focus style on %s", getattr(widget, 'objectName', lambda: '')())
            # Additionally apply a subtle drop shadow for robustness across platforms
            try:
                # Subtle shadow: smaller blur, no vertical offset, semi-transparent color
                shadow = QGraphicsDropShadowEffect(widget)
                shadow.setBlurRadius(8)
                shadow.setXOffset(0)
                shadow.setYOffset(0)
                try:
                    qcol = QColor(fq['border_focus'])
                    qcol.setAlpha(140)
                    shadow.setColor(qcol)
                except Exception:
                    shadow.setColor(QColor(fq['border_focus']))
                widget.setGraphicsEffect(shadow)
            except Exception:
                logging.exception("SnippetDialog: failed to apply drop shadow on %s", getattr(widget, 'objectName', lambda: '')())
        except Exception:
            logging.exception("SnippetDialog._apply_inline_focus_style error")

    def _remove_inline_focus_style(self, widget):
        """Restore the original inline stylesheet for `widget`."""
        try:
            if widget is None:
                return
            key = id(widget)
            orig = self._orig_inline_styles.get(key, None)
            if orig is not None:
                try:
                    widget.setStyleSheet(orig)
                except Exception:
                    logging.exception("SnippetDialog: failed to restore inline style on %s", getattr(widget, 'objectName', lambda: '')())
                try:
                    del self._orig_inline_styles[key]
                except Exception:
                    pass
            # Remove any graphics effect we may have applied
            try:
                ge = widget.graphicsEffect()
                if ge is not None:
                    try:
                        widget.setGraphicsEffect(None)
                    except Exception:
                        pass
            except Exception:
                logging.exception("SnippetDialog: failed to remove graphics effect on %s", getattr(widget, 'objectName', lambda: '')())
        except Exception:
            logging.exception("SnippetDialog._remove_inline_focus_style error")
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

    def _diagnose(self, w, label: str):
        """Log diagnostics about a widget's style, palette and attributes."""
        try:
            if not w:
                logger.debug("SnippetDialog.diagnose: %s is None", label)
                return
            name = w.objectName() if hasattr(w, 'objectName') else ''
            cls = type(w).__name__
            ss = (w.styleSheet() or '')
            ss_len = len(ss)
            has_effect = getattr(w, 'graphicsEffect', lambda: None)() is not None
            mac_focus = False
            opaque = None
            try:
                mac_focus = bool(w.testAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect))
            except Exception:
                pass
            try:
                opaque = bool(w.testAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent))
            except Exception:
                pass
            viewport_info = ''
            try:
                if hasattr(w, 'viewport'):
                    vp = w.viewport()
                    vp_ss = (vp.styleSheet() or '')
                    vp_mac = False
                    try:
                        vp_mac = bool(vp.testAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect))
                    except Exception:
                        pass
                    viewport_info = f"viewport_ss_len={len(vp_ss)}, vp_WA_MacShowFocusRect={vp_mac}"
            except Exception:
                viewport_info = 'viewport_error'
            pal_info = ''
            try:
                pal = w.palette()
                hl = pal.color(QPalette.ColorRole.Highlight).name()
                hlt = pal.color(QPalette.ColorRole.HighlightedText).name()
                pal_info = f"Highlight={hl}, HighlightedText={hlt}"
            except Exception:
                pal_info = 'palette_error'

            logger.debug("SnippetDialog.diagnose %s: name=%s class=%s ss_len=%d has_effect=%s mac_focus=%s opaque=%s %s %s",
                         label, name, cls, ss_len, has_effect, mac_focus, opaque, viewport_info, pal_info)
        except Exception:
            logger.exception("SnippetDialog.diagnose: failed for %s", label)

    def _on_focus_changed(self, old, now):
        """Clear selection in text edits when they lose focus."""
        try:
            old_name = getattr(old, 'objectName', lambda: None)() if old else None
            now_name = getattr(now, 'objectName', lambda: None)() if now else None
            logging.debug("SnippetDialog._on_focus_changed: old=%s (%s), now=%s (%s)", old, old_name, now, now_name)

            # Extra diagnostics for focused widgets
            self._diagnose(old, 'old')
            self._diagnose(now, 'now')
            # If an internal QTextEdit lost focus, clear its selection
            for edit in (self.description_edit, self.command_edit, self.name_edit, self.tags_edit):
                if old is edit and now is not edit:
                    # QTextEdit selection
                    if isinstance(edit, QTextEdit):
                        cursor = edit.textCursor()
                        if cursor.hasSelection():
                            cursor.clearSelection()
                            edit.setTextCursor(cursor)
                            try:
                                edit.viewport().update()
                            except Exception:
                                pass
                            logger.debug("SnippetDialog: cleared selection on %s", getattr(edit, 'objectName', lambda: '')())
                    else:
                        # QLineEdit: try to deselect
                        try:
                            edit.deselect()
                        except Exception:
                            try:
                                edit.setSelection(0, 0)
                            except Exception:
                                pass
                        logger.debug("SnippetDialog: deselected QLineEdit %s", getattr(edit, 'objectName', lambda: '')())
        except Exception:
            pass

    def _create_glow(self):
        # Glow creation removed — leave placeholder in case future work
        # needs a programmatic effect. Do not apply graphical effects here.
        return None

    def _apply_glow(self, widget):
        # Glow application removed — intentionally no-ops to keep UI unchanged
        return

    def _remove_glow(self, widget):
        # Glow removal removed — intentionally no-ops
        return

    def closeEvent(self, event):
        """Cleanup: disconnect focusChanged handler when dialog closes."""
        try:
            app = QApplication.instance()
            if app:
                try:
                    app.focusChanged.disconnect(self._on_focus_changed)
                except Exception:
                    pass
        except Exception:
            pass
        super().closeEvent(event)

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
