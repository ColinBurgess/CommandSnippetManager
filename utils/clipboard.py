"""
Clipboard and terminal interaction utilities.
"""

import subprocess
import os
from PyQt6.QtWidgets import QApplication

def copy_to_clipboard(text: str) -> None:
    """
    Copy text to system clipboard.

    Args:
        text: Text to copy
    """
    clipboard = QApplication.clipboard()
    clipboard.setText(text)

def execute_in_terminal_macos(command: str) -> None:
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

    # Execute the AppleScript
    try:
        subprocess.run(['osascript', '-e', apple_script], check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to execute command in Terminal: {e}")
