"""
Module to store various command related functionality
"""

import os


class Commands:
    """
    Utility class for commands retrieval
    """

    def __init__(self) -> None:
        self.commands = set()
        self._fill_commands()

    def get_commands(self) -> set[str]:
        """
        Returns the list of all the recognized executables in the bin directories

        Returns:
                commands(set(str)): Set of all the commands
        """
        return self.commands

    def search_command(self, command_name: str) -> str:
        """
        Search for a specific command and return its full path if found.

        Args:
            command_name (str): Name of the command to search for.

        Returns:
            str: Full path of the command if found, empty string if not found.
        """
        for path in self.commands:
            cmd_path = os.path.join(path, command_name)
            if (
                os.path.exists(cmd_path)
                and os.access(cmd_path, os.X_OK)
                and not os.path.isdir(cmd_path)
            ):
                return cmd_path
        return ""

    def _fill_commands(self) -> None:
        paths = ["/bin", "usr/bin", "sbin", "usr/sbin"]
        self.commands = set(paths)

        for path in paths:
            if os.path.isdir(path):
                for cmd in os.listdir(path):
                    cmd_path = os.path.join(path, cmd)
                    if os.access(cmd_path, os.X_OK) and not os.path.isdir(cmd_path):
                        self.commands.add(cmd)
