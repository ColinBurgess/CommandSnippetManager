"""
Utility functions for the Command Snippet Management Application.
"""

import subprocess
import os
from PyQt6.QtWidgets import QApplication


def copy_to_clipboard(text):
    """Copy text to system clipboard."""
    clipboard = QApplication.clipboard()
    clipboard.setText(text)


def execute_command_basic(command):
    """
    Basic command execution using subprocess.

    NOTE: This is a simple implementation that may not work well with
    commands requiring environment sourcing (like aws-vault exec).
    Future enhancement: Consider using osascript for macOS terminal integration.
    """
    try:
        # For basic commands, use subprocess
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def execute_in_terminal_macos(command):
    """
    Execute command in a new macOS Terminal window.

    TODO: This is a placeholder for more advanced terminal integration.
    Consider using osascript to open Terminal.app or iTerm2 with the command.
    """
    try:
        # Basic approach: open Terminal and execute command
        # This creates a new terminal window and runs the command
        terminal_command = f'''
        osascript -e 'tell application "Terminal"
            activate
            do script "{command.replace('"', '\\"')}"
        end tell'
        '''
        subprocess.run(terminal_command, shell=True)
        return True, "Command sent to Terminal", ""
    except Exception as e:
        return False, "", str(e)
