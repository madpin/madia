from __future__ import annotations

import os
import string
import sys
from math import ceil

from langchain.callbacks.base import BaseCallbackHandler

from madia.logger import get_logger

logger = get_logger(__name__)


class ShortProgressStringsHandler(BaseCallbackHandler):
    """
    A callback handler for displaying short progress
    strings with a rotating progress bar.

    This handler is used to show the progress of data arriving through tokens in a Chain
    It displays a rotating progress bar along with the accumulating tokens to provide a
    visual representation of the progress.

    Attributes:
        banner_lines (List[str]): List of tokens as part of the progress line.
        prepend (str): The string to be prepended before the progress display.
        printing_line (str):
            The current line being printed, including progress and tokens.
        progress_bar (str):
            The rotating progress bar characters.
        PRINT_NO_TOKENS (int):
            Number of tokens after which the displayed tokens are reset.

    Methods:
        on_llm_new_token(token: str, **kwargs) -> None:
            Called when a new token is processed. Updates and displays the progress.

        on_llm_end(response, **kwargs) -> None:
            Called when the processing of tokens ends. Clears the progress display.
    """

    banner_lines = []
    prepend = "Data Arriving: "
    printing_line = ""
    progress_bar = "🔁" + "." * 20
    PRINT_NO_TOKENS = 10

    def _clear_lines_below(self, lines_count: int):
        """
        Clear a specific number of lines below the current cursor position.

        Args:
            lines_count (int): The number of lines to be cleared.
        """

        sys.stdout.write("\x1b[2K")  # Clear current line
        for _ in range(1, lines_count):
            # sys.stdout.write("\x1b[1A")  # Move Cursor up 1 line
            sys.stdout.write("\x1b[1B")  # Move Cursor down 1 line
            sys.stdout.write("\x1b[2K")  # Clear current line
        sys.stdout.write("\x1b[u")  # Restore cursor position
        sys.stdout.flush()

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        Update and display the progress upon processing a new token.

        Args:
            token (str): The newly processed token.
            **kwargs: Additional keyword arguments.
        """
        self.banner_lines.append(token.replace("\n", ""))

        lines_count = ceil((len(self.printing_line)) / os.get_terminal_size().columns)

        sys.stdout.write("\x1b[s")  # Save Cursor position
        self._clear_lines_below(lines_count)

        # Printing
        self.printing_line = (
            f"{self.prepend} [{self.progress_bar}] {' '.join(self.banner_lines)}"
        )
        sys.stdout.write(self.printing_line)
        sys.stdout.write("\x1b[u")  # Restore cursor position
        sys.stdout.flush()

        # Processing Progress Bar
        self.progress_bar = self.progress_bar[-1] + self.progress_bar[:-1]

        if len(self.banner_lines) > self.PRINT_NO_TOKENS:
            self.banner_lines = []

    def on_llm_end(self, response, **kwargs) -> None:
        """
        Clear the progress display when the processing of tokens ends.

        Args:
            response: The response after processing tokens.
            **kwargs: Additional keyword arguments.
        """
        sys.stdout.write("\x1b[s")  # Save Cursor position
        lines_count = ceil((len(self.printing_line)) / os.get_terminal_size().columns)

        self._clear_lines_below(lines_count)


class FileLoggerHandler(BaseCallbackHandler):
    """
    A callback handler for logging data to a file.

    This handler is used to log data from the Language Chain to a file using the logger.

    Methods:
        on_llm_end(response, **kwargs) -> None:
            Called when the processing of tokens ends. Logs the response.

        on_chain_end(outputs, **kwargs) -> None:
            Called when the entire chain processing ends. Logs the outputs.
    """

    def on_llm_end(self, response, **kwargs) -> None:
        """
        Log the response when the processing of tokens ends.

        Args:
            response: The response after processing tokens.
            **kwargs: Additional keyword arguments.
        """
        logger.debug(response)

    def on_chain_end(self, outputs, **kwargs) -> None:
        """
        Log the outputs when the entire chain processing ends.

        Args:
            outputs: The outputs after processing the entire chain.
            **kwargs: Additional keyword arguments.
        """
        logger.debug(outputs)


def response_strip(text):
    """
    Strip leading and trailing whitespace and control characters from a string.

    This function removes all leading and trailing whitespace characters
    as well as control characters with ASCII values in the range [0, 31].

    Args:
        text (str): The input text to be stripped.

    Returns:
        str: The input text with leading and trailing whitespace
            and control characters removed.
    """
    return text.strip(string.whitespace + "".join(chr(i) for i in range(32)))
