#!/usr/bin/env python3
"""
tsh - A basic shell

This script provides a simple shell interface that can execute most Unix commands.
It also saves all the commands in the ~/.tsh_history and provides support for 
the history command.
"""
import os
import subprocess
import sys
from pathlib import Path

from sshkeyboard import listen_keyboard, stop_listening

hist_loc = Path.home() / ".tsh_history"


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
        if self.history and self.history[-1] == "history" and cmd == "history":
            return
        self.history.append(cmd)
        self.history_index = len(self.history) - 1

    def ch_dir(self, directory: Path | str):
        """Handles cd command"""
        try:
            os.chdir(directory)
            self.add_history(f"cd {directory}")
        except FileNotFoundError:
            print(f"File {directory} not found!")
            return
        except PermissionError:
            print(f"No execute permission on {directory}!")
            return

    def exec_command(self, command: str):
        """Execute the user command by creating a sub process and save to history"""
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
        try:
            proc = subprocess.run(command, shell=True, capture_output=True, check=True)
            print(proc.stdout.decode(), end="")
            print(proc.stderr.decode(), end="")
            if proc.returncode == 0:
                self.add_history(command)
        except subprocess.CalledProcessError:
            print(f"{command}: command not found")
        except KeyboardInterrupt:
            print("Process terminated")
        return True

    def process_key(self, key: str):
        """Processes user key press
        enter executes the command
        backspace deletes last character on the shell
        exit terminates the session"""

        if key == "enter":
            print()
            if not self.exec_command("".join(self.buffer).strip()):
                self.terminate()
            self.buffer = []
            print("tsh>", end="", flush=True)
        elif key == "backspace":
            if self.buffer:
                self.buffer.pop()
            print("\r\033[K", end="", flush=True)
            print(f'tsh>{"".join(map(str, self.buffer))}', end="", flush=True)
        elif key == "up":
            self.handle_history_event("up")
        elif key == "down":
            self.handle_history_event("down")
        elif key in {"right", "left", "home", "end", "pagedown", "pageup", "delete"}:
            pass
        # TODO: Implement Tab functionality
        elif key == "tab":
            pass
        else:
            if key == "space":
                key = " "
            self.buffer.append(key)
            print(key, end="", flush=True)

    def handle_history_event(self, key: str):
        """Shows the previous/next command if the up or down arrow is pressed"""
        cmd = ""
        if key == "up":
            if len(self.history) > 0 and len(self.history) > self.history_index:
                cmd = self.history[self.history_index]
            else:
                cmd = ""
            if self.history_index > 0:
                self.history_index -= 1
        elif key == "down":
            if len(self.history) > 0 and len(self.history) > self.history_index:
                cmd = self.history[self.history_index]
            else:
                cmd = ""
            if self.history_index < len(self.history):
                self.history_index += 1
        padding = len(self.previous_command) - len(cmd)
        padding = max(padding, 0)
        print(f"\rtsh>{cmd}{' ' * padding}", end="", flush=True)
        sys.stdout.write("\b" * padding)
        sys.stdout.flush()
        self.buffer = list(cmd)
        self.previous_command = cmd

    def on_release(self, key: str):
        """Handles key release events"""
        if key == "esc":
            self.save_history()
            sys.exit()

    def save_history(self):
        """Saves the current history to the .tsh_history"""
        if not hist_loc.is_file():
            hist_loc.touch()
            print("creating history file")
        with open(hist_loc, "a", encoding="utf-8") as f:
            for i in range(self.old_history_index, len(self.history)):
                f.write(self.history[i] + "\n")
            # f.write("\n".join(self.history[self.old_history_index :]))

    def terminate(self):
        """Exits the shell"""
        self.save_history()
        stop_listening()
        try:
            sys.exit()
        except SystemExit:
            pass

    def get_history(self):
        """returns the entire history of commands"""
        return self.history

    def init_history(self):
        """Loads the tsh_history file"""
        if hist_loc.is_file():
            with open(hist_loc, "r", encoding="utf-8") as f:
                self.history.extend(line.strip() for line in f.readlines())
        self.old_history_index = len(self.history)
        self.history_index = self.old_history_index - 1


def main():
    """Main entry point"""
    handler = CommandHandler()
    print("tsh>", end="", flush=True)
    listen_keyboard(
        on_press=handler.process_key,
        on_release=handler.on_release,
        delay_second_char=0.05,
    )


if __name__ == "__main__":
    main()
