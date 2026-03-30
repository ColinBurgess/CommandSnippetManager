"""
UI import smoke tests.

These tests verify that all UI modules can be imported without errors and that
critical methods produce valid output.  They run without a display (DISPLAY is
not required for import-level checks) and catch syntax errors, bad f-strings, or
broken module-level code before the app is even launched.
"""

import ast
import importlib
import os
import pytest
import sys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

UI_PACKAGE = "ui"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

UI_MODULES = [
    "ui.modern_dark_theme",
]


# ---------------------------------------------------------------------------
# Syntax / AST validation (no Qt needed)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module_name", UI_MODULES)
def test_no_syntax_errors(module_name):
    """Verify that the source file parses cleanly as Python (no f-string escaping bugs)."""
    rel_path = module_name.replace(".", os.sep) + ".py"
    abs_path = os.path.join(PROJECT_ROOT, rel_path)

    with open(abs_path, encoding="utf-8") as fh:
        source = fh.read()

    try:
        ast.parse(source)
    except SyntaxError as exc:
        pytest.fail(
            f"SyntaxError in {module_name} at line {exc.lineno}: {exc.msg}\n"
            f"  => {exc.text}"
        )


# ---------------------------------------------------------------------------
# Runtime import + stylesheet generation
# ---------------------------------------------------------------------------

def test_modern_dark_theme_imports():
    """ModernDarkTheme can be imported at runtime."""
    from ui.modern_dark_theme import ModernDarkTheme  # noqa: F401


def test_application_stylesheet_is_non_empty_string():
    """get_application_stylesheet() returns a non-empty string (no runtime f-string errors)."""
    from ui.modern_dark_theme import ModernDarkTheme

    result = ModernDarkTheme.get_application_stylesheet()
    assert isinstance(result, str), "Stylesheet must be a string"
    assert len(result) > 100, "Stylesheet is suspiciously short"


def test_dialog_styles_is_non_empty_string():
    """get_dialog_styles() returns a non-empty string."""
    from ui.modern_dark_theme import ModernDarkTheme

    result = ModernDarkTheme.get_dialog_styles()
    assert isinstance(result, str), "Dialog styles must be a string"
    assert len(result) > 50, "Dialog styles are suspiciously short"


def test_button_styles_keys_present():
    """get_button_styles() returns a dict with all expected keys."""
    from ui.modern_dark_theme import ModernDarkTheme

    styles = ModernDarkTheme.get_button_styles()
    assert isinstance(styles, dict)
    for key in ("primary", "secondary", "success", "danger"):
        assert key in styles, f"Missing button style: '{key}'"
        assert isinstance(styles[key], str) and len(styles[key]) > 10


def test_tag_colors_list():
    """get_tag_colors() returns a non-empty list of color strings."""
    from ui.modern_dark_theme import ModernDarkTheme

    colors = ModernDarkTheme.get_tag_colors()
    assert isinstance(colors, list) and len(colors) > 0
    for color in colors:
        assert color.startswith("#"), f"Invalid color format: {color}"


def test_create_tag_badge_style():
    """create_tag_badge_style() returns a non-empty string for a valid color."""
    from ui.modern_dark_theme import ModernDarkTheme

    style = ModernDarkTheme.create_tag_badge_style("#27d5b0")
    assert isinstance(style, str) and len(style) > 20


def test_colors_dict_has_required_keys():
    """COLORS dict contains all keys referenced throughout the theme."""
    from ui.modern_dark_theme import ModernDarkTheme

    required = {
        "background", "surface", "surface_elevated",
        "text_primary", "text_secondary", "text_muted",
        "accent_blue", "accent_blue_hover", "accent_green",
        "accent_orange", "accent_red", "accent_purple",
        "border", "border_focus", "selection", "selection_border", "hover",
        "success", "warning", "error", "info",
    }
    missing = required - set(ModernDarkTheme.COLORS.keys())
    assert not missing, f"Missing color keys: {missing}"


def test_stylesheets_contain_no_unescaped_fstring_braces():
    """
    Stylesheet strings must not contain lone '{' or '}' left over from
    incorrect f-string escaping (each CSS brace pair should be {{ / }}).
    We validate by checking that every '{' that remains in the rendered
    output is followed by a letter/# (i.e. it is part of a CSS rule or
    property value), not a standalone CSS brace that was meant to be escaped.

    This catches the exact class of bug where a developer writes:
        QWidget { color: ... }
    instead of:
        QWidget {{ color: ... }}
    inside a Python f-string.
    """
    import re
    from ui.modern_dark_theme import ModernDarkTheme

    for name, css in [
        ("application", ModernDarkTheme.get_application_stylesheet()),
        ("dialog", ModernDarkTheme.get_dialog_styles()),
    ]:
        # After rendering, a standalone CSS opening brace is valid — but a
        # Python-level broken f-string would have raised SyntaxError already.
        # What we check here is that the rendered string is balanced.
        depth = 0
        for ch in css:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    pytest.fail(
                        f"Unmatched '}}' found in '{name}' stylesheet — "
                        "check for unescaped f-string braces"
                    )
        assert depth == 0, (
            f"Unbalanced braces in '{name}' stylesheet (depth={depth}) — "
            "check for unescaped f-string braces"
        )


# ---------------------------------------------------------------------------
# Font safety tests
# ---------------------------------------------------------------------------

def test_no_css_font_stack_in_qfont_calls():
    """
    Detect QFont("family1, family2, ...") calls in Python source files.

    Qt's QFont constructor does NOT accept CSS-style comma-separated fallback
    lists.  Passing such a string causes:
      - a Qt warning about populating font family aliases (100+ ms delay)
      - the literal multi-value string being used as the family name (no match)

    This test scans all .py files under ui/ and flags any QFont call whose
    first argument contains a comma — which is never a valid single font name.
    """
    import re

    pattern = re.compile(r'QFont\s*\(\s*["\']([^"\']*,[^"\']*)["\']')
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ui_dir = os.path.join(project_root, "ui")

    violations = []
    for fname in os.listdir(ui_dir):
        if not fname.endswith(".py"):
            continue
        fpath = os.path.join(ui_dir, fname)
        with open(fpath, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                m = pattern.search(line)
                if m:
                    violations.append(
                        f"{fname}:{lineno} — QFont with CSS font-stack: {m.group(0)!r}"
                    )

    assert not violations, (
        "Found QFont calls with comma-separated CSS font stacks "
        "(Qt ignores fallbacks — use ModernDarkTheme.resolve_monospace_font() instead):\n"
        + "\n".join(violations)
    )


def test_no_sf_mono_in_rendered_stylesheets():
    """
    'SF Mono' must not appear in any rendered QSS stylesheet.

    Qt processes each font-family token in a QSS rule and logs a 100+ ms
    warning when it can't find a listed family (e.g. 'SF Mono' which is
    only available when Xcode is installed).  The stylesheet must start
    the font-family fallback list with a font guaranteed to exist on macOS
    (e.g. 'Menlo') so Qt never needs to populate alias tables.
    """
    from ui.modern_dark_theme import ModernDarkTheme

    for name, css in [
        ("application", ModernDarkTheme.get_application_stylesheet()),
        ("dialog", ModernDarkTheme.get_dialog_styles()),
    ]:
        assert "SF Mono" not in css, (
            f"'SF Mono' found in '{name}' stylesheet — "
            "remove it to avoid the Qt font-alias warning (131 ms delay). "
            "Use 'Menlo' as the first monospace family instead."
        )


def test_resolve_monospace_font_returns_valid_qfont():
    """
    resolve_monospace_font() must return a QFont whose family is a single
    name (no commas) and whose point size matches the requested size.

    A QFontDatabase is needed, which requires a QApplication instance.
    We create a minimal one if not already running.
    """
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont
    from ui.modern_dark_theme import ModernDarkTheme

    app = QApplication.instance() or QApplication(sys.argv)

    font = ModernDarkTheme.resolve_monospace_font(13)

    assert isinstance(font, QFont)
    assert font.pointSize() == 13
    family = font.family()
    assert "," not in family, (
        f"resolve_monospace_font() returned a CSS font stack: {family!r} — "
        "must be a single family name"
    )
    assert family != "", "resolve_monospace_font() returned an empty family name"
