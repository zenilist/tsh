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

    def _fill_commands(self) -> None:
        paths = ["/bin", "usr/bin", "sbin", "usr/sbin"]
        self.commands = set(paths)

        for path in paths:
            if os.path.isdir(path):
                for cmd in os.listdir(path):
                    cmd_path = os.path.join(path, cmd)
                    if os.access(cmd_path, os.X_OK) and not os.path.isdir(cmd_path):
                        self.commands.add(cmd)
