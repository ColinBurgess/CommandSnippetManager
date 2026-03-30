"""
Clipboard and terminal interaction utilities.
"""

import subprocess
from typing import Tuple
from PyQt6.QtWidgets import QApplication

def copy_to_clipboard(text: str) -> None:
    """
    Copy text to system clipboard.

    Args:
        text: Text to copy
    """
    clipboard = QApplication.clipboard()
    clipboard.setText(text)

def execute_in_terminal_macos(command: str) -> Tuple[bool, str, str]:
    """
    Execute a command in a new Terminal.app window on macOS.

    Args:
        command: Command to execute
    """
    # Escape single quotes in the command
    escaped_command = command.replace("'", "'\\''")

    # Create the AppleScript command
    apple_script = f'''
    tell application "Terminal"
        activate
        do script "{escaped_command}"
    end tell
    '''

    # Return a tuple so callers can handle success/failure consistently.
    try:
        completed = subprocess.run(
            ['osascript', '-e', apple_script],
            check=True,
            capture_output=True,
            text=True
        )
        return True, completed.stdout or "", completed.stderr or ""
    except subprocess.CalledProcessError as e:
        return False, e.stdout or "", e.stderr or str(e)
    except Exception as e:
        return False, "", str(e)
