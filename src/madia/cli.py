from madia.repl.loops import main_loop, chat_gpt_loop
from madia.llm.OpenAI import (
    BufferedWindowMessage,
    single_message,
    BufferedSearchWindowMessage,
    search_llmmath,
)

# from madia.llm.OpenAI import buffer_window_message


def chat_gpt_loop_mock(_):
    buffer_window_message_instance = BufferedWindowMessage()
    chat_gpt_loop(buffer_window_message_instance.get_response)


buffer_window_search_message_instance = BufferedSearchWindowMessage()

main_loop_options = {
    "config": {
        "read": [],
        "set": [],
    },
    "ai": single_message,
    "openai": single_message,
    "aichat": chat_gpt_loop_mock,
    "chatai": chat_gpt_loop_mock,
    "ai_search": buffer_window_search_message_instance.get_response,
    "ai_search2": search_llmmath,
}


def cli():
    print("MadIA REPL with Autocomplete - Type 'exit' or 'quit' to exit.")
    main_loop(main_loop_options)


if __name__ == "__main__":
    print("You got in the wrong place, but I'll help you")
    cli()
