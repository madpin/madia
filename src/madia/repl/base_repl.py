from __future__ import annotations

import os
import shlex
from functools import lru_cache

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory, InMemoryHistory

from madia.config import settings
from madia.logger import LoggingMixin, get_logger
from madia.repl.utils import delete_stdout_content
from madia.repl.utils import \
    detect_and_highlight_code as detect_and_highlight_code_fn
from madia.repl.utils import safe_shlex_split
from madia.utils_string import string_to_md5

logger = get_logger(__name__)


class BaseRepl(LoggingMixin):
    """
    A base class for creating interactive REPL (Read-Eval-Print Loop) environments.

    This class provides functionality to create an interactive command-line interface
    where users can input commands, have them evaluated, and see the results printed.

    :param completion_dict: A dictionary containing the command completion tree.
    :type completion_dict: dict, optional
    :param default_fn: The default function to execute if the input command doesn't match any known commands.
    :type default_fn: callable, optional
    :param history_fn: The history function for storing user input history.
    :type history_fn: class, optional
    :param history_fn_args: Additional arguments for initializing the history function.
    :type history_fn_args: tuple, optional
    :param prompt_message: The message to display as the prompt.
    :type prompt_message: str, optional
    :param print_fn_return: Whether to print the return value of executed functions.
    :type print_fn_return: bool, optional
    :param delete_stdout_content: Whether to clear the standard output before printing results.
    :type delete_stdout_content: bool, optional
    :param detect_and_highlight_code: Whether to detect and highlight code in the output.
    :type detect_and_highlight_code: bool, optional

    Usage Example:

    .. code-block:: python

        completion_dict = {
            "command1": {"cmd": some_function, "description": "This is command 1."},
            "command2": {"cmd": another_function, "description": "This is command 2."},
        }

        repl = BaseRepl(
            completion_dict=completion_dict,
            default_fn=default_function,
            history_fn=FileHistory,
            history_fn_args=("history.txt",),
            prompt_message=">>> ",
            print_fn_return=True,
            detect_and_highlight_code=True,
        )

        repl.loop()
    """

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

            if len(text.strip()) == 0 or text[-1] == " ":
                arguments.append("")

            # Traverse the completion tree based on parsed arguments.
            cur_tree = self.completion_tree
            for arg in arguments[:-1]:
                if callable(cur_tree):
                    continue
                matching_key = next(
                    (k for k in cur_tree.get("child", cur_tree) if k.lower() == arg),
                    None,
                )
                if isinstance(cur_tree.get("child", cur_tree), dict) and matching_key:
                    cur_tree = cur_tree.get("child", cur_tree)[matching_key]
                else:
                    return

            # Get the prefix for suggestions at the current level.
            prefix = arguments[-1]

            # Check if the current level contains options (dict or list).
            if isinstance(cur_tree.get("child", cur_tree), dict):
                # Special handling for dictionary values that are lists
                matching_key = next(
                    (k for k in cur_tree.get("child", cur_tree) if k.lower() == prefix),
                    None,
                )
                if matching_key and isinstance(
                    cur_tree.get("child", cur_tree)[matching_key], list
                ):
                    for option in cur_tree.get("child", cur_tree)[matching_key]:
                        yield Completion(str(option), start_position=0)
                    return

                # Regular handling for other dictionary values
                options = [
                    o
                    for o in cur_tree.get("child", cur_tree)
                    if prefix in str(o).lower()
                ]
                for option in options:
                    yield Completion(str(option), start_position=-len(prefix))

            elif isinstance(cur_tree.get("child", cur_tree), list):
                options = [
                    o
                    for o in cur_tree.get("child", cur_tree)
                    if prefix in str(o).lower()
                ]
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
        self.prompt_message = prompt_message or ">>> "
        self.detect_and_highlight_code = detect_and_highlight_code or True
        self.print_fn_return = print_fn_return or True
        self.delete_stdout_content = delete_stdout_content or False
        self.completion_dict = completion_dict or {}

        if settings.rep_hist and settings.rep_hist_path:
            history_fn = FileHistory
            history_fn_args = os.path.join(
                os.path.expanduser(settings.rep_hist_path),
                f"{string_to_md5(self.prompt_message, self.default_fn)}.txt",
            )
        else:
            history_fn = InMemoryHistory

        self.session = PromptSession(
            completer=self.CustomCompleter(self.completion_dict),
            history=history_fn(history_fn_args),
            auto_suggest=AutoSuggestFromHistory(),
            # multiline=True,
        )

    def print_help(self, ob, key="", i=1):
        """
        Print help information about a command.

        :param ob: The command object for which to display help information.
        :type ob: dict
        :param key: The key of the command object in the completion dictionary.
        :type key: str
        :param i: The indentation level for formatting the help display.
        :type i: int
        """
        p = "| " * i
        print(f"{p}--- Help [{key}] ---")
        print(f"{p}Name: {ob.get('name', 'No name available.')}")
        print(f"{p}Short Help: {ob.get('short_help', 'No help available.')}")
        print(f"{p}Help: {ob.get('help', 'No help available.')}")
        print(f"{p}Description: {ob.get('description', 'No description available.')}")
        print(f"{p}Childs:")
        for key, child_ob in ob.get("child", {}).items():
            self.print_help(child_ob, key, i + 1)

    def execute_command(self, command):
        """
        Execute the provided command.

        :param command: The input command to execute.
        :type command: str
        :return: The result of the executed command.
        :rtype: str
        """
        command_arr = safe_shlex_split(command)
        if not command_arr:
            return None
        cur_tree = self.completion_dict
        cur_obj = None
        prev_obj, prev_key = None, None
        fn = None  # Placeholder for our function

        # Loop until we either find a callable or exhaust the commands list
        for i, cur_level in enumerate(command_arr):
            if cur_level == "?":
                self.print_help(prev_obj, prev_key)
                return

            if cur_level not in cur_tree:
                break

            cur_obj = cur_tree[cur_level]
            cur_tree = cur_obj.get("child", cur_tree)
            fn = cur_obj if callable(cur_obj) else cur_obj.get("cmd", None)
            prev_obj, prev_key = cur_obj, cur_level

        if fn:
            pass
        elif self.default_fn:
            i = i - 1
            fn = self.default_fn
        else:
            return f"Invalid command: {cur_level}"

        if not fn:
            return f"'{command}' does not map to a valid function."

        args = command_arr[i:]  # Extract the remaining commands as arguments
        return fn(" ".join(args))

    def present_result(
        self,
        result,
        print_fn_return=None,
        detect_and_highlight_code=None,
    ):
        """
        Present the result of a command execution.

        :param result: The result to be presented.
        :type result: str
        :param print_fn_return: Whether to print the return value of executed functions.
        :type print_fn_return: bool, optional
        :param detect_and_highlight_code: Whether to detect and highlight code in the output.
        :type detect_and_highlight_code: bool, optional
        """
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
        print_fn_return=None,
        detect_and_highlight_code=None,
    ):
        """
        Start the interactive REPL loop.

        :param print_fn_return: Whether to print the return value of executed functions.
        :type print_fn_return: bool, optional
        :param detect_and_highlight_code: Whether to detect and highlight code in the output.
        :type detect_and_highlight_code: bool, optional
        """
        print_fn_return = print_fn_return or (
            print_fn_return is None and self.print_fn_return
        )
        detect_and_highlight_code = detect_and_highlight_code or (
            detect_and_highlight_code is None and self.detect_and_highlight_code
        )

        while True:
            try:
                command = self.session.prompt(self.prompt_message)

                if command.lower() in ("exit", "quit"):
                    print("Exiting REPL. See Ya!")
                    break

                result = self.execute_command(command)
                self.logger.debug(f"Command result pre formatter: {result}")
                self.present_result(result)

            except KeyboardInterrupt:
                print("\n🎹🎹Interrupt, opsie, let's move on!")
            except EOFError:
                print("\nExiting REPL. Bye 👋🏻\n")
                break
