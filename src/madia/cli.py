# from madia.repl.loops import main_loop, chat_gpt_loop
from madia.llm.OpenAI import (
    BufferedWindowMessage,
    single_message,
    # BufferedSearchWindowMessage,
    search_llmmath,
)

from madia.llm.openai_search import BufferedSearchWindowMessage

from madia.repl.base_repl import BaseRepl

import logging

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Starting cli.py file")
# from madia.llm.OpenAI import buffer_window_message


main_loop_options = {
    "print": lambda x: "testing 123",
    "config": {
        "read": [],
        "set": [],
    },
    "ai": single_message,
    "openai": single_message,
    "memory_chat": lambda x: (
        BaseRepl(
            main_loop_options,
            default_fn=BufferedWindowMessage().get_response,
            prompt_message="Ai REPL >> ",
        ).loop()
    ),
    "ai_search": lambda x: (BufferedSearchWindowMessage().get_response),
}


def cli():
    print("MadIA REPL with Autocomplete - Type 'exit' or 'quit' to exit.")
    base_repl = BaseRepl(main_loop_options, default_fn=print)
    base_repl.loop()


if __name__ == "__main__":
    print("You got in the wrong place, but I'll help you")
    cli()
