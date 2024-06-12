"""
test suite for tsh

"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from app.ysh import CommandHandler


class TestYsh(unittest.TestCase):
    """test class for ysh"""

    def setUp(self):
        self.handler = CommandHandler()
        self.original_cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.original_cwd)

    @patch("subprocess.run")
    def test_exec_command(self, mock_run):
        """test if command execution properly works"""
        mock_run.return_value = MagicMock(
            returncode=0, stdout=b"Test Output\n", stderr=b""
        )

        result = self.handler.exec_command("echo Test")

        self.assertTrue(result)
        self.assertIn("echo Test", self.handler.history)
        self.assertEqual(self.handler.history_index, len(self.handler.history))
        mock_run.assert_called_with(["echo", "Test"], capture_output=True, check=True)

    def test_ch_dir(self):
        """test change directory implementation"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.handler.ch_dir(tmpdirname)
            self.assertEqual(os.getcwd(), tmpdirname)
            self.assertIn(f"cd {tmpdirname}", self.handler.history)

        try:
            self.handler.ch_dir("/nonexistent_directory")
        except FileNotFoundError:
            pass

    def test_process_key(self):
        """test if key press is properly stored and processed in the buffer"""
        self.handler.buffer = list("echo Hello")
        self.handler.process_key("enter")
        self.assertIn("echo Hello", self.handler.history)

        self.handler.buffer = list("cd /tmp")
        self.handler.process_key("enter")
        self.assertIn("cd /tmp", self.handler.history)

    def test_handle_history_event(self):
        """test if the history is properly retrieved"""
        self.handler.history = ["cmd1", "cmd2", "cmd3"]
        self.handler.history_index = 3
        self.handler.handle_history_event("up")  # initial up will bring up last command
        self.assertEqual(self.handler.buffer, list(self.handler.history[2]))
        self.handler.handle_history_event("up")
        self.assertEqual(self.handler.buffer, list(self.handler.history[1]))

        self.handler.handle_history_event("down")
        self.assertEqual(self.handler.buffer, list(self.handler.history[2]))

        self.handler.history_index = 3
        self.handler.handle_history_event("down")
        self.assertEqual(self.handler.buffer, list(self.handler.history[2]))

        self.handler.history = []
        self.handler.handle_history_event("down")
        self.assertEqual(self.handler.buffer, list(""))

        self.handler.handle_history_event("up")
        self.assertEqual(self.handler.buffer, list(""))

    @patch("os.listdir")
    def test_tab_completion(self, mock_listdir):
        """mock tab functionality"""
        mock_listdir.return_value = ["file1.txt", "file2.txt", "directory"]
        self.handler.buffer = list("cd fi")
        self.handler.handle_tab_event()
        self.assertEqual(self.handler.buffer, list("cd file"))

    def test_save_and_load_history(self):
        """test if the history is persistent"""
        test_history = ["echo Hello", "ls", "cd /"]
        self.handler.init_history()
        self.handler.history.extend(test_history[:])
        self.handler.save_history()

        handler2 = CommandHandler()
        handler2.init_history()

        self.assertEqual(handler2.history[-3:], test_history)


if __name__ == "__main__":
    unittest.main()
