from __future__ import annotations

import contextlib
import re
import shlex
import sys
import threading

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import get_all_lexers, get_lexer_by_name


def detect_and_highlight_code(text):
    """
    Detect and highlight code blocks in text.

    This function looks for Markdown-style code blocks in the provided
    text and highlights them using Pygments. It searches for code blocks
    of the form:

    ```language
    code
    ```

    And highlights the code block using the specified language lexer.

    Parameters
    ----------
    text : str
        The text to search for code blocks.

    Returns
    -------
    str
        The text with detected code blocks highlighted.

    Examples
    --------

    .. code-block:: python

        from madia.repl.utils import detect_and_highlight_code

        text = "Here is some text with a code block:

        ```python
        print('Hello World!')
        ```

        And some more text..."

        print(detect_and_highlight_code(text))

    This would detect the Python code block and highlight it before
    returning the text.

    """
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
    """
    Import statement for this module.

    .. code-block:: python

        import shlex

    Split a string into tokens in a shell-like manner. This is a wrapper around
    the shlex.split function that handles unmatched quotes more gracefully.

    Parameters
    ----------
    text : str
        The string to split into tokens.

    Returns
    -------
    list of str
        A list of tokens from splitting the input text.

    Raises
    ------
    ValueError
        If there is still an unmatched quote after attempting to fix
        unclosed quotes.

    Examples
    --------
    >>> text = "This is a 'string' with unmatched quote"
    >>> safe_shlex_split(text)
    ['This', 'is', 'a', "'string'", 'with', 'unmatched', 'quote']

    """
    if not content:
        return
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
    """Splits text into tokens using shlex, fixing unclosed quotes.

    This function splits the input text into tokens using shlex.split(),
    but catches ValueErrors caused by unmatched quotes and attempts to fix
    them by adding the quote character to the end of the string before
    splitting.

    This allows splitting strings with unclosed quotes without raising an
    exception. For example a string like: 'hello world' will be split into
    ['hello world"'] instead of raising an error.

    Parameters
    ----------
    text : str
        The string to split into tokens.

    Returns
    -------
    list of str
        A list of tokens from splitting the input text.

    Raises
    ------
    ValueError
        If there is still an unmatched quote after attempting to fix
        unclosed quotes.

    Examples
    --------
    >>> text = "This is a 'string' with unmatched quote"
    >>> safe_shlex_split(text)
    ['This', 'is', 'a', "'string'", 'with', 'unmatched', 'quote']

    """
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


class StreamWrapper:
    """
    Wrapper class for a stream (e.g., stdout) that supports buffering and flushing.
    """

    def __init__(self, original_stream):
        self.original_stream = original_stream
        self.lock = threading.Lock()
        self.buffer = ""

    def write(self, data):
        with self.lock:
            self.buffer += data
            self.original_stream.write(data)
            self.original_stream.flush()

    def flush(self):
        with self.lock:
            self.original_stream.flush()

    def clear(self):
        with self.lock:
            print("\033[F\033[K" * self.buffer.count("\n"), end="")
            self.buffer = ""
            self.original_stream.flush()
            # print("")


@contextlib.contextmanager
def temporary_stdout():
    """
    Context manager for temporarily redirecting stdout.

    This context manager redirects the standard output (stdout) to a custom
    stream wrapper. It allows capturing and manipulating printed content
    within the context, which can be useful for testing and capturing output.

    Example
    -------
    >>> from madia.repl.utils import temporary_stdout
    >>> with temporary_stdout():
    ...     print("Hello, world!")
    ...     print("This is a test.")
    ...     print("Goodbye!")
    ... # stdout is back to normal here

    """
    original_stdout = sys.stdout
    custom_stream = StreamWrapper(original_stdout)
    sys.stdout = custom_stream
    try:
        yield
    finally:
        sys.stdout = original_stdout
        custom_stream.flush()
        custom_stream.clear()
