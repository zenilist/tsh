#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

from sshkeyboard import listen_keyboard, stop_listening

hist_loc = Path.home() / ".tsh_history"


class CommandHandler:
    def __init__(self):
        self.buffer = []
        self.history = []
        self.history_index = 0
        self.old_history_index = 0
        self.previous_command = ""
        self.init_history()

    def add_history(self, cmd: str):
        if self.history and self.history[-1] == "history" and cmd == "history":
            return
        self.history.append(cmd)
        self.history_index = len(self.history) - 1

    def ch_dir(self, dir: Path | str):
        try:
            os.chdir(dir)
            self.add_history(f"cd {dir}")
        except FileNotFoundError:
            print(f"File {dir} not found!")
            return
        except PermissionError:
            print(f"No execute permission on {dir}!")
            return

    def exec_command(self, command: str):
        """Execute the user command by creating a sub process and save to history"""
        if command == "exit":
            self.add_history(command)
            return False
        if command.startswith("cd"):
            args = command.split()
            if len(args) < 2:
                dir = Path.home()
            else:
                dir = args[1]

            self.ch_dir(dir)
            return True
        if command == "history":
            for cmd in self.get_history():
                print(cmd)
            self.add_history(command)
            return True
        try:
            proc = subprocess.run(command, shell=True, capture_output=True)
            print(proc.stdout.decode(), end="")
            print(proc.stderr.decode(), end="")
            if proc.returncode == 0:
                self.add_history(command)
        except subprocess.CalledProcessError:
            print(
                f"Encountered unexcepted error when calling command: {command}", end=""
            )
        except KeyboardInterrupt:
            print("Process terminated")
        return True

    def process_key(self, key):
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
        elif key == "right":
            pass
        elif key == "left":
            pass
        elif key == "home":
            pass
        elif key == "end":
            pass
        elif key == "pageup":
            pass
        elif key == "pagedown":
            pass
        # TODO: IMplement Tab functionality
        elif key == "tab":
            pass
        elif key == "delete":
            pass

        else:
            if key == "space":
                key = " "
            self.buffer.append(key)
            print(key, end="", flush=True)

    def handle_history_event(self, key):
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
        if padding < 0:
            padding = 0
        print(f"\rtsh>{cmd}{' ' * padding}", end="", flush=True)
        sys.stdout.write("\b" * padding)
        sys.stdout.flush()
        self.buffer = list(cmd)
        self.previous_command = cmd

    def on_release(self, key):
        """Handles key release events"""
        if key == "esc":
            self.save_history()
            sys.exit()

    def save_history(self):
        if not hist_loc.is_file():
            hist_loc.touch()
            print("creating history file")
        with open(hist_loc, "a") as f:
            for i in range(self.old_history_index, len(self.history)):
                f.write(self.history[i] + "\n")
            # f.write("\n".join(self.history[self.old_history_index :]))

    def terminate(self):
        self.save_history()
        stop_listening()
        try:
            sys.exit()
        except:
            pass

    def get_history(self):
        return self.history

    def init_history(self):
        if hist_loc.is_file():
            with open(hist_loc, "r") as f:
                self.history.extend(line.strip() for line in f.readlines())
        self.old_history_index = len(self.history)
        self.history_index = self.old_history_index - 1


def main():
    handler = CommandHandler()
    print("tsh>", end="", flush=True)
    listen_keyboard(
        on_press=handler.process_key,
        on_release=handler.on_release,
        delay_second_char=0.05,
    )


if __name__ == "__main__":
    main()
