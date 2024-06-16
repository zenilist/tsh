# ysh

ysh is a basic shell implementation written in Python that allows users to execute Unix commands. It also features command history functionality, enabling users to navigate through previously executed commands using the up/down arrow keys.

## Features

- Execute Unix commands directly within the shell.
- Command history: Navigate through previously executed commands using up/down arrow keys.
- Command history is persistent: All executed commands are saved in `~/.ysh_history`.
- Tab completion functionality.
- Aliases can be saved in the config '~/.yashrc' file. eg: ```alias ll = 'ls -l'```
- Syntax highlighting (currently only highlights known commands and aliases)

## Installation

You can install ysh using pip

    pip install ysh    

## Usage

Simply run `tsh` to start the shell. You can then type Unix commands directly into the shell prompt and press Enter to execute them.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
