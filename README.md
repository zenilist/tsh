# tsh (Basic Shell Implementation)

tsh is a basic shell implementation written in Python that allows users to execute Unix commands. It also features command history functionality, enabling users to navigate through previously executed commands using the up/down arrow keys.

## Features

- Execute Unix commands directly within the shell.
- Command history: Navigate through previously executed commands using up/down arrow keys.
- Command history is persistent: All executed commands are saved in `~/.tsh_history`.
- [Future] Tab completion functionality.

## Installation

1. Clone the repository:

    ```
    git clone https://github.com/zenilist/tsh.git
    ```
2. Install dependencies using pip:

    ```
    cd tsh/
    ```

3. Install dependencies using pip:

    ```
    pip install -r requirements.txt
    ```

3. Run the shell:

    ```
    ./tsh.py
    ```

## Usage

Simply run `./tsh.py` to start the shell. You can then type Unix commands directly into the shell prompt and press Enter to execute them.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
