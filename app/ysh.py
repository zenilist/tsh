"""
ysh - A basic shell

This script provides a simple shell interface that can execute most Unix commands.
It also saves all the commands in the ~/.ysh_history and provides support for 
the history command.
"""

import os
import shlex
import subprocess
import sys
from pathlib import Path

from sshkeyboard import listen_keyboard, stop_listening

try:
    from app._commands import Commands
    from app.config import Config
except ModuleNotFoundError:
    from _commands import Commands
    from config import Config

hist_loc = Path.home() / ".ysh_history"
PROMPT = "ysh>"
YELLOW = "\033[93m"
DEFAULT = "\033[0m"
RED = "\033[91m"
BLUE = "\033[94m"


class CommandHandler:
    """Handles unix command executions and parsing user input for the shell"""

    def __init__(self):
        self.buffer = []
        self.history_settings = {
            "history": [],
            "history_index": 0,
            "old_history_index": 0,
            "previous_command": "",
        }
        self.init_history()
        self.alias_cmds = Config().get_alias()
        self._fill_commands()
        self.colorized = False
        self.sep = False
        self.command = ""

    def _fill_commands(self) -> None:
        self.commands = Commands().get_commands()
        self.commands.add("history")
        self.commands.add("cd")
        self.commands.add("exit")
        self.commands.update(self.alias_cmds)

    def add_history(self, cmd: str):
        """Adds command to the current history list
        ignores repeated history command"""
        if (
            self.history_settings["history"]
            and self.history_settings["history"][-1] == "history"
            and cmd == "history"
            or cmd == ""
        ):
            return
        self.history_settings["history"].append(cmd)
        self.history_settings["history_index"] = len(self.history_settings["history"])

    def ch_dir(self, directory: Path | str):
        """Handles cd command"""
        try:
            os.chdir(directory)
            self.add_history(f"cd {directory}")
        except FileNotFoundError:
            print(f"File {directory} not found!")
        except PermissionError:
            print(f"No execute permission on {directory}!")
        except NotADirectoryError:
            print(f"{directory} is not a directory!")

    def _change_dir(self, args: list[str]) -> None:
        if len(args) < 2:
            directory = Path.home()
        else:
            directory = args[1]
        self.ch_dir(directory)

    def _print_history(self) -> None:
        for cmd in self.get_history():
            print(cmd)

    def exec_command(self, command: str):
        """Execute the user command by creating a sub process and save to history"""
        self.add_history(command)
        if command in self.alias_cmds:
            command = self.alias_cmds[command]
        if command == "":
            return True
        if command == "exit":
            return False
        if command.startswith("cd"):
            self._change_dir(command.split())
            return True
        if command == "history":
            self._print_history()
            return True
        try:
            cmd, args = shlex.split(command)
        except ValueError:
            cmd = command
            args = ""
        try:
            output, error = self._run_subprocess(cmd, args)
            print(output, end="")
            print(error, end="")
        except ValueError:
            print(f"Failed to run command: {cmd}")
        except subprocess.CalledProcessError as err:
            print(err.stderr.decode(), end="")
        except FileNotFoundError:
            print(f"Could not find command: {cmd}")
        except PermissionError:
            print(f"Could not find command: {cmd}")
        except KeyboardInterrupt:
            print("Process terminated")
        return True

    def _run_subprocess(self, cmd: str, args) -> tuple[str, str]:
        return subprocess.Popen(
            [cmd, args] if args else [cmd],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).communicate()

    def handle_history_event(self, key: str):
        """Shows the previous/next command if the up or down arrow is pressed"""
        cmd = ""
        if key == "up":
            if self.history_settings["history_index"] > 0:
                self.history_settings["history_index"] -= 1
            if (
                len(self.history_settings["history"]) > 0
                and len(self.history_settings["history"])
                > self.history_settings["history_index"]
            ):
                cmd = self.history_settings["history"][
                    self.history_settings["history_index"]
                ]
        elif key == "down":
            if (
                self.history_settings["history_index"]
                < len(self.history_settings["history"]) - 1
            ):
                self.history_settings["history_index"] += 1
            if (
                len(self.history_settings["history"]) > 0
                and len(self.history_settings["history"])
                > self.history_settings["history_index"]
            ):
                cmd = self.history_settings["history"][
                    self.history_settings["history_index"]
                ]
            elif self.history_settings["history"]:
                cmd = self.history_settings["history"][
                    self.history_settings["history_index"] - 1
                ]  # get last command
        padding = len(self.history_settings["previous_command"]) - len(cmd)
        padding = max(padding, 0)
        print(f"\r{YELLOW}{PROMPT}{DEFAULT}{cmd}{' ' * padding}", end="", flush=True)
        sys.stdout.write("\b" * padding)
        sys.stdout.flush()
        self.buffer = list(cmd)
        self.history_settings["previous_command"] = cmd

    def terminate(self):
        """Exits the shell"""
        self.save_history()
        stop_listening()
        try:
            sys.stdout.flush()
            sys.exit()
        except SystemExit:
            pass

    def process_key(self, key: str):
        """Processes user key press
        enter executes the command
        backspace deletes last character on the shell
        exit terminates the session"""

        if key == "enter":
            self._enter()
        elif key == "backspace":
            self._backspace()
        elif key == "up":
            self.handle_history_event("up")
        elif key == "down":
            self.handle_history_event("down")
        elif key in {"right", "left", "home", "end", "pagedown", "pageup", "delete"}:
            pass
        elif key == "tab":
            self.handle_tab_event()
        else:
            self._default(key)

    def _default(self, key) -> None:
        if key == "space":
            key = " "
            self.sep = True
        self.buffer.append(key)
        buffer = "".join(self.buffer)
        if self._is_command(buffer):
            self._colorize_cmd(RED)
            self.colorized = True
            self.command = buffer
        else:
            if self.colorized and not self.sep:
                self._colorize_cmd(DEFAULT)
                self.colorized = False
            else:
                print(key, end="", flush=True)

    def _enter(self) -> None:
        print()
        command = "".join(self.buffer).strip()
        self.command = ""
        self.sep = False
        if command != "" and not self.exec_command(command):
            self.terminate()
        else:
            self.buffer = []
            print(f"{YELLOW}{PROMPT}{DEFAULT}", end="", flush=True)

    def _backspace(self) -> None:
        if self.buffer:
            self.buffer.pop()
            if " " not in self.buffer:
                self.sep = False
            if len(self.buffer) < len(self.command):
                self.command = ""
        if self.command != "":
            print("\r\033[K", end="", flush=True)
            print(
                f"{YELLOW}{PROMPT}{RED}{self.command}{DEFAULT}"
                f'{"".join(self.buffer[len(self.command):])}',
                end="",
                flush=True,
            )
        else:
            print("\r\033[K", end="", flush=True)
            print(
                f'{YELLOW}{PROMPT}{DEFAULT}{"".join(map(str, self.buffer))}',
                end="",
                flush=True,
            )

    def _is_command(self, buffer: str) -> bool:
        if buffer in self.commands:
            return True
        return False

    def _colorize_cmd(self, color: str) -> None:
        padding = len(self.buffer) - 1
        print(
            f"\r{YELLOW}{PROMPT}{color}{''.join(self.buffer)}{DEFAULT}{' ' * padding}",
            end="",
            flush=True,
        )
        sys.stdout.write("\b" * padding)
        sys.stdout.flush()

    def get_completions(self, text):
        """Get a list of possible completions for the given text"""
        if "~" in text:
            text = os.path.expanduser(text)

        if os.path.sep not in text:
            completions = [cmd for cmd in os.listdir(".") if cmd.startswith(text)]
        else:
            dirname, rest = os.path.split(text)
            if not dirname:
                dirname = "."
            try:
                completions = [
                    os.path.join(dirname, cmd)
                    for cmd in os.listdir(dirname)
                    if cmd.startswith(rest)
                ]
            except FileNotFoundError:
                completions = []

        return completions

    def get_prefix_cmd(self):
        """returns prefix cmd for use in a tab completion event"""
        buffer_str = "".join(self.buffer)
        valid_cmds = {"cd ", "ls ", "pwd ", "grep "}
        for cmd in valid_cmds:
            if buffer_str.startswith(cmd):
                return cmd
        return ""

    def handle_tab_event(self):
        """Handles the tab completion event"""
        prefix_cmd = self.get_prefix_cmd()
        if not prefix_cmd:
            return
        text_to_complete = "".join(self.buffer)[len(prefix_cmd) :]
        completions = self.get_completions(text_to_complete)
        if completions:
            common_prefix = os.path.commonprefix(completions)
            self.buffer = list(prefix_cmd + common_prefix)
            print("\r\033[K", end="", flush=True)
            print(
                f'{YELLOW}{PROMPT}{DEFAULT}{"".join(map(str, self.buffer))}',
                end="",
                flush=True,
            )
            if len(completions) > 1:
                print("\n" + "  ".join(completions))
                print(
                    f'{YELLOW}{PROMPT}{DEFAULT}{"".join(map(str, self.buffer))}',
                    end="",
                    flush=True,
                )

    def on_release(self, key: str):
        """Handles key release events"""
        if key == "esc":
            self.save_history()
            sys.exit()

    def save_history(self):
        """Saves the current history to the .ysh_history"""
        if not hist_loc.is_file():
            hist_loc.touch()
        with open(hist_loc, "a", encoding="utf-8") as f:
            for i in range(
                self.history_settings["old_history_index"],
                len(self.history_settings["history"]),
            ):
                f.write(self.history_settings["history"][i] + "\n")
            # f.write("\n".join(self.history[self.old_history_index :]))

    def get_history(self):
        """returns the entire list of ran commands"""
        return self.history_settings["history"]

    def init_history(self):
        """Loads the ysh_history file"""
        if hist_loc.is_file():
            with open(hist_loc, "r", encoding="utf-8") as f:
                self.history_settings["history"].extend(
                    line.strip() for line in f.readlines()
                )
        self.history_settings["old_history_index"] = len(
            self.history_settings["history"]
        )
        self.history_settings["history_index"] = (
            self.history_settings["old_history_index"] - 1
        )


def main():
    """Main entry point"""
    handler = CommandHandler()
    print(f"{YELLOW}{PROMPT}{DEFAULT}", end="", flush=True)
    listen_keyboard(
        on_press=handler.process_key,
        on_release=handler.on_release,
        delay_second_char=0.05,
    )


if __name__ == "__main__":
    main()
