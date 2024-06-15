"""
test module for ysh configuration
"""

import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from app.config import Config


class TestConfig(unittest.TestCase):
    """
    unit test class for the config class
    """

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='alias ll="ls -l"\nalias la="ls -a"\n',
    )
    @patch.object(Path, "is_file", return_value=True)
    def test_load_alias(self, _mock_is_file, _m_open):
        """
        test if the config properly stores the alias
        """
        config = Config()
        expected_aliases = {"ll": "ls -l", "la": "ls -a"}
        self.assertEqual(config.get_alias(), expected_aliases)

    @patch("builtins.open", new_callable=mock_open, read_data="")
    @patch.object(Path, "is_file", return_value=False)
    def test_init_creates_file_if_not_exists(self, _mock_is_file, m_open):
        """
        test if the config creates a new file
        """
        Config()
        m_open.assert_called_once_with(Path.home() / ".yshrc", "r", encoding="utf-8")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='alias ll="ls -l"\nalias la="ls -a"\n',
    )
    @patch.object(Path, "is_file", return_value=True)
    def test_get_alias(self, _mock_is_file, _m_open):
        """
        test alias retreival
        """
        config = Config()
        aliases = config.get_alias()
        self.assertEqual(aliases["ll"], "ls -l")
        self.assertEqual(aliases["la"], "ls -a")


if __name__ == "__main__":
    unittest.main()
