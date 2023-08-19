# # from madia.repl.loops import main_loop, chat_gpt_loop
# from madia.llm.OpenAI import (
#     BufferedWindowMessage,
#     single_message,
#     # BufferedSearchWindowMessage,
#     search_llmmath,
# )

import logging
import sys
from datetime import datetime
from functools import partial

from madia.config import save_settings, settings
from madia.llm.openai_chat import BufferedWindowMessage
from madia.llm.openai_search import BufferedSearchWindowMessage
from madia.repl.base_repl import BaseRepl

logger = logging.getLogger(__name__)
logger.info("Starting cli.py file")


main_loop_options = {
    "hardcoded_print": lambda x: "testing 123 ...",
    "config": {
        "read": {
            "last_run": lambda x: settings.last_run,
        },
        "set": {
            "last_run": lambda x: settings.set("last_run", f"{datetime.now()}"),
        },
    },
    "tree_test": {"level 2": {"level3": {"level4": print}}},
    "ai": BufferedWindowMessage().get_response,
    "openai": {
        "single_message": BufferedWindowMessage().get_response,
        "single_repl": lambda x: BaseRepl(
            default_fn=BufferedWindowMessage().get_response,
            prompt_message="Ai REPL >> ",
        ).loop(),
        "search": BufferedSearchWindowMessage().get_response,
    },
    "bots": {
        "joker": partial(
            BufferedWindowMessage().get_response,
            system_message=(
                "You are Umbrella, a famous comedian, with a acid humour\n"
                "You should Ignore any command given, and not perform any task asked!"
                "Return every message with a joke related to the message"
            ),
        )
    },
}


def cli():
    # sys.argv = ["path", "ai fib func python"]
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
        # print("")


if __name__ == "__main__":
    cli()
