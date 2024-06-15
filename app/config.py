"""
utility class to store helper methods for storage and retrival of config attributes
"""

import re
from pathlib import Path


class Config:
    """
    This class provides the ability to get handle the behavior of the configuration files for ysh
    """

    _conf = Path.home() / ".yshrc"
    _alias_to_cmd = {}
    _pattern = r'alias\s+([^"]+)\s*=\s*"(.+)"'

    def __init__(self) -> None:
        if not self._conf.is_file():
            self._conf.touch()
        self._load_alias()

    def get_alias(self) -> dict[str, str]:
        """
        returns a dict where keys are alias
        and values are corresponding commands
        """
        return self._alias_to_cmd

    def get_config_loc(self) -> Path:
        """
        returns the location of the config file
        """
        return self._conf

    def _load_alias(self) -> None:
        with open(self._conf, "r", encoding="utf-8") as f:
            conf_lines = f.readlines()
        for line in conf_lines:
            match = re.search(self._pattern, line)
            if match:
                alias = match.group(1)
                cmd = match.group(2)
                self._alias_to_cmd[alias] = cmd
