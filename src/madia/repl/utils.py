import re
import shlex
import sys
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.formatters import TerminalFormatter


def detect_and_highlight_code(text):
    code_pattern = re.compile(r"```(.*?)\n(.*?)```", re.DOTALL)
    if not text:
        return ""
    for match in code_pattern.findall(text):
        lexer_name, code_block = match
        if all(
            lexer_name.lower() not in [str(x).lower() for x in lexer]
            for lexer in get_all_lexers()
        ):
            continue
        lexer = get_lexer_by_name(lexer_name.strip())
        highlighted_code = highlight(code_block, lexer, TerminalFormatter())
        text = text.replace(
            f"```{lexer_name}\n{code_block}```",
            f"```{lexer_name}\n{highlighted_code}\n```",
        )

    return text


def delete_stdout_content(content):
    number_of_lines = content.count("\n")

    for line_no in range(number_of_lines):
        # Move cursor up one line
        sys.stdout.write("\x1b[1A")
        sys.stdout.flush()

        # Erase current line
        sys.stdout.write(
            "\r" + " " * len(content.split("\n")[number_of_lines - 1 - line_no]) + "\r"
        )
        sys.stdout.flush()
    if number_of_lines == 0:
        sys.stdout.write("\r")
    sys.stdout.flush()


def safe_shlex_split(text):
    try:
        return shlex.split(text)
    except ValueError as err:
        if "No closing quotation" not in str(err):
            raise

        char_list = ["'", '"']

        # Find the last occurrence of each character
        positions = {char: text.rfind(char) for char in char_list}

        # Get the character with the maximum position
        closest_char = max(positions, key=positions.get)
        return shlex.split(text + closest_char)


def execute_command(command_str, options_tree):
    commands = safe_shlex_split(command_str)

    cur_tree = options_tree
    fn = None  # Placeholder for our function

    # Loop until we either find a callable or exhaust the commands list
    for i, cmd in enumerate(commands):
        if cmd not in cur_tree:
            return f"Invalid command: {cmd}"

        if callable(cur_tree[cmd]):
            fn = cur_tree[cmd]
            break  # We've found our function, stop here.
        cur_tree = cur_tree[cmd]

    if not fn:
        return f"'{command_str}' does not map to a valid function."
    args = commands[i + 1 :]  # Extract the remaining commands as arguments
    return fn(" ".join(args))
