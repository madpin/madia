import logging
import os
import string
import sys
from math import ceil

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI

logger = logging.getLogger(__name__)


class MyCustomSyncHandler(BaseCallbackHandler):
    banner_lines = []
    prepend = "Data Arriving: "
    printing_line = ""
    progress_bar = "🔁" + "." * 80
    PRINT_NO_TOKENS = 10

    def _clear_lines_below(self, lines_count: int):
        """Clear a specific number of lines above the current cursor position."""

        sys.stdout.write("\x1b[2K")  # Clear current line
        for _ in range(1, lines_count):
            # sys.stdout.write("\x1b[1A")  # Move Cursor up 1 line
            sys.stdout.write("\x1b[1B")  # Move Cursor down 1 line
            sys.stdout.write("\x1b[2K")  # Clear current line
        sys.stdout.write("\x1b[u")  # Restore cursor position
        sys.stdout.flush()

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        # Appending the new token to the array
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
        sys.stdout.write("\x1b[s")  # Save Cursor position
        lines_count = ceil((len(self.printing_line)) / os.get_terminal_size().columns)

        self._clear_lines_below(lines_count)


def response_strip(text):
    return text.strip(string.whitespace + "".join(chr(i) for i in range(32)))
