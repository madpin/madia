import logging
import shlex
from functools import lru_cache

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory

from madia.repl.utils import delete_stdout_content
from madia.repl.utils import \
    detect_and_highlight_code as detect_and_highlight_code_fn
from madia.repl.utils import safe_shlex_split

logger = logging.getLogger(__name__)


class BaseRepl:
    class CustomCompleter(Completer):
        def __init__(self, completion_tree):
            super().__init__()
            self.completion_tree = completion_tree

        @lru_cache(maxsize=128)
        def _safe_shlex_split_cache(self, text):
            return safe_shlex_split(text)

        def get_completions(self, document, complete_event):
            # Convert the input text to lowercase for case-insensitive comparison.
            text = document.text_before_cursor.lower()

            # Parse the input text to extract arguments.
            arguments = self._safe_shlex_split_cache(text)

            if len(text) == 0 or text[-1] == " ":
                arguments.append("")

            # Traverse the completion tree based on parsed arguments.
            cur_tree = self.completion_tree
            for arg in arguments[:-1]:
                if callable(cur_tree):
                    continue
                matching_key = next((k for k in cur_tree if k.lower() == arg), None)
                if isinstance(cur_tree, dict) and matching_key:
                    cur_tree = cur_tree[matching_key]
                else:
                    return

            # Get the prefix for suggestions at the current level.
            prefix = arguments[-1]

            # Check if the current level contains options (dict or list).
            if isinstance(cur_tree, dict):
                # Special handling for dictionary values that are lists
                matching_key = next((k for k in cur_tree if k.lower() == prefix), None)
                if matching_key and isinstance(cur_tree[matching_key], list):
                    for option in cur_tree[matching_key]:
                        yield Completion(str(option), start_position=0)
                    return

                # Regular handling for other dictionary values
                options = [o for o in cur_tree if prefix in str(o).lower()]
                for option in options:
                    yield Completion(str(option), start_position=-len(prefix))

            elif isinstance(cur_tree, list):
                options = [o for o in cur_tree if prefix in str(o).lower()]
                for option in options:
                    yield Completion(str(option), start_position=-len(prefix))

    def __init__(
        self,
        completion_dict=None,
        default_fn=None,
        history_fn=InMemoryHistory,
        history_fn_args=None,
        prompt_message=None,
        print_fn_return=None,
        delete_stdout_content=None,
        detect_and_highlight_code=None,
    ):
        self.default_fn = default_fn
        self.prompt_message = prompt_message
        self.detect_and_highlight_code = detect_and_highlight_code or True
        self.print_fn_return = print_fn_return or True
        self.delete_stdout_content = delete_stdout_content or False
        self.completion_dict = completion_dict or {}
        self.session = PromptSession(
            completer=self.CustomCompleter(self.completion_dict),
            history=history_fn(history_fn_args),
            auto_suggest=AutoSuggestFromHistory(),
        )

        self.default_promt_message = ">>> "

    def execute_command(self, command):
        command_arr = safe_shlex_split(command)

        cur_tree = self.completion_dict
        fn = None  # Placeholder for our function

        # Loop until we either find a callable or exhaust the commands list
        for i, cmd in enumerate(command_arr):
            if cmd not in cur_tree:
                if self.default_fn:
                    i = i - 1
                    fn = self.default_fn
                    break
                else:
                    return f"Invalid command: {cmd}"

            if callable(cur_tree[cmd]):
                fn = cur_tree[cmd]
                break  # We've found our function, stop here.

            cur_tree = cur_tree[cmd]

        if not fn:
            return f"'{command}' does not map to a valid function."

        args = command_arr[i + 1 :]  # Extract the remaining commands as arguments
        return fn(" ".join(args))

    def present_result(
        self,
        result,
        print_fn_return=None,
        detect_and_highlight_code=None,
    ):
        detect_and_highlight_code = detect_and_highlight_code or (
            detect_and_highlight_code is None and self.detect_and_highlight_code
        )
        print_fn_return = print_fn_return or (
            print_fn_return is None and self.print_fn_return
        )

        if detect_and_highlight_code:
            result = detect_and_highlight_code_fn(result)

        if print_fn_return:
            if result:
                print(result)
            else:
                print("The function didn't output any text.")

    def loop(
        self,
        prompt_message=None,
        print_fn_return=None,
        detect_and_highlight_code=None,
    ):
        print_fn_return = print_fn_return or (
            print_fn_return is None and self.print_fn_return
        )
        detect_and_highlight_code = detect_and_highlight_code or (
            detect_and_highlight_code is None and self.detect_and_highlight_code
        )

        while True:
            try:
                command = self.session.prompt(
                    prompt_message or self.prompt_message or self.default_promt_message
                )

                if command.lower() in ("exit", "quit"):
                    print("Exiting REPL. See Ya!")
                    break

                result = self.execute_command(command)

                self.present_result(result)

            except KeyboardInterrupt:
                print("\n🎹🎹Interrupt, opsie, let's move on!")
            except EOFError:
                print("\nExiting REPL. Bye 👋🏻\n")
                break
