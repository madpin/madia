from madia.repl.utils import (
    delete_stdout_content,
    execute_command,
    detect_and_highlight_code,
)
from madia.repl.completer import CustomCompleter
from prompt_toolkit import PromptSession

# from prompt_toolkit.completion import Completer, Completion
# from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


def main_loop(options):
    completer = CustomCompleter(options)
    history = FileHistory("repl_history.txt")
    session = PromptSession(
        message=">>> ",
        history=history,
        # lexer=PygmentsLexer(PythonLexer),
        completer=completer,
        auto_suggest=AutoSuggestFromHistory(),
    )

    while True:
        try:
            user_input = session.prompt()
            if user_input.lower() in ("exit", "quit"):
                print("Exiting REPL. See Ya!")
                break

            try:
                result = execute_command(user_input, options)
                print(detect_and_highlight_code(result))
            except Exception as err:
                print(f"Error: {err}")
        except KeyboardInterrupt:
            print("\n🎹🎹Interrupt, opsie, let's move on!")
        except EOFError:
            print("\nExiting REPL. Bye 👋🏻\n")
            break


def chat_gpt_loop(conversation_function):
    history_ai = FileHistory("repl_history_chat_gpt_loop.txt")
    session = PromptSession(
        message="Chat GPT > ",
        history=history_ai,
        auto_suggest=AutoSuggestFromHistory(),
    )

    while True:
        try:
            user_input = session.prompt()
            if user_input.lower() in ("exit", "quit"):
                print("Exiting REPL. See Ya!")
                break

            try:
                ans = conversation_function(user_input)

                # delete_stdout_content(ans)
                # print(detect_and_highlight_code(ans))
            except Exception as err:
                print(f"Error: {err}")

        except KeyboardInterrupt:
            print("\n🎹🎹Interrupt, opsie, let's move on!")
        except EOFError:
            print("\nExiting REPL. Bye 👋🏻\n")
            break
