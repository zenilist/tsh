#!/usr/bin/env python3
"""
ysh - A basic shell

This script provides a simple shell interface that can execute most Unix commands.
It also saves all the commands in the ~/.ysh_history and provides support for 
the history command.
"""
import os
import subprocess
import sys
from pathlib import Path

from sshkeyboard import listen_keyboard, stop_listening

hist_loc = Path.home() / ".ysh_history"
PROMPT = "ysh>"
COLOR = "\033[93m"  # set to Yellow
DEFAULT = "\033[0m"


class CommandHandler:
    """Handles unix command executions and parsing user input for the shell"""

    def __init__(self):
        self.buffer = []
        self.history = []
        self.history_index = 0
        self.old_history_index = 0
        self.previous_command = ""
        self.init_history()

    def add_history(self, cmd: str):
        """Adds command to the current history list
        ignores repeated history command"""
        if (
            self.history
            and self.history[-1] == "history"
            and cmd == "history"
            or cmd == ""
        ):
            return
        self.history.append(cmd)
        self.history_index = len(self.history)

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

    def exec_command(self, command: str):
        """Execute the user command by creating a sub process and save to history"""
        if command == "":
            return
        if command == "exit":
            self.add_history(command)
            return False
        if command.startswith("cd"):
            args = command.split()
            if len(args) < 2:
                directory = Path.home()
            else:
                directory = args[1]

            self.ch_dir(directory)
            return True
        if command == "history":
            for cmd in self.get_history():
                print(cmd)
            self.add_history(command)
            return True
        has_args = False
        try:
            cmd, args = command.split(" ")
            has_args = True
        except ValueError:
            cmd = command
            args = ""
        try:
            if has_args:
                proc = subprocess.run([cmd, args], capture_output=True, check=True)
            else:
                proc = subprocess.run([cmd], capture_output=True, check=True)
            print(proc.stdout.decode(), end="")
            print(proc.stderr.decode(), end="")
            if proc.returncode == 0:
                self.add_history(command)
        except subprocess.CalledProcessError as err:
            print(err.stderr.decode(), end="")
        except FileNotFoundError:
            print(f"Could not find command: {cmd}")
        except PermissionError:
            print(f"Could not find command: {cmd}")
        except KeyboardInterrupt:
            print("Process terminated")
        return True

    def handle_history_event(self, key: str):
        """Shows the previous/next command if the up or down arrow is pressed"""
        cmd = ""
        if key == "up":
            if self.history_index > 0:
                self.history_index -= 1
            if len(self.history) > 0 and len(self.history) > self.history_index:
                cmd = self.history[self.history_index]
        elif key == "down":
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
            if len(self.history) > 0 and len(self.history) > self.history_index:
                cmd = self.history[self.history_index]
            elif self.history:
                cmd = self.history[self.history_index - 1]  # get last command
        padding = len(self.previous_command) - len(cmd)
        padding = max(padding, 0)
        print(f"\r{COLOR}{PROMPT}{DEFAULT}{cmd}{' ' * padding}", end="", flush=True)
        sys.stdout.write("\b" * padding)
        sys.stdout.flush()
        self.buffer = list(cmd)
        self.previous_command = cmd

    def terminate(self):
        """Exits the shell"""
        self.save_history()
        stop_listening()
        try:
            sys.exit()
        except SystemExit:
            pass

    def process_key(self, key: str):
        """Processes user key press
        enter executes the command
        backspace deletes last character on the shell
        exit terminates the session"""

        if key == "enter":
            print()
            command = "".join(self.buffer).strip()
            if command != "" and not self.exec_command(command):
                self.terminate()
            self.buffer = []
            print(f"{COLOR}{PROMPT}{DEFAULT}", end="", flush=True)
        elif key == "backspace":
            if self.buffer:
                self.buffer.pop()
            print("\r\033[K", end="", flush=True)
            print(
                f'{COLOR}{PROMPT}{DEFAULT}{"".join(map(str, self.buffer))}',
                end="",
                flush=True,
            )
        elif key == "up":
            self.handle_history_event("up")
        elif key == "down":
            self.handle_history_event("down")
        elif key in {"right", "left", "home", "end", "pagedown", "pageup", "delete"}:
            pass
        elif key == "tab":
            self.handle_tab_event()
        else:
            if key == "space":
                key = " "
            self.buffer.append(key)
            print(key, end="", flush=True)

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
                f'{COLOR}{PROMPT}{DEFAULT}{"".join(map(str, self.buffer))}',
                end="",
                flush=True,
            )
            if len(completions) > 1:
                print("\n" + "  ".join(completions))
                print(
                    f'{COLOR}{PROMPT}{DEFAULT}{"".join(map(str, self.buffer))}',
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
            for i in range(self.old_history_index, len(self.history)):
                f.write(self.history[i] + "\n")
            # f.write("\n".join(self.history[self.old_history_index :]))

    def get_history(self):
        """returns the entire list of ran commands"""
        return self.history

    def init_history(self):
        """Loads the ysh_history file"""
        if hist_loc.is_file():
            with open(hist_loc, "r", encoding="utf-8") as f:
                self.history.extend(line.strip() for line in f.readlines())
        self.old_history_index = len(self.history)
        self.history_index = self.old_history_index - 1


def main():
    """Main entry point"""
    handler = CommandHandler()
    print(f"{COLOR}{PROMPT}{DEFAULT}", end="", flush=True)
    listen_keyboard(
        on_press=handler.process_key,
        on_release=handler.on_release,
        delay_second_char=0.05,
    )


if __name__ == "__main__":
    main()
