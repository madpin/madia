from __future__ import annotations

import logging
import sys
from datetime import datetime
from functools import partial
from pprint import pformat

from madia.config import save_settings, settings
from madia.llm.openai_chat import BufferedWindowMessage
from madia.llm.openai_search import BufferedSearchWindowMessage
from madia.logger import get_buffered_logs, get_logger, show_logs_to_user
from madia.options_dict import main_loop_options
from madia.repl.base_repl import BaseRepl

logger = get_logger(__name__)

logger.info("Starting cli.py file")


def cli():
    """Command line interface for MadIA assistant.

    This is the entrypoint for the MadIA assistant command line. It handles
    parsing command line arguments and starting the REPL or executing a single
    command.

    The REPL will be started if no arguments are provided, allowing the user
    to interactively chat with the assistant.

    If command line arguments are passed, it will execute that command using
    the assistant and print the result.

    Usage:

    .. code-block:: python

       import madia

       madia.cli() # Starts REPL

       madia.cli("hello") # Executes 'hello' command

    """

    if len(sys.argv) == 1:
        print("MadIA REPL with Autocomplete - Type 'exit' or 'quit' to exit.")
        base_repl = BaseRepl(main_loop_options, default_fn=print)
        base_repl.loop()
    else:
        print("This is a shortcut, for any Madia Command that you can run via REPL\n")
        base_repl = BaseRepl(main_loop_options, default_fn=print)
        base_repl.present_result(
            base_repl.execute_command(
                " ".join(
                    sys.argv[1:],
                )
            )
        )


if __name__ == "__main__":
    cli()
